#!/usr/bin/env python3
"""Regression tests for the summit template Skill."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from brand_core import (  # noqa: E402
    NS,
    delta_e,
    hex_rgb,
    load_manifest,
    negative_chart_axis_ids,
    nearest_palette_color,
    sha256,
    shape_box,
    slide_paths,
    text_value,
    xml,
)
from brand_palette import validate_color  # noqa: E402
from summit_adapter import build_mapping, ledger_stub  # noqa: E402
from validate_deck_brand import asset_errors  # noqa: E402
from validate_element_migration import expected_counts  # noqa: E402


class SkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_manifest()
        cls.template = ROOT / cls.manifest["template"]["file"]

    def test_manifest_and_assets_match(self) -> None:
        self.assertEqual(sha256(self.template), self.manifest["template"]["sha256"])
        self.assertEqual(asset_errors(self.manifest), [])
        icons = list((ROOT / "assets" / "icons").glob("*.svg"))
        self.assertEqual(len(icons), self.manifest["template"]["assetLibrary"]["extractedSvgCount"])
        self.assertEqual(self.manifest["capabilities"]["fixedOpeningDestinationSlides"], [1, 2, 3])
        self.assertEqual(self.manifest["capabilities"]["bodyContentStartsAtDestinationSlide"], 4)
        self.assertFalse(self.manifest["fixedPages"]["title"]["structureMutable"])
        self.assertFalse(self.manifest["fixedPages"]["speaker"]["structureMutable"])

    def test_color_distance_and_palette(self) -> None:
        orange = hex_rgb("FD9D50")
        self.assertAlmostEqual(delta_e(orange, orange), 0.0, places=8)
        first = delta_e(hex_rgb("FD9D50"), hex_rgb("4A6FE8"))
        second = delta_e(hex_rgb("4A6FE8"), hex_rgb("FD9D50"))
        self.assertAlmostEqual(first, second, places=8)
        nearest = nearest_palette_color("FE9D50", ["FD9D50", "4A6FE8", "4D9557"])
        self.assertEqual(nearest["to"], "FD9D50")
        self.assertTrue(validate_color("#FD9D50", self.manifest)["safe"])
        self.assertFalse(validate_color("#FF00FF", self.manifest)["safe"])

    def test_template_mapping_geometry_and_axis_warning(self) -> None:
        with zipfile.ZipFile(self.template) as archive:
            _, paths = slide_paths(archive)
            self.assertEqual(len(paths), self.manifest["template"]["sourceSlideCount"])
            title_root = xml(archive, paths[self.manifest["template"]["sourceSlideRoles"]["talkTitle"] - 1])
            title_boxes = {
                shape_box(shape)
                for shape in title_root.findall(".//p:sp", NS)
                if text_value(shape).strip()
            }
            for field in self.manifest["fixedPages"]["title"]["fields"]:
                self.assertIn(tuple(field["boxOriginalEmu"]), title_boxes)

            speaker_root = xml(archive, paths[self.manifest["template"]["sourceSlideRoles"]["speaker"] - 1])
            speaker_boxes = {
                shape_box(shape)
                for shape in speaker_root.findall(".//p:sp", NS)
                if text_value(shape).strip()
            }
            for field in self.manifest["fixedPages"]["speaker"]["fields"]:
                if "font" in field:
                    self.assertIn(tuple(field["boxOriginalEmu"]), speaker_boxes)

            values = {item["value"] for item in negative_chart_axis_ids(archive)}
            self.assertEqual(values, {-756365072, -756369360})

    def test_generic_mapping_and_ledger(self) -> None:
        intake = {
            "slides": [
                {"sourcePage": 1, "classification": "source-opening-or-title", "objectCounts": {"shapes": 2, "connectors": 0, "images": 1, "tables": 0, "charts": 0}},
                {"sourcePage": 2, "classification": "speaker-profile-candidate", "objectCounts": {"shapes": 3, "connectors": 0, "images": 1, "tables": 0, "charts": 0}},
                {"sourcePage": 3, "classification": "content", "objectCounts": {"shapes": 5, "connectors": 1, "images": 2, "tables": 0, "charts": 0}},
                {"sourcePage": 4, "classification": "conclusion-candidate", "objectCounts": {"shapes": 2, "connectors": 0, "images": 0, "tables": 0, "charts": 0}},
            ]
        }
        mapping = build_mapping(intake, self.manifest)
        self.assertEqual(mapping["excludedTemplateSlides"], [2])
        self.assertEqual(mapping["fixedOpeningSequence"], [1, 2, 3])
        self.assertEqual(mapping["bodyContentStartsAtDestinationSlide"], 4)
        self.assertEqual(mapping["mappings"][0]["destinationSlides"], [1])
        self.assertEqual(mapping["mappings"][1]["destinationSlides"], [2])
        self.assertEqual(mapping["mappings"][2]["destinationSlides"], [3])
        body = [item for item in mapping["mappings"] if item["mode"] == "element-level-migration"]
        self.assertEqual([item["destinationSlides"][0] for item in body], [4, 5])
        ledger = ledger_stub(intake, mapping)
        self.assertEqual(len(ledger["slides"]), 2)
        self.assertIsNone(ledger["slides"][0]["after"])

    def test_existing_canonical_opening_and_final_are_preserved(self) -> None:
        intake = {
            "canonicalOpeningSequence": True,
            "canonicalFinalThankYou": True,
            "slides": [
                {"sourcePage": 1, "classification": "source-opening-or-title", "objectCounts": {}},
                {"sourcePage": 2, "classification": "section-divider-candidate", "objectCounts": {}},
                {"sourcePage": 3, "classification": "speaker-profile-candidate", "objectCounts": {}},
                {"sourcePage": 4, "classification": "content", "objectCounts": {"shapes": 2}},
                {"sourcePage": 5, "classification": "conclusion-candidate", "objectCounts": {}},
            ],
        }
        mapping = build_mapping(intake, self.manifest)
        self.assertEqual(mapping["mappings"][0]["mode"], "preserve-canonical-opening-sequence")
        body = [item for item in mapping["mappings"] if item["mode"] == "element-level-migration"]
        self.assertEqual(body[0]["sourcePages"], [4])
        self.assertEqual(body[0]["destinationSlides"], [4])
        self.assertEqual(mapping["mappings"][-1]["mode"], "preserve-canonical-final-thanks")

    def test_legacy_opening_roles_map_before_body(self) -> None:
        intake = {
            "sourceFinalThankYouCandidate": True,
            "slides": [
                {"sourcePage": 1, "classification": "source-opening-or-title", "visibleText": "", "objectCounts": {"images": 1}},
                {"sourcePage": 2, "classification": "section-divider-candidate", "visibleText": "技术主题主讲人：", "objectCounts": {"shapes": 3, "images": 1}},
                {"sourcePage": 3, "classification": "section-divider-candidate", "visibleText": "", "objectCounts": {"images": 1}},
                {"sourcePage": 4, "classification": "content", "visibleText": "正文第一页", "objectCounts": {"shapes": 2}},
                {"sourcePage": 5, "classification": "conclusion-candidate", "visibleText": "THANKS", "objectCounts": {"images": 1}},
            ],
        }
        mapping = build_mapping(intake, self.manifest)
        self.assertEqual(mapping["mappings"][1]["sourcePages"], [2])
        self.assertEqual(mapping["mappings"][1]["destinationSlides"], [2])
        self.assertEqual(mapping["mappings"][2]["sourcePages"], [3])
        body = [item for item in mapping["mappings"] if item["mode"] == "element-level-migration"]
        self.assertEqual([(item["sourcePages"], item["destinationSlides"]) for item in body], [([4], [4])])
        self.assertEqual(mapping["mappings"][-1]["sourcePages"], [5])
        self.assertEqual(mapping["mappings"][-1]["mode"], "replace-source-thanks-with-canonical-final-thanks")

    def test_ledger_arithmetic_supports_rasterization(self) -> None:
        before = {"shapes": 3, "connectors": 1, "images": 0, "tables": 0, "charts": 0}
        result = expected_counts(
            before,
            deleted=[{"type": "shape"}],
            added=[{"type": "shape"}],
            rasterized=[{"sourceType": "connector"}],
        )
        self.assertEqual(result, {"shapes": 3, "connectors": 0, "images": 1, "tables": 0, "charts": 0})

    def test_adapter_cli_writes_all_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "summit_adapter.py"),
                    "--source",
                    str(self.template),
                    "--output-dir",
                    temp_dir,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            summary = json.loads(result.stdout)
            for name in ("adapter-report.json", "migration-map.json", "element-migration-ledger.json", "companion-instructions.md"):
                self.assertTrue((Path(temp_dir) / name).is_file())
            self.assertEqual(Path(summary["report"]).name, "adapter-report.json")
            mapping = json.loads((Path(temp_dir) / "migration-map.json").read_text(encoding="utf-8"))
            self.assertEqual(mapping["mappings"][0], {"sourcePages": [1], "destinationSlides": [1], "mode": "preserve-canonical-cover"})
            self.assertEqual(mapping["mappings"][1]["sourcePages"], [3])
            self.assertEqual(mapping["mappings"][2]["sourcePages"], [4])
            self.assertEqual(mapping["mappings"][-1]["sourcePages"], [13])


if __name__ == "__main__":
    unittest.main(verbosity=2)
