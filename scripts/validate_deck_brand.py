#!/usr/bin/env python3
"""Validate summit PPTX fixed assets, fonts, colors, and text-box collision risks."""

import argparse
import hashlib
import posixpath
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXED = ROOT / "assets" / "fixed-pages"
BACKGROUNDS = ROOT / "assets" / "backgrounds"

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"p": P, "a": A, "r": R, "rel": REL}

STANDARD_CX = 12192000
STANDARD_CY = 6858000
ORIGINAL_CX = 18288000
ORIGINAL_CY = 10287000
ALLOWED_CANVASES = {(STANDARD_CX, STANDARD_CY), (ORIGINAL_CX, ORIGINAL_CY)}
ALLOWED_FONTS = {"腾讯体 W7", "腾讯体 W3"}
TEXT_COLLISION_CLEARANCE = round(0.04 * 914400)
ALLOWED_TEXT_COLORS = {
    "FD9D50", "FFFFFF", "FFE7B9", "A7A7A7", "8B8C8C",
    "4A6FE8", "4D9557", "00365F",
}
CANONICAL_BACKGROUND_HASHES = {
    "background-01-cover.jpg": "f8a7f1a3f6536f632b6a54511c545ca1940b6d4d94fd4585430535f4e09f05ac",
    "background-02-content.jpg": "1654ba475d1c3e35c3b8ed25772fe7871f7f08137f86b3a1d226975087b6c68c",
    "background-03-section.jpg": "a05520185110930bcfd659528f6d5241d026ee04598932db9417e4fcc00145a3",
    "background-04-content-alt.jpg": "20ca3aed69d2630163567e66c9f1136e1c39411058f8b3de816bc9776e18f937",
    "background-05-content-alt.jpg": "4ec6d12f308a16a1df35518ace49e283ee7e278e5b1cca458219d4d4a970510b",
    "background-06-closing.jpg": "3a337f7867a7abf3e2ee6cc782d65225547bb8fce7f01adfb4f163d4fff1e866",
}
FIXED_PAGE_HASHES = {
    "slide-01-main-kv.jpg": CANONICAL_BACKGROUND_HASHES["background-01-cover.jpg"],
    "slide-02-title-background.jpg": CANONICAL_BACKGROUND_HASHES["background-02-content.jpg"],
    "slide-03-original-background.jpg": CANONICAL_BACKGROUND_HASHES["background-03-section.jpg"],
    "slide-final-thanks.png": "f45e79d23692ef6af37ab48e0a0f06c8d7bde3866ff1980dadd7a68def9a29d6",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def xml(archive: zipfile.ZipFile, name: str):
    return ET.fromstring(archive.read(name))


def rel_map(archive: zipfile.ZipFile, rel_name: str):
    return {
        node.get("Id"): (node.get("Type", ""), node.get("Target", ""))
        for node in xml(archive, rel_name)
    }


def slide_paths(archive: zipfile.ZipFile):
    presentation = xml(archive, "ppt/presentation.xml")
    rels = rel_map(archive, "ppt/_rels/presentation.xml.rels")
    paths = []
    for item in presentation.findall("./p:sldIdLst/p:sldId", NS):
        _, target = rels[item.get(f"{{{R}}}id")]
        paths.append(posixpath.normpath(posixpath.join("ppt", target)))
    return presentation, paths


def slide_images(archive: zipfile.ZipFile, slide_path: str, root):
    dirname = posixpath.dirname(slide_path)
    basename = posixpath.basename(slide_path)
    rel_name = f"{dirname}/_rels/{basename}.rels"
    rels = rel_map(archive, rel_name)
    images = []
    for picture in root.findall(".//p:pic", NS):
        blip = picture.find(".//a:blip", NS)
        if blip is None:
            continue
        rel_id = blip.get(f"{{{R}}}embed")
        rel_type, target = rels.get(rel_id, ("", ""))
        if rel_type.endswith("/image"):
            media_path = posixpath.normpath(posixpath.join(dirname, target))
            transform = picture.find("./p:spPr/a:xfrm", NS)
            box = None
            if transform is not None:
                off = transform.find("./a:off", NS)
                ext = transform.find("./a:ext", NS)
                if off is not None and ext is not None:
                    box = tuple(int(v) for v in (off.get("x"), off.get("y"), ext.get("cx"), ext.get("cy")))
            crop = picture.find("./p:blipFill/a:srcRect", NS)
            cropped = crop is not None and any(int(value or "0") != 0 for value in crop.attrib.values())
            images.append((rel_id, media_path, archive.read(media_path), box, cropped))
    return images


def run_style(run):
    value = "".join(node.text or "" for node in run.findall("./a:t", NS))
    props = run.find("./a:rPr", NS)
    size = int(props.get("sz", "0")) if props is not None else 0
    color_node = props.find("./a:solidFill/a:srgbClr", NS) if props is not None else None
    color_value = color_node.get("val") if color_node is not None else None
    color = color_value.upper() if color_value else None
    fonts = {}
    for tag in ("latin", "ea", "cs"):
        node = props.find(f"./a:{tag}", NS) if props is not None else None
        fonts[tag] = node.get("typeface") if node is not None else None
    return value, size, color, fonts


def text_runs(root):
    return [run_style(run) for run in root.findall(".//a:r", NS) + root.findall(".//a:fld", NS)]


def text_and_style(shape):
    runs = [item for item in text_runs(shape) if item[0]]
    value = "".join(item[0] for item in runs)
    sizes = {item[1] for item in runs}
    colors = {item[2] for item in runs}
    fonts = {face for item in runs for face in item[3].values() if face}
    return (
        value,
        next(iter(sizes)) if len(sizes) == 1 else 0,
        next(iter(colors)) if len(colors) == 1 else None,
        fonts,
    )


def shape_box(shape):
    transform = shape.find("./p:spPr/a:xfrm", NS)
    if transform is None:
        return None
    off = transform.find("./a:off", NS)
    ext = transform.find("./a:ext", NS)
    if off is None or ext is None:
        return None
    return tuple(int(v) for v in (off.get("x"), off.get("y"), ext.get("cx"), ext.get("cy")))


def text_shapes(root):
    """Return ungrouped non-empty text shapes with slide-coordinate boxes."""
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
        value = "".join(node.text or "" for node in shape.findall(".//a:t", NS)).strip()
        box = shape_box(shape)
        if value and box is not None:
            entries.append((value, box))
    return entries


def check_text_collisions(errors, slide_number, root, scale):
    clearance = round(TEXT_COLLISION_CLEARANCE * scale)
    entries = text_shapes(root)
    for index, (first_text, first_box) in enumerate(entries):
        ax, ay, aw, ah = first_box
        for second_text, second_box in entries[index + 1:]:
            bx, by, bw, bh = second_box
            overlap_w = min(ax + aw, bx + bw) - max(ax, bx)
            overlap_h = min(ay + ah, by + bh) - max(ay, by)
            if overlap_w > clearance and overlap_h > clearance:
                errors.append(
                    f"Slide {slide_number} text boxes {first_text[:24]!r} and {second_text[:24]!r} "
                    "substantially intersect; reflow them and rerender the slide"
                )


def check_box(errors, label, actual, expected, tolerance=2000):
    if not box_matches(actual, expected, tolerance):
        errors.append(f"Slide 2 {label} box must be {expected}; found {actual}")


def box_matches(actual, expected, tolerance=2000):
    return actual is not None and all(abs(a - e) <= tolerance for a, e in zip(actual, expected))


def drawable_elements(root):
    tree = root.find("./p:cSld/p:spTree", NS)
    if tree is None:
        return []
    ignored = {f"{{{P}}}nvGrpSpPr", f"{{{P}}}grpSpPr"}
    return [node for node in list(tree) if node.tag not in ignored]


def check_asset_integrity(errors):
    for name, expected in CANONICAL_BACKGROUND_HASHES.items():
        path = BACKGROUNDS / name
        actual = sha256(path.read_bytes()) if path.exists() else None
        if actual != expected:
            errors.append(f"Canonical background asset {name} is missing or has been modified")
    for name, expected in FIXED_PAGE_HASHES.items():
        path = FIXED / name
        actual = sha256(path.read_bytes()) if path.exists() else None
        if actual != expected:
            errors.append(f"Fixed-page asset {name} is missing or has been modified")


def validate(deck: Path) -> list[str]:
    errors = []
    check_asset_integrity(errors)
    approved_hashes = set(CANONICAL_BACKGROUND_HASHES.values()) | {
        FIXED_PAGE_HASHES["slide-final-thanks.png"]
    }
    opening_fixed_hashes = [
        FIXED_PAGE_HASHES["slide-01-main-kv.jpg"],
        FIXED_PAGE_HASHES["slide-02-title-background.jpg"],
        FIXED_PAGE_HASHES["slide-03-original-background.jpg"],
    ]

    with zipfile.ZipFile(deck) as archive:
        presentation, paths = slide_paths(archive)
        size = presentation.find("./p:sldSz", NS)
        canvas = (int(size.get("cx", 0)), int(size.get("cy", 0))) if size is not None else (0, 0)
        if canvas not in ALLOWED_CANVASES:
            errors.append("Deck must use the standard 13.333 x 7.5 or original 20 x 11.25 inch 16:9 canvas")
        if len(paths) < 4:
            return errors + ["Deck must contain the fixed first three slides and the fixed final thank-you slide"]

        roots = [xml(archive, path) for path in paths]
        all_images = [slide_images(archive, path, root) for path, root in zip(paths, roots)]
        full_slide_box = (0, 0, *canvas)
        final_hash = FIXED_PAGE_HASHES["slide-final-thanks.png"]
        for index, images in enumerate(all_images, 1):
            approved = [item for item in images if sha256(item[2]) in approved_hashes]
            if not any(box_matches(box, full_slide_box) and not cropped for _, _, _, box, cropped in approved):
                errors.append(f"Slide {index} does not contain an approved background placed exactly full-slide")
            drawables = drawable_elements(roots[index - 1])
            if not drawables or drawables[0].tag != f"{{{P}}}pic" or not approved or images[0] not in approved:
                errors.append(f"Slide {index} approved background must be the bottom-most visible object")
            if index != len(paths) and any(sha256(data) == final_hash for _, _, data, _, _ in images):
                errors.append(f"Slide {index} uses the fixed thank-you asset before the final slide")

        for index in (0, 2):
            root = roots[index]
            visible_count = len(root.findall(".//p:pic", NS)) + len(root.findall(".//p:sp", NS))
            visible_count += len(root.findall(".//p:graphicFrame", NS)) + len(root.findall(".//p:cxnSp", NS))
            if visible_count != 1 or len(all_images[index]) != 1:
                errors.append(f"Slide {index + 1} must contain only its single canonical background image")
            elif (sha256(all_images[index][0][2]) != opening_fixed_hashes[index]
                  or not box_matches(all_images[index][0][3], full_slide_box)
                  or all_images[index][0][4]):
                errors.append(f"Slide {index + 1} background does not match the canonical asset")

        final_root = roots[-1]
        final_visible_count = len(final_root.findall(".//p:pic", NS)) + len(final_root.findall(".//p:sp", NS))
        final_visible_count += len(final_root.findall(".//p:graphicFrame", NS)) + len(final_root.findall(".//p:cxnSp", NS))
        if final_visible_count != 1 or len(all_images[-1]) != 1:
            errors.append("Final slide must contain only the single canonical thank-you image")
        elif (sha256(all_images[-1][0][2]) != final_hash
              or not box_matches(all_images[-1][0][3], full_slide_box)
              or all_images[-1][0][4]):
            errors.append("Final slide does not match the canonical thank-you asset")

        if not any(sha256(data) == opening_fixed_hashes[1] and box_matches(box, full_slide_box) and not cropped
                   for _, _, data, box, cropped in all_images[1]):
            errors.append("Slide 2 background does not match the canonical title background")
        slide2_shapes = [shape for shape in roots[1].findall(".//p:sp", NS) if shape.findall(".//a:t", NS)]
        if len(slide2_shapes) != 3:
            errors.append(f"Slide 2 must contain exactly three text fields; found {len(slide2_shapes)}")
        if len(drawable_elements(roots[1])) != 4 or len(all_images[1]) != 1:
            errors.append("Slide 2 must contain only one canonical background and its three text fields")
        styled = [(*text_and_style(shape), shape_box(shape)) for shape in slide2_shapes]
        main = next((item for item in styled if item[1] == 8800), None)
        subtitle = next((item for item in styled if item[1] == 5400), None)
        speaker = next((item for item in styled if item[1] == 2800), None)
        scale = canvas[0] / STANDARD_CX if canvas[0] else 1
        expected_styles = [
            ("main title", main, "FD9D50", "腾讯体 W7", (1828800, 1865376, 8513064, 1124712)),
            ("subtitle", subtitle, "FD9D50", "腾讯体 W7", (2788920, 2944368, 6592824, 694944)),
            ("speaker", speaker, "FFFFFF", "腾讯体 W3", (4745736, 4818384, 2624328, 356616)),
        ]
        for label, item, color, font, box in expected_styles:
            if item is None:
                errors.append(f"Slide 2 is missing the required {label} size")
                continue
            _, _, actual_color, fonts, actual_box = item
            if actual_color != color:
                errors.append(f"Slide 2 {label} color must be #{color}; found {actual_color}")
            if fonts != {font}:
                errors.append(f"Slide 2 {label} font must be {font}; found {sorted(fonts)}")
            scaled_box = tuple(round(value * scale) for value in box)
            check_box(errors, label, actual_box, scaled_box)

        for slide_index, root in enumerate(roots, 1):
            for value, _, color, fonts in text_runs(root):
                if not value.strip():
                    continue
                font_values = set(fonts.values())
                if None in font_values or len(font_values) != 1 or not font_values <= ALLOWED_FONTS:
                    errors.append(
                        f"Slide {slide_index} text {value[:24]!r} must set latin/ea/cs to one exact Tencent font; "
                        f"found {fonts}"
                    )
                if color not in ALLOWED_TEXT_COLORS:
                    found = f"#{color}" if color else "no direct sRGB color"
                    errors.append(f"Slide {slide_index} text {value[:24]!r} uses disallowed color {found}")
        for slide_index, root in enumerate(roots[3:-1], 4):
            check_text_collisions(errors, slide_index, root, scale)
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    args = parser.parse_args()
    errors = validate(args.pptx.resolve())
    if errors:
        print("Brand validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print(
        "Brand validation passed: canonical assets, fixed slides, final thank-you page, backgrounds, "
        "fonts, text colors, and text-box collision checks are valid."
    )


if __name__ == "__main__":
    main()
