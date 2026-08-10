#!/usr/bin/env python3
"""Regression tests for the summit template Skill."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
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
from safe_repair_deck import normalized_contrast_rules, repair_slide_xml  # noqa: E402
from summit_adapter import build_mapping, ledger_stub  # noqa: E402
from validate_deck_brand import asset_errors, check_large_foreground_panels, migration_review_errors  # noqa: E402
from validate_element_migration import apply_approved_text_changes, expected_counts  # noqa: E402


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
        self.assertEqual(self.manifest["schemaVersion"], 3)
        self.assertEqual(self.manifest["palette"]["darkText"], ["00365F", "111111", "000000"])

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
        self.assertEqual(ledger["schemaVersion"], 3)
        self.assertEqual(len(ledger["slides"]), 2)
        self.assertIsNone(ledger["slides"][0]["after"])
        self.assertEqual(
            ledger["slides"][0]["visualReview"],
            {
                "renderedAtFullSize": None,
                "surfaceContrastReviewed": None,
                "textBackingShapesAdded": None,
                "status": "pending",
                "notes": [],
            },
        )

    def test_contrast_map_is_explicit_and_palette_limited(self) -> None:
        rules = normalized_contrast_rules(
            {
                "shapeColors": {15: "#00365F"},
                "tableTextColors": {1: "111111"},
                "tableCellTextColors": {1: {"1,1": "FFFFFF", "2,1": "000000"}},
                "tableTextColor": "000000",
            },
            self.manifest,
        )
        self.assertEqual(rules["shapeColors"], {"15": "00365F"})
        self.assertEqual(rules["tableTextColors"], {"1": "111111"})
        self.assertEqual(rules["tableCellTextColors"], {"1": {"1,1": "FFFFFF", "2,1": "000000"}})
        with self.assertRaises(ValueError):
            normalized_contrast_rules({"shapeColors": {15: "FF00FF"}}, self.manifest)

    def test_schema_three_visual_review_is_a_release_gate(self) -> None:
        pending = {
            "schemaVersion": 3,
            "slides": [
                {
                    "visualReview": {
                        "renderedAtFullSize": None,
                        "surfaceContrastReviewed": None,
                        "textBackingShapesAdded": None,
                        "status": "pending",
                    }
                }
            ],
        }
        passed = {
            "schemaVersion": 3,
            "slides": [
                {
                    "visualReview": {
                        "renderedAtFullSize": True,
                        "surfaceContrastReviewed": True,
                        "textBackingShapesAdded": 0,
                        "status": "passed",
                    }
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "ledger.json"
            path.write_text(json.dumps(pending), encoding="utf-8")
            self.assertEqual(len(migration_review_errors(path)), 4)
            path.write_text(json.dumps(passed), encoding="utf-8")
            self.assertEqual(migration_review_errors(path), [])

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
        self.assertEqual([(item["sourcePages"], item["destinationSlides"]) for item in body], [([1], [4]), ([4], [5])])
        self.assertIn("precedes the detected title", body[0]["note"])
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

    def test_declared_text_changes_are_applied_exactly(self) -> None:
        value, errors = apply_approved_text_changes("原始文本2026", [{"before": "原始文本", "after": "修订文本"}])
        self.assertEqual(value, "修订文本2026")
        self.assertEqual(errors, [])
        value, errors = apply_approved_text_changes("原始文本", [{"reason": "missing before/after"}])
        self.assertEqual(value, "原始文本")
        self.assertTrue(errors)

    def test_large_filled_foreground_panel_is_rejected(self) -> None:
        root = ET.fromstring(
            f'''<p:sld xmlns:p="{NS['p']}" xmlns:a="{NS['a']}">
            <p:cSld><p:spTree><p:sp>
              <p:nvSpPr><p:cNvPr id="7" name="bad overlay"/></p:nvSpPr>
              <p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="11000000" cy="6000000"/></a:xfrm><a:solidFill><a:srgbClr val="063B64"/></a:solidFill></p:spPr>
            </p:sp></p:spTree></p:cSld></p:sld>'''
        )
        errors = []
        check_large_foreground_panels(errors, 4, root, tuple(self.manifest["canvas"]["standardEmu"]), self.manifest)
        self.assertEqual(len(errors), 1)
        self.assertIn("large dark foreground shape", errors[0])
        root.find(".//a:srgbClr", NS).set("val", "000000")
        errors = []
        check_large_foreground_panels(errors, 4, root, tuple(self.manifest["canvas"]["standardEmu"]), self.manifest)
        self.assertEqual(len(errors), 1)
        root.find(".//a:srgbClr", NS).set("val", "FFFFFF")
        errors = []
        check_large_foreground_panels(errors, 4, root, tuple(self.manifest["canvas"]["standardEmu"]), self.manifest)
        self.assertEqual(errors, [])

    def test_layout_background_does_not_hide_local_full_slide_overlay(self) -> None:
        root = ET.fromstring(
            f'''<p:sld xmlns:p="{NS['p']}" xmlns:a="{NS['a']}"><p:cSld><p:spTree><p:pic>
            <p:nvPicPr><p:cNvPr id="8" name="overlay"/></p:nvPicPr>
            <p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="12192000" cy="6858000"/></a:xfrm></p:spPr>
            </p:pic></p:spTree></p:cSld></p:sld>'''
        )
        errors = []
        check_large_foreground_panels(
            errors,
            4,
            root,
            tuple(self.manifest["canvas"]["standardEmu"]),
            self.manifest,
            {"kind": "layout-background-fill"},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("non-background picture", errors[0])
        errors = []
        check_large_foreground_panels(
            errors,
            4,
            root,
            tuple(self.manifest["canvas"]["standardEmu"]),
            self.manifest,
            {"kind": "picture"},
        )
        self.assertEqual(errors, [])

    def test_large_grouped_dark_field_is_rejected(self) -> None:
        root = ET.fromstring(
            f'''<p:sld xmlns:p="{NS['p']}" xmlns:a="{NS['a']}"><p:cSld><p:spTree><p:grpSp>
            <p:nvGrpSpPr><p:cNvPr id="9" name="grouped overlay"/></p:nvGrpSpPr>
            <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="11000000" cy="6000000"/><a:chOff x="0" y="0"/><a:chExt cx="11000000" cy="6000000"/></a:xfrm></p:grpSpPr>
            <p:sp><p:nvSpPr><p:cNvPr id="10" name="dark child"/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="11000000" cy="6000000"/></a:xfrm><a:solidFill><a:srgbClr val="063B64"/></a:solidFill></p:spPr></p:sp>
            </p:grpSp></p:spTree></p:cSld></p:sld>'''
        )
        errors = []
        check_large_foreground_panels(errors, 4, root, tuple(self.manifest["canvas"]["standardEmu"]), self.manifest)
        self.assertEqual(len(errors), 1)
        self.assertIn("grouped dark foreground", errors[0])
        child_extent = root.find(".//p:sp/p:spPr/a:xfrm/a:ext", NS)
        child_extent.set("cx", "500000")
        child_extent.set("cy", "300000")
        errors = []
        check_large_foreground_panels(errors, 4, root, tuple(self.manifest["canvas"]["standardEmu"]), self.manifest)
        self.assertEqual(errors, [])

    def test_safe_repair_supports_mixed_table_cell_surfaces(self) -> None:
        source = f'''<p:sld xmlns:p="{NS['p']}" xmlns:a="{NS['a']}">
        <p:cSld><p:spTree><p:graphicFrame><a:graphic><a:graphicData><a:tbl><a:tr>
          <a:tc><a:txBody><a:p><a:r><a:t>light-card text</a:t></a:r></a:p></a:txBody></a:tc>
          <a:tc><a:txBody><a:p><a:r><a:t>dark-card text</a:t></a:r></a:p></a:txBody></a:tc>
        </a:tr></a:tbl></a:graphicData></a:graphic></p:graphicFrame></p:spTree></p:cSld></p:sld>'''.encode()
        repaired, report = repair_slide_xml(
            source,
            4,
            self.manifest,
            tuple(self.manifest["canvas"]["standardEmu"]),
            {"tableCellTextColors": {"1": {"1,1": "111111", "1,2": "FFFFFF"}}},
        )
        root = ET.fromstring(repaired)
        colors = [node.get("val") for node in root.findall(".//a:rPr/a:solidFill/a:srgbClr", NS)]
        self.assertEqual(colors, ["111111", "FFFFFF"])
        self.assertEqual(report["tableRunsVisited"], 2)
        for props in root.findall(".//a:rPr", NS):
            self.assertEqual({props.find(f"./a:{tag}", NS).get("typeface") for tag in ("latin", "ea", "cs")}, {"腾讯体 W3"})

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
