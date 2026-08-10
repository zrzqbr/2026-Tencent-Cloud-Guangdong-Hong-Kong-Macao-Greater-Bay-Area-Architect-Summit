#!/usr/bin/env python3
"""Shared OOXML, geometry, manifest, and color helpers for the summit Skill."""

from __future__ import annotations

import hashlib
import json
import math
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "brand-manifest.json"

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
NS = {"p": P, "a": A, "r": R, "rel": REL, "c": C}

EMU_PER_INCH = 914400


def load_manifest(path: Path | None = None) -> dict:
    return json.loads((path or MANIFEST_PATH).read_text(encoding="utf-8"))


def sha256(data_or_path: bytes | Path) -> str:
    if isinstance(data_or_path, Path):
        data = data_or_path.read_bytes()
    else:
        data = data_or_path
    return hashlib.sha256(data).hexdigest()


def xml(archive: zipfile.ZipFile, name: str) -> ET.Element:
    return ET.fromstring(archive.read(name))


def package_path(base: str, target: str) -> str:
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    return posixpath.normpath(posixpath.join(base, target))


def rel_map(archive: zipfile.ZipFile, rel_name: str) -> dict[str, tuple[str, str]]:
    if rel_name not in archive.namelist():
        return {}
    return {
        node.get("Id", ""): (node.get("Type", ""), node.get("Target", ""))
        for node in xml(archive, rel_name)
    }


def slide_paths(archive: zipfile.ZipFile) -> tuple[ET.Element, list[str]]:
    presentation = xml(archive, "ppt/presentation.xml")
    rels = rel_map(archive, "ppt/_rels/presentation.xml.rels")
    paths = []
    for item in presentation.findall("./p:sldIdLst/p:sldId", NS):
        _, target = rels[item.get(f"{{{R}}}id", "")]
        paths.append(package_path("ppt", target))
    return presentation, paths


def slide_rels_name(slide_path: str) -> str:
    dirname = posixpath.dirname(slide_path)
    basename = posixpath.basename(slide_path)
    return f"{dirname}/_rels/{basename}.rels"


def related_part(
    archive: zipfile.ZipFile,
    source_path: str,
    rel_id: str,
) -> tuple[str, str] | None:
    rels = rel_map(archive, slide_rels_name(source_path))
    rel_type, target = rels.get(rel_id, ("", ""))
    if not target:
        return None
    return rel_type, package_path(posixpath.dirname(source_path), target)


def slide_layout_path(archive: zipfile.ZipFile, slide_path: str) -> str | None:
    for rel_type, target in rel_map(archive, slide_rels_name(slide_path)).values():
        if rel_type.endswith("/slideLayout"):
            return package_path(posixpath.dirname(slide_path), target)
    return None


def part_rels_name(part_path: str) -> str:
    dirname = posixpath.dirname(part_path)
    basename = posixpath.basename(part_path)
    return f"{dirname}/_rels/{basename}.rels"


def image_from_blip(
    archive: zipfile.ZipFile,
    part_path: str,
    blip: ET.Element | None,
) -> tuple[str, bytes] | None:
    if blip is None:
        return None
    rel_id = blip.get(f"{{{R}}}embed", "")
    rels = rel_map(archive, part_rels_name(part_path))
    rel_type, target = rels.get(rel_id, ("", ""))
    if not rel_type.endswith("/image"):
        return None
    image_path = package_path(posixpath.dirname(part_path), target)
    return image_path, archive.read(image_path)


def xfrm_box(node: ET.Element, prefix: str = "p") -> tuple[int, int, int, int] | None:
    xfrm = node.find(f"./{prefix}:spPr/a:xfrm", NS)
    if xfrm is None and prefix == "p":
        xfrm = node.find("./p:xfrm", NS)
    if xfrm is None:
        return None
    off = xfrm.find("./a:off", NS)
    ext = xfrm.find("./a:ext", NS)
    if off is None or ext is None:
        return None
    try:
        return tuple(int(value) for value in (off.get("x"), off.get("y"), ext.get("cx"), ext.get("cy")))
    except (TypeError, ValueError):
        return None


def shape_box(node: ET.Element) -> tuple[int, int, int, int] | None:
    if node.tag == f"{{{P}}}graphicFrame":
        xfrm = node.find("./p:xfrm", NS)
        if xfrm is None:
            return None
        off = xfrm.find("./a:off", NS)
        ext = xfrm.find("./a:ext", NS)
    elif node.tag == f"{{{P}}}grpSp":
        xfrm = node.find("./p:grpSpPr/a:xfrm", NS)
        if xfrm is None:
            return None
        off = xfrm.find("./a:off", NS)
        ext = xfrm.find("./a:ext", NS)
    else:
        return xfrm_box(node)
    if off is None or ext is None:
        return None
    return tuple(int(value) for value in (off.get("x"), off.get("y"), ext.get("cx"), ext.get("cy")))


def box_matches(
    actual: tuple[int, int, int, int] | None,
    expected: tuple[int, int, int, int],
    tolerance: int = 10000,
) -> bool:
    return actual is not None and all(abs(a - e) <= tolerance for a, e in zip(actual, expected))


def boxes_intersect(
    first: tuple[int, int, int, int],
    second: tuple[int, int, int, int],
    clearance: int = 0,
) -> bool:
    ax, ay, aw, ah = first
    bx, by, bw, bh = second
    return (
        min(ax + aw, bx + bw) - max(ax, bx) > clearance
        and min(ay + ah, by + bh) - max(ay, by) > clearance
    )


def drawable_elements(root: ET.Element) -> list[ET.Element]:
    tree = root.find("./p:cSld/p:spTree", NS)
    if tree is None:
        return []
    ignored = {f"{{{P}}}nvGrpSpPr", f"{{{P}}}grpSpPr"}
    return [node for node in list(tree) if node.tag not in ignored]


def text_value(node: ET.Element) -> str:
    return "".join(item.text or "" for item in node.findall(".//a:t", NS))


def run_style(run: ET.Element) -> dict:
    value = "".join(node.text or "" for node in run.findall("./a:t", NS))
    props = run.find("./a:rPr", NS)
    size = int(props.get("sz", "0")) if props is not None else 0
    color = None
    if props is not None:
        color_node = props.find("./a:solidFill/a:srgbClr", NS)
        if color_node is not None:
            color = color_node.get("val", "").upper() or None
    fonts = {}
    for tag in ("latin", "ea", "cs"):
        font_node = props.find(f"./a:{tag}", NS) if props is not None else None
        fonts[tag] = font_node.get("typeface") if font_node is not None else None
    return {"text": value, "size": size, "color": color, "fonts": fonts}


def text_runs(root: ET.Element) -> list[dict]:
    return [run_style(run) for run in root.findall(".//a:r", NS) + root.findall(".//a:fld", NS)]


def text_shapes(root: ET.Element) -> list[tuple[str, tuple[int, int, int, int]]]:
    parents = {child: parent for parent in root.iter() for child in parent}
    entries = []
    for shape in root.findall(".//p:sp", NS):
        ancestor = parents.get(shape)
        grouped = False
        while ancestor is not None:
            if ancestor.tag == f"{{{P}}}grpSp":
                grouped = True
                break
            ancestor = parents.get(ancestor)
        if grouped:
            continue
        value = text_value(shape).strip()
        box = shape_box(shape)
        if value and box is not None:
            entries.append((value, box))
    return entries


def object_counts(root: ET.Element) -> dict[str, int]:
    tree = root.find("./p:cSld/p:spTree", NS)
    if tree is None:
        return {"shapes": 0, "connectors": 0, "images": 0, "tables": 0, "charts": 0}
    result = {
        "shapes": len(tree.findall(".//p:sp", NS)),
        "connectors": len(tree.findall(".//p:cxnSp", NS)),
        "images": len(tree.findall(".//p:pic", NS)),
        "tables": 0,
        "charts": 0,
    }
    for frame in tree.findall(".//p:graphicFrame", NS):
        data = frame.find(".//a:graphicData", NS)
        uri = data.get("uri", "") if data is not None else ""
        if uri.endswith("/table"):
            result["tables"] += 1
        elif uri.endswith("/chart"):
            result["charts"] += 1
    return result


def normalized_text(root: ET.Element) -> str:
    return re.sub(r"\s+", "", text_value(root))


def image_candidates(
    archive: zipfile.ZipFile,
    part_path: str,
    root: ET.Element,
) -> list[dict]:
    candidates = []
    background_blip = root.find("./p:cSld/p:bg/p:bgPr/a:blipFill/a:blip", NS)
    background = image_from_blip(archive, part_path, background_blip)
    if background:
        candidates.append({"part": background[0], "data": background[1], "box": None, "kind": "background-fill", "cropped": False})
    for picture in root.findall("./p:cSld/p:spTree/p:pic", NS):
        image = image_from_blip(archive, part_path, picture.find(".//a:blip", NS))
        if not image:
            continue
        crop = picture.find("./p:blipFill/a:srcRect", NS)
        cropped = crop is not None and any(int(value or "0") != 0 for value in crop.attrib.values())
        candidates.append({"part": image[0], "data": image[1], "box": shape_box(picture), "kind": "picture", "cropped": cropped})
    return candidates


def slide_and_layout_images(
    archive: zipfile.ZipFile,
    slide_path: str,
    slide_root: ET.Element,
) -> list[dict]:
    candidates = image_candidates(archive, slide_path, slide_root)
    layout_path = slide_layout_path(archive, slide_path)
    if layout_path:
        layout_root = xml(archive, layout_path)
        for candidate in image_candidates(archive, layout_path, layout_root):
            candidate = dict(candidate)
            candidate["kind"] = f"layout-{candidate['kind']}"
            candidate["layoutPath"] = layout_path
            candidates.append(candidate)
    return candidates


def canvas_from_presentation(presentation: ET.Element) -> tuple[int, int]:
    size = presentation.find("./p:sldSz", NS)
    if size is None:
        return 0, 0
    return int(size.get("cx", "0")), int(size.get("cy", "0"))


def inches_box_to_emu(box: list[float], scale: float = 1.0) -> tuple[int, int, int, int]:
    return tuple(round(value * EMU_PER_INCH * scale) for value in box)


def _rgb_to_linear(value: int) -> float:
    channel = value / 255.0
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_rgb_to_linear(value) for value in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(first: tuple[int, int, int], second: tuple[int, int, int]) -> float:
    high, low = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def rgb_hex(rgb: tuple[int, int, int]) -> str:
    return "".join(f"{value:02X}" for value in rgb)


def _xyz(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (_rgb_to_linear(value) for value in rgb)
    return (
        r * 0.4124564 + g * 0.3575761 + b * 0.1804375,
        r * 0.2126729 + g * 0.7151522 + b * 0.0721750,
        r * 0.0193339 + g * 0.1191920 + b * 0.9503041,
    )


def _lab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    x, y, z = _xyz(rgb)
    xn, yn, zn = 0.95047, 1.0, 1.08883

    def curve(value: float) -> float:
        return value ** (1 / 3) if value > 0.008856 else 7.787 * value + 16 / 116

    fx, fy, fz = curve(x / xn), curve(y / yn), curve(z / zn)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(first: tuple[int, int, int], second: tuple[int, int, int]) -> float:
    """Return CIEDE2000 perceptual color distance."""
    l1, a1, b1 = _lab(first)
    l2, a2, b2 = _lab(second)
    c1, c2 = math.hypot(a1, b1), math.hypot(a2, b2)
    c_avg = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt(c_avg**7 / (c_avg**7 + 25**7)))
    a1p, a2p = a1 * (1 + g), a2 * (1 + g)
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)

    def hue(b: float, a: float) -> float:
        angle = math.degrees(math.atan2(b, a))
        return angle + 360 if angle < 0 else angle

    h1p = hue(b1, a1p) if c1p > 1e-9 else 0
    h2p = hue(b2, a2p) if c2p > 1e-9 else 0
    dlp, dcp = l2 - l1, c2p - c1p
    if c1p * c2p < 1e-9:
        dhp = 0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    elif h2p - h1p > 180:
        dhp = h2p - h1p - 360
    else:
        dhp = h2p - h1p + 360
    dh_term = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dhp / 2))
    lp_avg, cp_avg = (l1 + l2) / 2, (c1p + c2p) / 2
    if c1p * c2p < 1e-9:
        hp_avg = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hp_avg = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hp_avg = (h1p + h2p + 360) / 2
    else:
        hp_avg = (h1p + h2p - 360) / 2
    t = (
        1
        - 0.17 * math.cos(math.radians(hp_avg - 30))
        + 0.24 * math.cos(math.radians(2 * hp_avg))
        + 0.32 * math.cos(math.radians(3 * hp_avg + 6))
        - 0.20 * math.cos(math.radians(4 * hp_avg - 63))
    )
    sl = 1 + 0.015 * (lp_avg - 50) ** 2 / math.sqrt(20 + (lp_avg - 50) ** 2)
    sc = 1 + 0.045 * cp_avg
    sh = 1 + 0.015 * cp_avg * t
    rc = 2 * math.sqrt(cp_avg**7 / (cp_avg**7 + 25**7))
    rt = -math.sin(math.radians(2 * 30 * math.exp(-((hp_avg - 275) / 25) ** 2))) * rc
    return math.sqrt((dlp / sl) ** 2 + (dcp / sc) ** 2 + (dh_term / sh) ** 2 + rt * (dcp / sc) * (dh_term / sh))


def nearest_palette_color(value: str, palette: list[str]) -> dict:
    source = hex_rgb(value)
    candidates = [(candidate, delta_e(source, hex_rgb(candidate))) for candidate in palette]
    candidate, distance = min(candidates, key=lambda item: item[1])
    return {"from": value.upper().lstrip("#"), "to": candidate.upper().lstrip("#"), "deltaE": round(distance, 3)}


def negative_chart_axis_ids(archive: zipfile.ZipFile) -> list[dict]:
    issues = []
    for name in archive.namelist():
        if not re.fullmatch(r"ppt/charts/chart\d+\.xml", name):
            continue
        root = xml(archive, name)
        for node in root.findall(".//c:axId", NS) + root.findall(".//c:crossAx", NS):
            value = node.get("val", "")
            if value.startswith("-"):
                issues.append({"part": name, "tag": node.tag.rsplit("}", 1)[-1], "value": int(value)})
    return issues
