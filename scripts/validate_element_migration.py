#!/usr/bin/env python3
"""Validate element-level fidelity for one-to-one, split, or merged PPTX migrations."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

from brand_core import (
    normalized_text,
    object_counts,
    package_path,
    part_rels_name,
    rel_map,
    slide_paths,
    xml,
)


COUNT_KEYS = ("shapes", "connectors", "images", "tables", "charts")
TYPE_TO_KEY = {
    "shape": "shapes",
    "connector": "connectors",
    "image": "images",
    "table": "tables",
    "chart": "charts",
}


def normalized_counts(value: dict | None) -> dict[str, int]:
    source = value or {}
    result = {key: int(source.get(key, 0)) for key in COUNT_KEYS}
    if "connectors" not in source and "shapes" in source:
        result["connectors"] = 0
    return result


def add_counts(first: dict[str, int], second: dict[str, int]) -> dict[str, int]:
    return {key: first[key] + second[key] for key in COUNT_KEYS}


def aggregate_counts(archive: zipfile.ZipFile, paths: list[str], pages: list[int]) -> dict[str, int]:
    total = {key: 0 for key in COUNT_KEYS}
    for page in pages:
        total = add_counts(total, normalized_counts(object_counts(xml(archive, paths[page - 1]))))
    return total


def aggregate_text(archive: zipfile.ZipFile, paths: list[str], pages: list[int]) -> str:
    return "".join(normalized_text(xml(archive, paths[page - 1])) for page in pages)


def list_value(entry: dict, plural: str, singular: str) -> list[int]:
    value = entry.get(plural)
    if value is None and singular in entry:
        value = [entry[singular]]
    if not isinstance(value, list) or not value:
        raise ValueError(f"Ledger entry requires non-empty {plural}")
    return [int(item) for item in value]


def expected_counts(before: dict, deleted: list[dict], added: list[dict], rasterized: list[dict]) -> dict[str, int]:
    expected = normalized_counts(before)
    for item in deleted:
        key = TYPE_TO_KEY.get(item.get("type"))
        if key:
            expected[key] -= 1
    for item in added:
        key = TYPE_TO_KEY.get(item.get("type"))
        if key:
            expected[key] += 1
    for item in rasterized:
        source_key = TYPE_TO_KEY.get(item.get("sourceType") or item.get("type"))
        if source_key and source_key != "images":
            expected[source_key] -= 1
            expected["images"] += 1
    return expected


def notes_text(archive: zipfile.ZipFile, slide_path: str) -> str:
    rels = rel_map(archive, part_rels_name(slide_path))
    for rel_type, target in rels.values():
        if rel_type.endswith("/notesSlide"):
            notes_path = package_path(str(Path(slide_path).parent).replace("\\", "/"), target)
            return normalized_text(xml(archive, notes_path))
    return ""


def hyperlink_targets(archive: zipfile.ZipFile, slide_path: str) -> list[str]:
    return sorted(target for rel_type, target in rel_map(archive, part_rels_name(slide_path)).values() if rel_type.endswith("/hyperlink"))


def apply_approved_text_changes(source_text: str, changes: list[dict]) -> tuple[str, list[str]]:
    value = source_text
    errors = []
    for index, item in enumerate(changes, 1):
        if not isinstance(item, dict):
            errors.append(f"approvedTextChanges item {index} must be an object with before/after")
            continue
        before = re.sub(r"\s+", "", str(item.get("before", "")))
        after = re.sub(r"\s+", "", str(item.get("after", "")))
        if not before:
            errors.append(f"approvedTextChanges item {index} requires nonempty before text")
            continue
        if before not in value:
            errors.append(f"approvedTextChanges item {index} before text does not occur in the source")
            continue
        value = value.replace(before, after, 1)
    return value, errors


def expected_source_pages(ledger: dict, migration_map_path: Path | None) -> set[int]:
    explicit = ledger.get("expectedSourcePages")
    if explicit:
        return {int(item) for item in explicit}
    if migration_map_path:
        mapping = json.loads(migration_map_path.read_text(encoding="utf-8"))
        pages = set()
        for item in mapping.get("mappings", []):
            if item.get("mode") == "element-level-migration":
                pages.update(int(page) for page in item.get("sourcePages", []))
        return pages
    pages = set()
    for entry in ledger.get("slides", []):
        pages.update(list_value(entry, "sourcePages", "sourcePage"))
    return pages


def validate(source: Path, destination: Path, ledger_path: Path, migration_map_path: Path | None = None) -> list[str]:
    errors = []
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    entries = ledger.get("slides", [])
    if not entries:
        return ["Ledger contains no migrated slide entries"]
    expected_pages = expected_source_pages(ledger, migration_map_path)
    require_visual_review = int(ledger.get("schemaVersion", 1)) >= 3
    covered_pages = set()
    try:
        with zipfile.ZipFile(source) as src, zipfile.ZipFile(destination) as dst:
            _, src_paths = slide_paths(src)
            _, dst_paths = slide_paths(dst)
            for entry_index, entry in enumerate(entries, 1):
                if require_visual_review:
                    review = entry.get("visualReview") or {}
                    if review.get("renderedAtFullSize") is not True:
                        errors.append(f"Ledger entry {entry_index} full-size rendered review is unresolved")
                    if review.get("surfaceContrastReviewed") is not True:
                        errors.append(f"Ledger entry {entry_index} surface-contrast review is unresolved")
                    if review.get("textBackingShapesAdded") != 0:
                        errors.append(f"Ledger entry {entry_index} must add zero readability-only text backing shapes")
                    if review.get("status") != "passed":
                        errors.append(f"Ledger entry {entry_index} visual review status must be 'passed'")
                    if entry.get("notesPreserved") is not True:
                        errors.append(f"Ledger entry {entry_index} notesPreserved must be true after comparison, including when both sides have no notes")
                    if entry.get("hyperlinksPreserved") is not True:
                        errors.append(f"Ledger entry {entry_index} hyperlinksPreserved must be true after target comparison, including when both sides have no links")
                try:
                    source_pages = list_value(entry, "sourcePages", "sourcePage")
                    destination_slides = list_value(entry, "destinationSlides", "destinationSlide")
                except (TypeError, ValueError) as exc:
                    errors.append(f"Ledger entry {entry_index}: {exc}")
                    continue
                covered_pages.update(source_pages)
                if any(page < 1 or page > len(src_paths) for page in source_pages):
                    errors.append(f"Ledger entry {entry_index} source pages point outside the source deck: {source_pages}")
                    continue
                if any(page < 1 or page > len(dst_paths) for page in destination_slides):
                    errors.append(f"Ledger entry {entry_index} destination slides point outside the destination deck: {destination_slides}")
                    continue

                src_counts = aggregate_counts(src, src_paths, source_pages)
                dst_counts = aggregate_counts(dst, dst_paths, destination_slides)
                before = normalized_counts(entry.get("before"))
                after_value = entry.get("after")
                if after_value is None:
                    errors.append(f"Ledger entry {entry_index} is still a stub: after is null")
                    continue
                after = normalized_counts(after_value)
                expected = expected_counts(
                    before,
                    entry.get("deleted", []),
                    entry.get("addedBrandElements", []),
                    entry.get("rasterizedElements", []),
                )
                if src_counts != before:
                    errors.append(f"Source pages {source_pages} counts differ from ledger: XML {src_counts}, ledger {before}")
                if any(value < 0 for value in expected.values()):
                    errors.append(f"Source pages {source_pages} ledger arithmetic produces a negative count: {expected}")
                if expected != after:
                    errors.append(f"Source pages {source_pages} ledger arithmetic is inconsistent: expected {expected}, ledger after {after}")
                if dst_counts != after:
                    errors.append(f"Destination slides {destination_slides} counts differ from ledger: XML {dst_counts}, ledger {after}")

                src_text = aggregate_text(src, src_paths, source_pages)
                dst_text = aggregate_text(dst, dst_paths, destination_slides)
                allowed_text_changes = entry.get("approvedTextChanges", [])
                expected_text, change_errors = apply_approved_text_changes(src_text, allowed_text_changes)
                errors.extend(f"Ledger entry {entry_index} {message}" for message in change_errors)
                if expected_text != dst_text:
                    errors.append(f"Source pages {source_pages} visible text does not match destination slides {destination_slides} after declared text changes")

                source_objects = sum(src_counts.values())
                destination_objects = sum(dst_counts.values()) - len(entry.get("addedBrandElements", []))
                if source_objects >= 3 and dst_counts["images"] == 1 and destination_objects <= 2 and not entry.get("rasterizedElements"):
                    errors.append(f"Destination slides {destination_slides} appear collapsed into a body image")
                image_growth = dst_counts["images"] - src_counts["images"]
                explained_images = sum(1 for item in entry.get("addedBrandElements", []) if item.get("type") == "image")
                explained_images += sum(1 for item in entry.get("rasterizedElements", []) if (item.get("sourceType") or item.get("type")) != "image")
                if image_growth > explained_images:
                    errors.append(f"Destination slides {destination_slides} add {image_growth - explained_images} unexplained image objects")

                if entry.get("notesPreserved") is True:
                    source_notes = "".join(notes_text(src, src_paths[page - 1]) for page in source_pages)
                    destination_notes = "".join(notes_text(dst, dst_paths[page - 1]) for page in destination_slides)
                    if source_notes != destination_notes:
                        errors.append(f"Source pages {source_pages} notes do not match destination slides {destination_slides}")
                if entry.get("hyperlinksPreserved") is True:
                    source_links = sorted(target for page in source_pages for target in hyperlink_targets(src, src_paths[page - 1]))
                    destination_links = sorted(target for page in destination_slides for target in hyperlink_targets(dst, dst_paths[page - 1]))
                    if source_links != destination_links:
                        errors.append(f"Source pages {source_pages} hyperlink targets {source_links} differ from destination {destination_links}")
    except (FileNotFoundError, zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
        return [f"Cannot validate migration packages: {exc}"]

    missing = expected_pages - covered_pages
    extra = covered_pages - expected_pages
    if missing:
        errors.append(f"Ledger does not account for mapped source pages: {sorted(missing)}")
    if extra:
        errors.append(f"Ledger contains source pages not declared for element migration: {sorted(extra)}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--migration-map", type=Path, help="Optional map used to derive required source-page coverage")
    args = parser.parse_args()
    errors = validate(
        args.source.expanduser().resolve(),
        args.destination.expanduser().resolve(),
        args.ledger.expanduser().resolve(),
        args.migration_map.expanduser().resolve() if args.migration_map else None,
    )
    if errors:
        print("Element migration validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("Element migration validation passed: mapped text, object counts, editability, declared notes/hyperlinks, and required visual-review records are complete.")


if __name__ == "__main__":
    main()
