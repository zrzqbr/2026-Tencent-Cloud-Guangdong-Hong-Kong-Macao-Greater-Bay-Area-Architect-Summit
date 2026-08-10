#!/usr/bin/env python3
"""Plan and audit summit-brand migrations without generating presentation content."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from brand_core import (
    EMU_PER_INCH,
    box_matches,
    boxes_intersect,
    canvas_from_presentation,
    drawable_elements,
    image_candidates,
    load_manifest,
    negative_chart_axis_ids,
    nearest_palette_color,
    object_counts,
    sha256,
    shape_box,
    slide_and_layout_images,
    slide_paths,
    text_runs,
    text_shapes,
    text_value,
    xml,
)


SUPPORTED = {".ppt", ".pptx", ".pdf", ".html", ".htm", ".md", ".markdown"}


class HTMLIntake(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []
        self.headings: list[str] = []
        self.images: list[str] = []
        self._heading: str | None = None
        self._heading_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"h1", "h2", "h3"}:
            self._heading = tag
            self._heading_parts = []
        if tag == "img":
            src = dict(attrs).get("src")
            if src:
                self.images.append(src)

    def handle_endtag(self, tag: str) -> None:
        if self._heading == tag:
            value = re.sub(r"\s+", " ", "".join(self._heading_parts)).strip()
            if value:
                self.headings.append(value)
            self._heading = None
            self._heading_parts = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.text.append(data.strip())
        if self._heading:
            self._heading_parts.append(data)


def approved_colors(manifest: dict) -> list[str]:
    palette = manifest["palette"]
    values = set(palette["allowedText"] + palette["chartSeries"] + palette["deepNavy"])
    values.update(block["color"] for block in palette["colorBlocks"])
    return sorted(values)


def classify_page(index: int, total: int, text: str, counts: dict[str, int]) -> str:
    compact = re.sub(r"\s+", "", text).lower()
    if index == 1:
        return "source-opening-or-title"
    if re.search(r"讲师|演讲嘉宾|speaker|aboutme|个人简介|嘉宾介绍|自我介绍", compact):
        return "speaker-profile-candidate"
    if re.search(r"目录|议程|agenda|contents|大纲", compact):
        return "agenda"
    if re.search(r"总结|结语|展望|q&a|qa|question|感谢", compact) or index == total:
        return "conclusion-candidate"
    if len(compact) <= 38 and sum(counts.values()) <= 6:
        return "section-divider-candidate"
    return "content"


def background_match(candidates: list[dict], manifest: dict, canvas: tuple[int, int]) -> tuple[str | None, dict | None]:
    by_hash = {item["sha256"]: item["id"] for item in manifest["backgrounds"]}
    for candidate in candidates:
        digest = sha256(candidate["data"])
        if digest not in by_hash:
            continue
        box = candidate.get("box")
        if candidate["kind"].endswith("background-fill") or box_matches(box, (0, 0, *canvas), 2000):
            return by_hash[digest], candidate
    return None, None


def slide_report(
    archive: zipfile.ZipFile,
    path: str,
    index: int,
    total: int,
    canvas: tuple[int, int],
    manifest: dict,
) -> dict:
    root = xml(archive, path)
    counts = object_counts(root)
    text = text_value(root).strip()
    runs = [run for run in text_runs(root) if run["text"].strip()]
    candidates = slide_and_layout_images(archive, path, root)
    background_id, background = background_match(candidates, manifest, canvas)
    allowed_fonts = {manifest["fonts"]["title"], manifest["fonts"]["body"]}
    palette = approved_colors(manifest)
    font_replacements = 0
    color_replacements = 0
    color_suggestions: dict[str, dict] = {}
    for run in runs:
        fonts = set(run["fonts"].values())
        if None in fonts or len(fonts) != 1 or not fonts <= allowed_fonts:
            font_replacements += 1
        color = run["color"]
        if color not in manifest["palette"]["allowedText"]:
            color_replacements += 1
            if color and re.fullmatch(r"[0-9A-F]{6}", color):
                color_suggestions[color] = nearest_palette_color(color, palette)

    warnings: list[dict] = []
    for node in drawable_elements(root):
        box = shape_box(node)
        if not box:
            continue
        x, y, width, height = box
        if x < 0 or y < 0 or x + width > canvas[0] or y + height > canvas[1]:
            warnings.append({"kind": "outside-canvas", "box": list(box)})

    clearance = round(manifest["release"]["textCollisionClearanceInches"] * EMU_PER_INCH)
    text_entries = text_shapes(root)
    for first_index, (first_text, first_box) in enumerate(text_entries):
        for second_text, second_box in text_entries[first_index + 1:]:
            if boxes_intersect(first_box, second_box, clearance):
                warnings.append(
                    {
                        "kind": "text-box-intersection",
                        "first": first_text[:80],
                        "second": second_text[:80],
                    }
                )

    approved_hashes = {item["sha256"] for item in manifest["backgrounds"]}
    for candidate in image_candidates(archive, path, root):
        box = candidate.get("box")
        if not box or not canvas[0] or not canvas[1]:
            continue
        area_ratio = box[2] * box[3] / (canvas[0] * canvas[1])
        if area_ratio >= 0.80 and sha256(candidate["data"]) not in approved_hashes:
            warnings.append(
                {
                    "kind": "legacy-full-slide-overlay",
                    "part": candidate["part"],
                    "areaRatio": round(area_ratio, 3),
                }
            )

    if background_id:
        background_spec = next(item for item in manifest["backgrounds"] if item["id"] == background_id)
        standard_width = manifest["canvas"]["standardEmu"][0]
        scale = canvas[0] / standard_width if standard_width else 1.0
        zones = []
        for zone in background_spec.get("logoZonesStandardInches", []):
            zones.append(tuple(round(value * EMU_PER_INCH * scale) for value in zone))
        for value, box in text_entries:
            if any(boxes_intersect(box, zone) for zone in zones):
                warnings.append({"kind": "logo-zone-text", "text": value[:80], "box": list(box)})

    return {
        "sourcePage": index,
        "classification": classify_page(index, total, text, counts),
        "visibleText": text,
        "objectCounts": counts,
        "runCount": len(runs),
        "fontReplacementCandidates": font_replacements,
        "colorReplacementCandidates": color_replacements,
        "colorSuggestions": sorted(color_suggestions.values(), key=lambda item: item["from"]),
        "approvedBackground": background_id,
        "backgroundInheritedFromLayout": bool(background and background["kind"].startswith("layout-")),
        "warnings": warnings,
    }


def inspect_pptx(source: Path, manifest: dict) -> dict:
    with zipfile.ZipFile(source) as archive:
        presentation, paths = slide_paths(archive)
        canvas = canvas_from_presentation(presentation)
        slides = [slide_report(archive, path, index, len(paths), canvas, manifest) for index, path in enumerate(paths, 1)]
        issues = negative_chart_axis_ids(archive)
        return {
            "pageCount": len(paths),
            "canvasEmu": list(canvas),
            "slides": slides,
            "totals": {
                "fontReplacementCandidates": sum(item["fontReplacementCandidates"] for item in slides),
                "colorReplacementCandidates": sum(item["colorReplacementCandidates"] for item in slides),
                "warnings": sum(len(item["warnings"]) for item in slides),
            },
            "signedChartAxisIds": issues,
        }


def inspect_pdf(source: Path) -> dict:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return {
            "pageCount": None,
            "dependencyNotice": "Install pypdf or use the companion PDF Skill for page-level extraction.",
            "editableRecovery": "Rebuild recoverable text, tables, and diagrams; do not flatten all pages into screenshots.",
        }
    reader = PdfReader(str(source))
    pages = []
    for index, page in enumerate(reader.pages, 1):
        value = page.extract_text() or ""
        pages.append({"sourcePage": index, "textCharacters": len(value), "textPreview": value[:500]})
    return {"pageCount": len(reader.pages), "pages": pages, "editableRecovery": "best-effort-reconstruction"}


def inspect_html(source: Path) -> dict:
    parser = HTMLIntake()
    parser.feed(source.read_text(encoding="utf-8", errors="replace"))
    return {
        "headingCount": len(parser.headings),
        "headings": parser.headings,
        "imageCount": len(parser.images),
        "images": parser.images,
        "textCharacters": len(" ".join(parser.text)),
    }


def inspect_markdown(source: Path) -> dict:
    value = source.read_text(encoding="utf-8", errors="replace")
    headings = [match.group(2).strip() for match in re.finditer(r"(?m)^(#{1,6})\s+(.+)$", value)]
    images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", value)
    code_blocks = len(re.findall(r"(?m)^```", value)) // 2
    return {"headingCount": len(headings), "headings": headings, "imageCount": len(images), "images": images, "codeBlockCount": code_blocks}


def source_intake(source: Path, manifest: dict) -> dict:
    suffix = source.suffix.lower()
    if suffix == ".pptx":
        return inspect_pptx(source, manifest)
    if suffix == ".ppt":
        return {
            "conversionRequired": True,
            "action": "Convert a copy to PPTX with PowerPoint, WPS, or LibreOffice before element-level migration.",
            "sourceMustRemainUnchanged": True,
        }
    if suffix == ".pdf":
        return inspect_pdf(source)
    if suffix in {".html", ".htm"}:
        return inspect_html(source)
    return inspect_markdown(source)


def build_mapping(intake: dict, manifest: dict) -> dict:
    slides = intake.get("slides", [])
    speaker_page = next((item["sourcePage"] for item in slides if item["classification"] == "speaker-profile-candidate"), None)
    mappings = []
    if slides:
        mappings.append(
            {
                "sourcePages": [1],
                "destinationSlides": [2],
                "mode": "extract-title-fields-only",
                "note": "Use the exact title-page field geometry; do not copy the source visual skin.",
            }
        )
        if speaker_page:
            mappings.append(
                {
                    "sourcePages": [speaker_page],
                    "destinationSlides": [3],
                    "mode": "populate-optional-speaker-page",
                    "note": "Populate only verified speaker data and photo; otherwise leave slide 3 blank.",
                }
            )
        destination = 4
        for item in slides:
            source_page = item["sourcePage"]
            if source_page == 1 or source_page == speaker_page:
                continue
            mappings.append(
                {
                    "sourcePages": [source_page],
                    "destinationSlides": [destination],
                    "mode": "element-level-migration",
                    "classification": item["classification"],
                    "structure": "flexible",
                }
            )
            destination += 1
    return {
        "schemaVersion": 1,
        "templateSourceSlides": manifest["template"]["sourceSlideRoles"],
        "fixedDestinationSlides": {"cover": 1, "title": 2, "speaker": 3, "thanks": "last"},
        "excludedTemplateSlides": [manifest["template"]["sourceSlideRoles"]["assetLibrary"]],
        "mappings": mappings,
        "penultimateRule": "The talk's own conclusion/Q&A/contact page is penultimate.",
        "finalRule": "Append the canonical single-image thank-you page unchanged.",
    }


def ledger_stub(intake: dict, mapping: dict) -> dict:
    slides = {item["sourcePage"]: item for item in intake.get("slides", [])}
    entries = []
    for item in mapping["mappings"]:
        if item["mode"] != "element-level-migration":
            continue
        source_page = item["sourcePages"][0]
        before = slides[source_page]["objectCounts"]
        entries.append(
            {
                "sourcePages": item["sourcePages"],
                "destinationSlides": item["destinationSlides"],
                "before": before,
                "deleted": [],
                "addedBrandElements": [],
                "rasterizedElements": [],
                "after": None,
                "notesPreserved": None,
                "hyperlinksPreserved": None,
            }
        )
    return {"schemaVersion": 2, "slides": entries, "status": "stub-requires-companion-tool-completion"}


def companion_instructions(source: Path, output_dir: Path) -> str:
    return f"""# Companion presentation tool instructions

Source: `{source}`

This Skill is the brand and migration layer. Use a presentation-authoring Skill or tool to execute `migration-map.json` and complete `element-migration-ledger.json`.

1. Preserve the canonical source template package and embedded Tencent fonts.
2. Output slide 1 comes from template source slide 1 unchanged.
3. Output slide 2 comes from template source slide 3 with exact fields from the source title.
4. Template source slide 2 is an icon library only and never becomes an output slide.
5. Output slide 3 comes from template source slide 4. Populate verified speaker information or leave the approved background blank.
6. From output slide 4 onward, keep structure flexible and migrate source objects element by element.
7. Use only approved backgrounds and preserve their Logo exclusion zones.
8. Place the talk's own conclusion/Q&A/contact page penultimate.
9. Append the canonical final thank-you page unchanged.
10. Render every slide, repair overlaps/clipping, complete the ledger, then run both validators.

Artifacts directory: `{output_dir}`
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="PPT/PPTX/PDF/HTML/Markdown source")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for dry-run reports and mapping artifacts")
    parser.add_argument("--destination", type=Path, help="Optional migrated PPTX to validate after planning")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in SUPPORTED:
        parser.error("--source must be an existing .ppt, .pptx, .pdf, .html, .htm, .md, or .markdown file")
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    intake = source_intake(source, manifest)
    mapping = build_mapping(intake, manifest)
    ledger = ledger_stub(intake, mapping)

    report = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "dryRun": True,
        "skillRole": manifest["event"]["skillRole"],
        "source": str(source),
        "sourceType": source.suffix.lower().lstrip("."),
        "canonicalTemplate": {
            "file": manifest["template"]["file"],
            "sha256": manifest["template"]["sha256"],
        },
        "intake": intake,
        "migrationMap": "migration-map.json",
        "ledger": "element-migration-ledger.json",
        "safeAutomaticRepairs": ["explicit font names", "direct text colors", "chart series palette", "signed chart axis compatibility IDs"],
        "structuralWorkOwner": "companion presentation-authoring Skill/tool",
        "contentStructureAfterSlide3": "unconstrained by this Skill",
    }

    destination_errors = None
    if args.destination:
        destination = args.destination.expanduser().resolve()
        if not destination.is_file() or destination.suffix.lower() != ".pptx":
            parser.error("--destination must be an existing .pptx file")
        from validate_deck_brand import validate

        destination_errors = validate(destination)
        report["destinationValidation"] = {"file": str(destination), "passed": not destination_errors, "errors": destination_errors}

    (output_dir / "adapter-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "migration-map.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "element-migration-ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "companion-instructions.md").write_text(companion_instructions(source, output_dir), encoding="utf-8")

    summary = {
        "report": str(output_dir / "adapter-report.json"),
        "mapping": str(output_dir / "migration-map.json"),
        "ledger": str(output_dir / "element-migration-ledger.json"),
        "instructions": str(output_dir / "companion-instructions.md"),
        "destinationPassed": None if destination_errors is None else not destination_errors,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if destination_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
