#!/usr/bin/env python3
"""Validate summit fixed pages, backgrounds, branding, and text-layout safety."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

from brand_core import (
    EMU_PER_INCH,
    box_matches,
    boxes_intersect,
    canvas_from_presentation,
    drawable_elements,
    inches_box_to_emu,
    load_manifest,
    negative_chart_axis_ids,
    package_path,
    part_rels_name,
    rel_map,
    sha256,
    shape_box,
    slide_and_layout_images,
    slide_layout_path,
    slide_paths,
    text_runs,
    text_shapes,
    text_value,
    xml,
)


ROOT = Path(__file__).resolve().parents[1]


def asset_errors(manifest: dict) -> list[str]:
    errors = []
    template_path = ROOT / manifest["template"]["file"]
    if not template_path.exists() or sha256(template_path) != manifest["template"]["sha256"]:
        errors.append("Canonical template is missing or differs from brand-manifest.json")
    for item in manifest["backgrounds"]:
        path = ROOT / item["file"]
        if not path.exists() or sha256(path) != item["sha256"]:
            errors.append(f"Approved background is missing or modified: {item['file']}")
    for key, item in manifest["fixedPages"].items():
        relative = item.get("file") or item.get("backgroundFile")
        path = ROOT / relative
        if not path.exists() or sha256(path) != item["sha256"]:
            errors.append(f"Fixed-page asset is missing or modified: {key} ({relative})")
    return errors


def approved_background(
    archive: zipfile.ZipFile,
    path: str,
    root,
    canvas: tuple[int, int],
    manifest: dict,
) -> tuple[dict | None, dict | None]:
    specs = {item["sha256"]: item for item in manifest["backgrounds"]}
    for candidate in slide_and_layout_images(archive, path, root):
        digest = sha256(candidate["data"])
        spec = specs.get(digest)
        if not spec:
            continue
        if candidate["kind"].endswith("background-fill"):
            return spec, candidate
        if box_matches(candidate.get("box"), (0, 0, *canvas), 2000) and not candidate.get("cropped"):
            return spec, candidate
    return None, None


def style_summary(shape) -> dict:
    runs = [run for run in text_runs(shape) if run["text"].strip()]
    sizes = {run["size"] for run in runs}
    colors = {run["color"] for run in runs}
    fonts = {tuple(sorted(run["fonts"].items())) for run in runs}
    return {"runs": runs, "sizes": sizes, "colors": colors, "fonts": fonts}


def expected_box(field: dict, canvas: tuple[int, int], manifest: dict) -> tuple[int, int, int, int]:
    if list(canvas) == manifest["canvas"]["originalEmu"]:
        return tuple(field["boxOriginalEmu"])
    if list(canvas) == manifest["canvas"]["standardEmu"]:
        return tuple(field["boxStandardEmu"])
    scale = canvas[0] / manifest["canvas"]["standardEmu"][0]
    return tuple(round(value * scale) for value in field["boxStandardEmu"])


def validate_field(errors: list[str], slide_number: int, shape, field: dict, canvas: tuple[int, int], manifest: dict) -> None:
    actual_box = shape_box(shape)
    target_box = expected_box(field, canvas, manifest)
    if not box_matches(actual_box, target_box, tolerance=18000):
        errors.append(f"Slide {slide_number} field {field['id']} box must be {target_box}; found {actual_box}")
    summary = style_summary(shape)
    if summary["sizes"] != {field["sizeHundredthPt"]}:
        errors.append(f"Slide {slide_number} field {field['id']} size must be {field['sizeHundredthPt'] / 100:g} pt; found {sorted(summary['sizes'])}")
    if summary["colors"] != {field["color"]}:
        errors.append(f"Slide {slide_number} field {field['id']} color must be #{field['color']}; found {sorted(str(value) for value in summary['colors'])}")
    for run in summary["runs"]:
        fonts = set(run["fonts"].values())
        if fonts != {field["font"]}:
            errors.append(f"Slide {slide_number} field {field['id']} must set latin/ea/cs to {field['font']}; found {run['fonts']}")
    if "fixedText" in field and text_value(shape).strip() != field["fixedText"]:
        errors.append(f"Slide {slide_number} field {field['id']} text must remain {field['fixedText']!r}")
    if field.get("alignment"):
        expected_alignment = {"center": "ctr"}.get(field["alignment"], field["alignment"])
        alignments = {node.get("algn") for node in shape.findall(".//a:pPr", {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"})}
        if alignments != {expected_alignment}:
            errors.append(
                f"Slide {slide_number} field {field['id']} alignment must remain {field['alignment']}; "
                f"found {sorted(str(value) for value in alignments)}"
            )


def content_objects(root) -> list:
    return drawable_elements(root)


def check_text_safety(errors: list[str], slide_number: int, root, canvas: tuple[int, int], manifest: dict) -> None:
    clearance = round(manifest["release"]["textCollisionClearanceInches"] * EMU_PER_INCH * canvas[0] / manifest["canvas"]["standardEmu"][0])
    entries = text_shapes(root)
    for index, (first_text, first_box) in enumerate(entries):
        x, y, width, height = first_box
        if x < 0 or y < 0 or x + width > canvas[0] or y + height > canvas[1]:
            errors.append(f"Slide {slide_number} text box {first_text[:30]!r} extends outside the canvas")
        for second_text, second_box in entries[index + 1:]:
            if boxes_intersect(first_box, second_box, clearance):
                errors.append(f"Slide {slide_number} text boxes {first_text[:24]!r} and {second_text[:24]!r} substantially intersect")


def check_logo_zones(
    errors: list[str],
    slide_number: int,
    root,
    background: dict,
    canvas: tuple[int, int],
    manifest: dict,
    background_candidate: dict | None,
) -> None:
    if slide_number <= 3:
        return
    scale = canvas[0] / manifest["canvas"]["standardEmu"][0]
    zones = [inches_box_to_emu(zone, scale) for zone in background.get("logoZonesStandardInches", [])]
    approved_local_picture = bool(background_candidate and background_candidate.get("kind") == "picture")
    for position, node in enumerate(content_objects(root)):
        box = shape_box(node)
        kind = node.tag.rsplit("}", 1)[-1]
        is_approved_background_picture = approved_local_picture and position == 0 and kind == "pic" and box_matches(box, (0, 0, *canvas), 2000)
        if box is None or is_approved_background_picture:
            continue
        if any(boxes_intersect(box, zone) for zone in zones):
            value = text_value(node).strip()
            name_node = node.find(".//p:cNvPr", {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"})
            name = name_node.get("name", "") if name_node is not None else ""
            label = value[:30] or name or kind
            errors.append(f"Slide {slide_number} foreground {kind} {label!r} enters an approved Logo exclusion zone")


def relative_luminance(color: str) -> float:
    channels = [int(color[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def node_has_dark_fill(node) -> bool:
    namespaces = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main", "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    props = node.find("./p:spPr", namespaces)
    if props is None:
        return False
    rgb_nodes = props.findall(".//a:srgbClr", namespaces)
    rgb_values = [item.get("val", "").upper() for item in rgb_nodes if len(item.get("val", "")) == 6]
    if rgb_values and sum(relative_luminance(value) for value in rgb_values) / len(rgb_values) <= 0.35:
        return True
    scheme_values = {item.get("val", "") for item in props.findall(".//a:schemeClr", namespaces)}
    return bool(scheme_values & {"dk1", "dk2", "tx1", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6"})


def group_has_large_dark_child(group, threshold: float) -> bool:
    namespaces = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main", "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    child_extent = group.find("./p:grpSpPr/a:xfrm/a:chExt", namespaces)
    try:
        group_area = int(child_extent.get("cx")) * int(child_extent.get("cy")) if child_extent is not None else 0
    except (TypeError, ValueError):
        group_area = 0
    if not group_area:
        return False
    for child in group.findall(".//p:sp", namespaces):
        box = shape_box(child)
        if box and node_has_dark_fill(child) and box[2] * box[3] / group_area >= threshold:
            return True
    return False


def check_large_foreground_panels(
    errors: list[str],
    slide_number: int,
    root,
    canvas: tuple[int, int],
    manifest: dict,
    background_candidate: dict | None = None,
) -> None:
    drawables = content_objects(root)
    canvas_area = canvas[0] * canvas[1]
    approved_local_picture = bool(background_candidate and background_candidate.get("kind") == "picture")
    threshold = manifest["release"]["maximumLargeDarkForegroundPanelAreaRatio"]
    for position, node in enumerate(drawables):
        box = shape_box(node)
        if box is None:
            continue
        kind = node.tag.rsplit("}", 1)[-1]
        area_ratio = box[2] * box[3] / canvas_area if canvas_area else 0
        is_bottom_background_picture = approved_local_picture and position == 0 and kind == "pic" and box_matches(box, (0, 0, *canvas), 2000)
        if is_bottom_background_picture:
            continue
        if kind == "pic" and area_ratio >= 0.9:
            errors.append(f"Slide {slide_number} contains a non-background picture covering {area_ratio:.0%} of the canvas")
        elif kind == "sp" and node_has_dark_fill(node) and area_ratio >= threshold:
            errors.append(f"Slide {slide_number} contains a large dark foreground shape covering {area_ratio:.0%} of the canvas")
        elif kind == "grpSp" and area_ratio >= threshold and group_has_large_dark_child(node, threshold):
            errors.append(f"Slide {slide_number} contains a large grouped dark foreground field covering {area_ratio:.0%} of the canvas")


def check_inherited_foreground(
    errors: list[str],
    slide_number: int,
    archive: zipfile.ZipFile,
    slide_path: str,
    canvas: tuple[int, int],
    background_candidate: dict | None,
) -> None:
    layout_path = slide_layout_path(archive, slide_path)
    if not layout_path:
        return
    inherited_parts = [("layout", layout_path)]
    for rel_type, target in rel_map(archive, part_rels_name(layout_path)).values():
        if rel_type.endswith("/slideMaster"):
            inherited_parts.append(("master", package_path(str(Path(layout_path).parent).replace("\\", "/"), target)))
    namespaces = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
    for level, part_path in inherited_parts:
        for position, node in enumerate(content_objects(xml(archive, part_path))):
            if node.find(".//p:ph", namespaces) is not None:
                continue
            box = shape_box(node)
            kind = node.tag.rsplit("}", 1)[-1]
            approved_layout_picture = bool(
                level == "layout"
                and background_candidate
                and background_candidate.get("kind") == "layout-picture"
                and position == 0
                and kind == "pic"
                and box_matches(box, (0, 0, *canvas), 2000)
            )
            if not approved_layout_picture:
                errors.append(f"Slide {slide_number} inherits non-placeholder foreground {kind} from {level} part {part_path}")


def migration_review_errors(ledger_path: Path | None) -> list[str]:
    if ledger_path is None:
        return []
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Cannot read element-migration ledger: {exc}"]
    if int(ledger.get("schemaVersion", 1)) < 3:
        return []
    errors = []
    for index, entry in enumerate(ledger.get("slides", []), 1):
        review = entry.get("visualReview") or {}
        if review.get("renderedAtFullSize") is not True:
            errors.append(f"Ledger entry {index} full-size rendered review is unresolved")
        if review.get("surfaceContrastReviewed") is not True:
            errors.append(f"Ledger entry {index} surface-contrast review is unresolved")
        if review.get("textBackingShapesAdded") != 0:
            errors.append(f"Ledger entry {index} must add zero readability-only text backing shapes")
        if review.get("status") != "passed":
            errors.append(f"Ledger entry {index} visual review status must be 'passed'")
    return errors


def validate(deck: Path, element_migration_ledger: Path | None = None) -> list[str]:
    element_migration = element_migration_ledger is not None
    manifest = load_manifest()
    errors = asset_errors(manifest) + migration_review_errors(element_migration_ledger)
    allowed_canvases = {tuple(manifest["canvas"]["standardEmu"]), tuple(manifest["canvas"]["originalEmu"])}
    final_hash = manifest["fixedPages"]["thanks"]["sha256"]

    try:
        archive = zipfile.ZipFile(deck)
    except (FileNotFoundError, zipfile.BadZipFile):
        return errors + ["Deck is missing or is not a valid PPTX package"]

    with archive:
        presentation, paths = slide_paths(archive)
        canvas = canvas_from_presentation(presentation)
        if canvas not in allowed_canvases:
            errors.append("Deck must use the standard or original 16:9 summit canvas")
        if len(paths) < manifest["release"]["minimumDeckSlides"]:
            return errors + ["Deck must contain the fixed first three slides and fixed final thank-you slide"]
        roots = [xml(archive, path) for path in paths]
        background_matches = []
        for index, (path, root) in enumerate(zip(paths, roots), 1):
            if index == len(paths):
                canonical_final = next(
                    (
                        item
                        for item in slide_and_layout_images(archive, path, root)
                        if item["kind"] == "picture"
                        and sha256(item["data"]) == final_hash
                        and item.get("box") == (0, 0, *canvas)
                        and not item.get("cropped")
                    ),
                    None,
                )
                if canonical_final:
                    background_matches.append(({"id": "canonical-final"}, canonical_final))
                    continue
            spec, candidate = approved_background(archive, path, root, canvas, manifest)
            background_matches.append((spec, candidate))
            if not spec:
                errors.append(f"Slide {index} does not use an approved summit background")
                continue
            if candidate and candidate["kind"] == "picture":
                drawables = content_objects(root)
                if not drawables or drawables[0].tag.rsplit("}", 1)[-1] != "pic":
                    errors.append(f"Slide {index} local background picture must be bottom-most")
            if 4 <= index < len(paths):
                check_large_foreground_panels(errors, index, root, canvas, manifest, candidate)
                check_inherited_foreground(errors, index, archive, path, canvas, candidate)
            check_logo_zones(errors, index, root, spec, canvas, manifest, candidate)

        cover_spec, cover_candidate = background_matches[0]
        if not cover_spec or cover_spec["id"] != "cover":
            errors.append("Slide 1 must use the canonical main KV")
        cover_drawables = content_objects(roots[0])
        if cover_drawables and not (
            len(cover_drawables) == 1
            and cover_candidate
            and cover_candidate["kind"] == "picture"
            and sha256(cover_candidate["data"]) == manifest["fixedPages"]["cover"]["sha256"]
        ):
            errors.append("Slide 1 must not contain content or overlays beyond its canonical KV")

        title_spec, _ = background_matches[1]
        if not title_spec or title_spec["id"] != "title":
            errors.append("Slide 2 must use the canonical title-page background from template source slide 3")
        slide2_shapes = [shape for shape in roots[1].findall(".//p:sp", {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}) if text_value(shape).strip()]
        slide2_non_background = [
            node
            for node in content_objects(roots[1])
            if node.tag.rsplit("}", 1)[-1] != "pic"
            or not box_matches(shape_box(node), (0, 0, *canvas), 2000)
        ]
        fields = manifest["fixedPages"]["title"]["fields"]
        if len(slide2_non_background) != len(fields) or any(node.tag.rsplit("}", 1)[-1] != "sp" for node in slide2_non_background):
            errors.append("Slide 2 structure is fixed: it may contain only the three canonical title text roles")
        if len(slide2_shapes) != len(fields):
            errors.append(f"Slide 2 must contain exactly {len(fields)} populated text fields; found {len(slide2_shapes)}")
        unmatched = list(slide2_shapes)
        for field in fields:
            target = expected_box(field, canvas, manifest)
            shape = next((item for item in unmatched if box_matches(shape_box(item), target, 18000)), None)
            if shape is None:
                errors.append(f"Slide 2 is missing field {field['id']} at {target}")
                continue
            unmatched.remove(shape)
            validate_field(errors, 2, shape, field, canvas, manifest)

        speaker_spec, _ = background_matches[2]
        if not speaker_spec or speaker_spec["id"] != "content-wave-right-logo":
            errors.append("Slide 3 must use the canonical optional speaker-page background from template source slide 4")
        slide3_text = [shape for shape in roots[2].findall(".//p:sp", {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}) if text_value(shape).strip()]
        slide3_non_background = [
            node
            for node in content_objects(roots[2])
            if node.tag.rsplit("}", 1)[-1] != "pic"
            or not box_matches(shape_box(node), (0, 0, *canvas), 2000)
        ]
        if slide3_non_background:
            speaker_fields = [field for field in manifest["fixedPages"]["speaker"]["fields"] if "font" in field]
            if len(slide3_non_background) != len(speaker_fields) + 1:
                errors.append(
                    f"Slide 3 populated speaker page must contain only three text roles and one photo group; "
                    f"found {len(slide3_non_background)} local objects"
                )
            if len(slide3_text) != len(speaker_fields):
                errors.append(f"Slide 3 populated speaker page must contain exactly {len(speaker_fields)} text fields; found {len(slide3_text)}")
            for field in speaker_fields:
                target = expected_box(field, canvas, manifest)
                shape = next((item for item in slide3_text if box_matches(shape_box(item), target, 18000)), None)
                if shape is None:
                    errors.append(f"Slide 3 is missing speaker field {field['id']} at {target}")
                else:
                    validate_field(errors, 3, shape, field, canvas, manifest)
            photo_field = next(field for field in manifest["fixedPages"]["speaker"]["fields"] if field["id"] == "speaker-photo")
            photo_box = expected_box(photo_field, canvas, manifest)
            photo = next((node for node in slide3_non_background if box_matches(shape_box(node), photo_box, 24000)), None)
            if photo is None:
                errors.append(f"Slide 3 populated speaker page is missing the circular photo role at {photo_box}")
            elif photo.tag.rsplit("}", 1)[-1] != "grpSp":
                errors.append("Slide 3 speaker photo must preserve the canonical template photo group and crop structure")
        elif slide3_text:
            errors.append("Slide 3 must be fully blank when no verified speaker profile is supplied")

        final_root = roots[-1]
        final_images = slide_and_layout_images(archive, paths[-1], final_root)
        local_final = [item for item in final_images if item["kind"] == "picture"]
        if len(content_objects(final_root)) != 1 or len(local_final) != 1:
            errors.append("Final slide must contain only the canonical single-image thank-you page")
        elif sha256(local_final[0]["data"]) != final_hash or local_final[0].get("box") != (0, 0, *canvas) or local_final[0].get("cropped"):
            errors.append("Final slide does not match the canonical rendered thank-you asset")

        for index, (path, root) in enumerate(zip(paths[:-1], roots[:-1]), 1):
            images = slide_and_layout_images(archive, path, root)
            if any(sha256(item["data"]) == final_hash for item in images):
                errors.append(f"Slide {index} uses the fixed thank-you asset before the final slide")

        allowed_fonts = {manifest["fonts"]["title"], manifest["fonts"]["body"]}
        allowed_colors = set(manifest["palette"]["allowedText"])
        for slide_index, root in enumerate(roots, 1):
            for run in text_runs(root):
                if not run["text"].strip():
                    continue
                fonts = set(run["fonts"].values())
                if None in fonts or len(fonts) != 1 or not fonts <= allowed_fonts:
                    errors.append(f"Slide {slide_index} text {run['text'][:24]!r} must set latin/ea/cs to one exact Tencent font; found {run['fonts']}")
                migration_body = element_migration and 4 <= slide_index < len(roots)
                if not migration_body and run["color"] not in allowed_colors:
                    found = f"#{run['color']}" if run["color"] else "no direct sRGB color"
                    errors.append(f"Slide {slide_index} text {run['text'][:24]!r} uses disallowed color {found}")
            if 4 <= slide_index < len(roots) and not element_migration:
                check_text_safety(errors, slide_index, root, canvas, manifest)

        axis_issues = negative_chart_axis_ids(archive)
        if axis_issues:
            errors.append("Deck contains signed negative chart axis IDs that can break some importers; repair an output copy with safe_repair_deck.py")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument(
        "--element-migration-ledger",
        type=Path,
        help="Completed ledger; fixed pages/backgrounds/fonts remain strict while body colors/overlaps use the visual-review record",
    )
    args = parser.parse_args()
    deck = args.pptx.expanduser().resolve()
    if not deck.is_file() or deck.suffix.lower() != ".pptx":
        parser.error("pptx must be an existing .pptx file")
    if args.element_migration_ledger and not args.element_migration_ledger.exists():
        parser.error("--element-migration-ledger does not exist")
    ledger = args.element_migration_ledger.expanduser().resolve() if args.element_migration_ledger else None
    errors = validate(deck, element_migration_ledger=ledger)
    if errors:
        print("Brand validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("Brand validation passed: fixed pages, approved backgrounds, Logo zones, Tencent fonts, and applicable new-deck or migration review gates are valid.")


if __name__ == "__main__":
    main()
