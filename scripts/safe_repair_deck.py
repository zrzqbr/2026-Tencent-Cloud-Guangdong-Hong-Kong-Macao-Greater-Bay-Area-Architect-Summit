#!/usr/bin/env python3
"""Apply package-preserving font, color, chart, and import-compatibility repairs."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from brand_core import A, C, NS, P, canvas_from_presentation, load_manifest, shape_box, slide_paths, text_value


for prefix, uri in (("a", A), ("c", C), ("p", P)):
    ET.register_namespace(prefix, uri)


def qn(namespace: str, tag: str) -> str:
    return f"{{{namespace}}}{tag}"


def solid_rgb(props: ET.Element | None) -> str | None:
    if props is None:
        return None
    node = props.find("./a:solidFill/a:srgbClr", NS)
    return node.get("val", "").upper() if node is not None else None


def set_color(props: ET.Element, color: str) -> bool:
    fill = props.find("./a:solidFill", NS)
    before = solid_rgb(props)
    if fill is None:
        fill = ET.SubElement(props, qn(A, "solidFill"))
    for child in list(fill):
        fill.remove(child)
    node = ET.SubElement(fill, qn(A, "srgbClr"))
    node.set("val", color)
    return before != color


def set_fonts(props: ET.Element, font: str) -> bool:
    changed = False
    for tag in ("latin", "ea", "cs"):
        node = props.find(f"./a:{tag}", NS)
        if node is None:
            node = ET.SubElement(props, qn(A, tag))
        if node.get("typeface") != font:
            node.set("typeface", font)
            changed = True
    return changed


def get_or_create_rpr(run: ET.Element) -> ET.Element:
    props = run.find("./a:rPr", NS)
    if props is None:
        props = ET.Element(qn(A, "rPr"))
        run.insert(0, props)
    return props


def shape_role(shape: ET.Element, canvas: tuple[int, int]) -> str:
    text = text_value(shape).strip()
    sizes = []
    for node in shape.findall(".//a:rPr", NS) + shape.findall(".//a:defRPr", NS):
        if node.get("sz", "").isdigit():
            sizes.append(int(node.get("sz")))
    max_size = max(sizes, default=0)
    box = shape_box(shape)
    top_band = bool(box and canvas[1] and box[1] < canvas[1] * 0.28)
    if max_size >= 4000:
        return "title"
    if max_size >= 3000 and (len(text) <= 80 or top_band):
        return "title"
    if top_band and max_size >= 2400 and len(text) <= 60:
        return "title"
    return "body"


def fixed_field_role(slide_number: int, shape: ET.Element, manifest: dict, canvas: tuple[int, int]) -> tuple[str, dict | None]:
    key = "boxOriginalEmu" if list(canvas) == manifest["canvas"]["originalEmu"] else "boxStandardEmu"
    box = shape_box(shape)
    if slide_number == 2:
        for field in manifest["fixedPages"]["title"]["fields"]:
            expected = field[key]
            if box and all(abs(a - b) <= 16000 for a, b in zip(box, expected)):
                return ("title" if field["id"] != "speaker" else "body"), field
    if slide_number == 3:
        for field in manifest["fixedPages"]["speaker"]["fields"]:
            if "font" not in field:
                continue
            expected = field[key]
            if box and all(abs(a - b) <= 16000 for a, b in zip(box, expected)):
                return ("title" if field["font"] == manifest["fonts"]["title"] else "body"), field
    return shape_role(shape, canvas), None


def shape_object_id(shape: ET.Element) -> str | None:
    node = shape.find("./p:nvSpPr/p:cNvPr", NS)
    return node.get("id") if node is not None else None


def normalized_contrast_rules(value: dict | None, manifest: dict) -> dict:
    rules = value or {}
    allowed = set(manifest["palette"]["allowedText"])
    shape_colors = {str(key): str(color).replace("#", "").upper() for key, color in rules.get("shapeColors", {}).items()}
    table_colors = {str(key): str(color).replace("#", "").upper() for key, color in rules.get("tableTextColors", {}).items()}
    table_cell_colors = {
        str(table): {str(cell): str(color).replace("#", "").upper() for cell, color in cells.items()}
        for table, cells in rules.get("tableCellTextColors", {}).items()
    }
    table_default = rules.get("tableTextColor")
    table_default = str(table_default).replace("#", "").upper() if table_default else None
    requested = set(shape_colors.values()) | set(table_colors.values()) | ({table_default} if table_default else set())
    requested.update(color for cells in table_cell_colors.values() for color in cells.values())
    invalid = requested - allowed
    if invalid:
        raise ValueError(f"Contrast map uses colors outside palette.allowedText: {sorted(invalid)}")
    return {
        "shapeColors": shape_colors,
        "tableTextColors": table_colors,
        "tableCellTextColors": table_cell_colors,
        "tableTextColor": table_default,
    }


def repair_slide_xml(
    data: bytes,
    slide_number: int,
    manifest: dict,
    canvas: tuple[int, int],
    contrast_rules: dict | None = None,
) -> tuple[bytes, dict]:
    root = ET.fromstring(data)
    report = {"slide": slide_number, "fontChanges": 0, "colorChanges": 0, "runsVisited": 0, "tableRunsVisited": 0}
    title_font, body_font = manifest["fonts"]["title"], manifest["fonts"]["body"]
    rules = normalized_contrast_rules(contrast_rules, manifest)

    for shape in root.findall(".//p:sp", NS):
        role, fixed_field = fixed_field_role(slide_number, shape, manifest, canvas)
        target_font = fixed_field["font"] if fixed_field else (title_font if role == "title" else body_font)
        object_color = rules["shapeColors"].get(shape_object_id(shape) or "")
        target_color = fixed_field["color"] if fixed_field else object_color
        for run in shape.findall(".//a:r", NS) + shape.findall(".//a:fld", NS):
            if not text_value(run).strip():
                continue
            report["runsVisited"] += 1
            props = get_or_create_rpr(run)
            if set_fonts(props, target_font):
                report["fontChanges"] += 1
            if target_color is not None and set_color(props, target_color):
                report["colorChanges"] += 1
        for props in shape.findall(".//a:defRPr", NS) + shape.findall(".//a:endParaRPr", NS):
            if set_fonts(props, target_font):
                report["fontChanges"] += 1
            if target_color is not None and set_color(props, target_color):
                report["colorChanges"] += 1

    for table_index, table in enumerate(root.findall(".//a:tbl", NS), 1):
        table_key = str(table_index)
        table_color = rules["tableTextColors"].get(table_key) or rules["tableTextColor"]
        cell_colors = rules["tableCellTextColors"].get(table_key, {})
        for row_index, row in enumerate(table.findall("./a:tr", NS), 1):
            for column_index, cell in enumerate(row.findall("./a:tc", NS), 1):
                target_color = cell_colors.get(f"{row_index},{column_index}") or table_color
                for run in cell.findall(".//a:r", NS) + cell.findall(".//a:fld", NS):
                    if not text_value(run).strip():
                        continue
                    report["runsVisited"] += 1
                    report["tableRunsVisited"] += 1
                    props = get_or_create_rpr(run)
                    if set_fonts(props, body_font):
                        report["fontChanges"] += 1
                    if target_color is not None and set_color(props, target_color):
                        report["colorChanges"] += 1
                for props in cell.findall(".//a:defRPr", NS) + cell.findall(".//a:endParaRPr", NS):
                    if set_fonts(props, body_font):
                        report["fontChanges"] += 1
                    if target_color is not None and set_color(props, target_color):
                        report["colorChanges"] += 1
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), report


def repair_chart_xml(data: bytes, manifest: dict, repair_axis_ids: bool, normalize_colors: bool) -> tuple[bytes, dict]:
    root = ET.fromstring(data)
    report = {"fontChanges": 0, "colorChanges": 0, "axisIdsRepaired": 0}
    body_font = manifest["fonts"]["body"]
    body_color = manifest["palette"]["body"]
    series = manifest["palette"]["chartSeries"]
    for props in root.findall(".//a:defRPr", NS) + root.findall(".//a:rPr", NS):
        if set_fonts(props, body_font):
            report["fontChanges"] += 1
        current = solid_rgb(props)
        if normalize_colors and current is not None and current not in manifest["palette"]["allowedText"] and set_color(props, body_color):
            report["colorChanges"] += 1
    if normalize_colors:
        for index, series_node in enumerate(root.findall(".//c:ser", NS)):
            color = series[index % len(series)]
            props = series_node.find("./c:spPr", NS)
            if props is None:
                props = ET.SubElement(series_node, qn(C, "spPr"))
            fill = props.find("./a:solidFill", NS)
            if fill is None:
                fill = ET.SubElement(props, qn(A, "solidFill"))
            current = fill.find("./a:srgbClr", NS)
            before = current.get("val", "").upper() if current is not None else None
            if before != color:
                for child in list(fill):
                    fill.remove(child)
                ET.SubElement(fill, qn(A, "srgbClr"), {"val": color})
                report["colorChanges"] += 1
    if repair_axis_ids:
        for node in root.findall(".//c:axId", NS) + root.findall(".//c:crossAx", NS):
            value = node.get("val", "")
            if re.fullmatch(r"-\d+", value):
                node.set("val", str(int(value) + 2**32))
                report["axisIdsRepaired"] += 1
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), report


def repair_deck(
    source: Path,
    destination: Path | None,
    *,
    strict_colors: bool,
    repair_axis_ids: bool,
    contrast_map: dict | None = None,
) -> dict:
    if strict_colors != bool(contrast_map):
        raise ValueError("strict color mode and a reviewed contrast map must be enabled together")
    manifest = load_manifest()
    report = {
        "input": str(source),
        "output": str(destination) if destination else None,
        "dryRun": destination is None,
        "strictColorMode": strict_colors,
        "contrastMapApplied": bool(contrast_map),
        "slides": [],
        "charts": [],
        "totals": {"fontChanges": 0, "colorChanges": 0, "axisIdsRepaired": 0},
        "structuralActionsStillRequired": [
            "Insert or preserve the immutable canonical cover, title, and speaker/avatar pages as output slides 1-3.",
            "Replace legacy backgrounds with approved summit backgrounds through the companion presentation tool.",
            "Resolve text against the actual rendered light/dark surface; never add a readability-only text backing shape.",
            "Append the canonical single-image thank-you page.",
            "Render every slide and repair text overlap or clipping.",
        ],
    }
    with zipfile.ZipFile(source) as archive:
        presentation, paths = slide_paths(archive)
        canvas = canvas_from_presentation(presentation)
        replacements: dict[str, bytes] = {}
        for index, path in enumerate(paths, 1):
            slide_rules = (contrast_map or {}).get("slides", {}).get(str(index), {})
            repaired, item = repair_slide_xml(archive.read(path), index, manifest, canvas, slide_rules)
            replacements[path] = repaired
            report["slides"].append(item)
            report["totals"]["fontChanges"] += item["fontChanges"]
            report["totals"]["colorChanges"] += item["colorChanges"]
        for name in archive.namelist():
            if not re.fullmatch(r"ppt/charts/chart\d+\.xml", name):
                continue
            normalize_chart_colors = bool((contrast_map or {}).get("normalizeChartColors", False))
            repaired, item = repair_chart_xml(archive.read(name), manifest, repair_axis_ids, normalize_chart_colors)
            replacements[name] = repaired
            item["part"] = name
            report["charts"].append(item)
            for key in ("fontChanges", "colorChanges", "axisIdsRepaired"):
                report["totals"][key] += item[key]
        if destination:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(destination, "w") as output:
                for info in archive.infolist():
                    output.writestr(info, replacements.get(info.filename, archive.read(info.filename)))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="Write a repaired copy. Omit for dry-run.")
    parser.add_argument("--report", type=Path, help="Optional JSON report path")
    parser.add_argument("--strict-colors", action="store_true", help="Enable only reviewed contrast-map color changes; no body/title color is inferred")
    parser.add_argument(
        "--contrast-map",
        type=Path,
        help='Reviewed JSON with shapeColors, tableTextColor(s), and optional tableCellTextColors keyed by "row,column"',
    )
    parser.add_argument("--repair-import-compatibility", action="store_true", help="Convert signed chart axis IDs to valid unsigned IDs")
    args = parser.parse_args()
    source = args.input.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".pptx":
        parser.error("--input must be an existing .pptx file")
    destination = args.output.expanduser().resolve() if args.output else None
    if destination == source:
        parser.error("Refusing to overwrite the source deck")
    if args.strict_colors and not args.contrast_map:
        parser.error("--strict-colors requires --contrast-map; body text cannot be normalized without verified surfaces")
    if args.contrast_map and not args.strict_colors:
        parser.error("--contrast-map requires --strict-colors so color-changing mode is always explicit")
    contrast_map = None
    if args.contrast_map:
        contrast_path = args.contrast_map.expanduser().resolve()
        if not contrast_path.is_file():
            parser.error("--contrast-map must be an existing JSON file")
        try:
            contrast_map = json.loads(contrast_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            parser.error(f"--contrast-map is not valid JSON: {exc}")
        if not isinstance(contrast_map.get("slides", {}), dict):
            parser.error("--contrast-map slides must be an object keyed by 1-based slide number")
    report = repair_deck(
        source,
        destination,
        strict_colors=args.strict_colors,
        repair_axis_ids=args.repair_import_compatibility,
        contrast_map=contrast_map,
    )
    if args.report:
        args.report.expanduser().resolve().write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
