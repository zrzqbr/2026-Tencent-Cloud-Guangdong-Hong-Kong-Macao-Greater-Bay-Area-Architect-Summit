#!/usr/bin/env python3
"""Inspect a summit template and stage or apply approved reusable assets."""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path

from brand_core import (
    MANIFEST_PATH,
    load_manifest,
    negative_chart_axis_ids,
    object_counts,
    R,
    related_part,
    sha256,
    shape_box,
    slide_paths,
    text_runs,
    text_value,
    xml,
)


BACKGROUND_TARGETS = {
    "ppt/media/image1.jpeg": "backgrounds/background-01-cover.jpg",
    "ppt/media/image2.jpeg": "backgrounds/background-02-content.jpg",
    "ppt/media/image3.jpeg": "backgrounds/background-03-section.jpg",
    "ppt/media/image4.jpeg": "backgrounds/background-04-content-alt.jpg",
    "ppt/media/image5.jpeg": "backgrounds/background-05-content-alt.jpg",
    "ppt/media/image6.jpeg": "backgrounds/background-06-closing.jpg",
}


def stage_template(template: Path, stage: Path, rendered_thanks: Path | None) -> dict:
    manifest = load_manifest()
    assets = stage / "assets"
    backgrounds = assets / "backgrounds"
    fixed = assets / "fixed-pages"
    icons = assets / "icons"
    backgrounds.mkdir(parents=True, exist_ok=True)
    fixed.mkdir(parents=True, exist_ok=True)
    icons.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, assets / "0815-architect-summit-template.pptx")

    report = {
        "template": str(template),
        "sha256": sha256(template),
        "expectedSha256": manifest["template"]["sha256"],
        "assets": [],
        "icons": [],
        "slides": [],
        "compatibilityIssues": [],
        "warnings": [],
    }

    with zipfile.ZipFile(template) as archive:
        _, paths = slide_paths(archive)
        report["slideCount"] = len(paths)
        for source_name, target_name in BACKGROUND_TARGETS.items():
            if source_name not in archive.namelist():
                report["warnings"].append(f"Missing {source_name}")
                continue
            data = archive.read(source_name)
            target = assets / target_name
            target.write_bytes(data)
            report["assets"].append({"source": source_name, "target": f"assets/{target_name}", "sha256": sha256(data)})

        fixed_copies = {
            "ppt/media/image1.jpeg": "slide-01-main-kv.jpg",
            "ppt/media/image2.jpeg": "slide-02-title-background.jpg",
            "ppt/media/image3.jpeg": "slide-03-original-background.jpg",
        }
        for source_name, target_name in fixed_copies.items():
            data = archive.read(source_name)
            (fixed / target_name).write_bytes(data)
            report["assets"].append({"source": source_name, "target": f"assets/fixed-pages/{target_name}", "sha256": sha256(data)})

        if len(paths) >= 2:
            slide2_path = paths[1]
            slide2 = xml(archive, slide2_path)
            seen = set()
            for node in slide2.iter():
                rel_id = node.get(f"{{{R}}}embed")
                related = related_part(archive, slide2_path, rel_id) if rel_id else None
                if not related or not related[0].endswith("/image") or not related[1].lower().endswith(".svg"):
                    continue
                part = related[1]
                if part in seen:
                    continue
                seen.add(part)
                data = archive.read(part)
                name = Path(part).name
                target = icons / name
                target.write_bytes(data)
                report["icons"].append({"source": part, "target": f"assets/icons/{name}", "sha256": sha256(data)})

        for index, path in enumerate(paths, 1):
            root = xml(archive, path)
            report["slides"].append(
                {
                    "sourceSlide": index,
                    "text": text_value(root),
                    "objectCounts": object_counts(root),
                    "textRuns": text_runs(root),
                    "textBoxes": [
                        {"text": text_value(shape), "boxOriginalEmu": list(shape_box(shape) or [])}
                        for shape in root.findall(".//p:sp", {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"})
                        if text_value(shape).strip()
                    ],
                }
            )
        report["compatibilityIssues"] = negative_chart_axis_ids(archive)

        if rendered_thanks:
            data = rendered_thanks.read_bytes()
            (fixed / "slide-final-thanks.png").write_bytes(data)
            report["assets"].append(
                {
                    "source": str(rendered_thanks),
                    "target": "assets/fixed-pages/slide-final-thanks.png",
                    "sha256": sha256(data),
                }
            )
        else:
            report["warnings"].append(
                "No rendered final-slide PNG supplied. Render template source slide 13 and pass --rendered-thanks before applying."
            )
    return report


def compare_manifest(report: dict, manifest: dict) -> list[str]:
    errors = []
    if report["sha256"] != manifest["template"]["sha256"]:
        errors.append("Template hash differs from brand-manifest.json; inspect and update the manifest intentionally.")
    actual = {item["target"]: item["sha256"] for item in report["assets"]}
    for item in manifest["backgrounds"]:
        if actual.get(item["file"]) != item["sha256"]:
            errors.append(f"Background hash mismatch: {item['file']}")
    for key, item in manifest["fixedPages"].items():
        target = item.get("file") or item.get("backgroundFile")
        if target and actual.get(target) != item["sha256"]:
            errors.append(f"Fixed page hash mismatch: {key} ({target})")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, help="Persistent staging directory; defaults to a temporary directory")
    parser.add_argument("--rendered-thanks", type=Path, help="Rendered PNG of source template slide 13")
    parser.add_argument("--apply", action="store_true", help="Copy verified staged assets into this Skill")
    args = parser.parse_args()

    template = args.template.expanduser().resolve()
    if not template.is_file() or template.suffix.lower() != ".pptx":
        parser.error("--template must be an existing .pptx file")
    rendered_thanks = args.rendered_thanks.expanduser().resolve() if args.rendered_thanks else None
    if rendered_thanks and (not rendered_thanks.is_file() or rendered_thanks.suffix.lower() != ".png"):
        parser.error("--rendered-thanks must be an existing PNG file")

    if args.output_dir:
        stage = args.output_dir.expanduser().resolve()
        stage.mkdir(parents=True, exist_ok=True)
    else:
        stage = (Path.cwd() / "template-assets-stage").resolve()
        stage.mkdir(parents=True, exist_ok=True)

    report = stage_template(template, stage, rendered_thanks)
    report["manifestErrors"] = compare_manifest(report, load_manifest())
    report_path = stage / "template-extraction-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.apply:
        if report["manifestErrors"] or report["warnings"]:
            parser.error("Refusing --apply while manifest mismatches or warnings remain; inspect the staged report first")
        root = MANIFEST_PATH.parents[1]
        staged_assets = stage / "assets"
        for path in staged_assets.rglob("*"):
            if path.is_file():
                target = root / "assets" / path.relative_to(staged_assets)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)

    print(
        json.dumps(
            {
                "stage": str(stage),
                "report": str(report_path),
                "applied": args.apply,
                "manifestErrors": report["manifestErrors"],
                "warnings": report["warnings"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
