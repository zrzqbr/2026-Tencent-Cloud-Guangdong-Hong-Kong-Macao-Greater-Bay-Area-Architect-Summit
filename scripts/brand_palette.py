#!/usr/bin/env python3
"""Query and validate the summit palette without opening a presentation."""

from __future__ import annotations

import argparse
import json
import re
import sys

from brand_core import delta_e, hex_rgb, load_manifest, nearest_palette_color


def allowed_colors(manifest: dict) -> list[str]:
    palette = manifest["palette"]
    values = set(palette["allowedText"] + palette["chartSeries"] + palette["deepNavy"])
    values.update(block["color"] for block in palette["colorBlocks"])
    return sorted(values)


def validate_color(value: str, manifest: dict, threshold: float = 8.0) -> dict:
    normalized = value.upper().lstrip("#")
    if not re.fullmatch(r"[0-9A-F]{6}", normalized):
        return {"safe": False, "color": value, "reason": "Expected #RRGGBB"}
    allowed = allowed_colors(manifest)
    if normalized in allowed:
        return {"safe": True, "color": f"#{normalized}", "reason": "Exact approved color"}
    nearest = nearest_palette_color(normalized, allowed)
    safe = nearest["deltaE"] <= threshold
    reason = (
        f"Near approved #{nearest['to']} (CIEDE2000 ΔE={nearest['deltaE']})"
        if safe
        else f"Outside approved palette; nearest #{nearest['to']} (CIEDE2000 ΔE={nearest['deltaE']})"
    )
    return {"safe": safe, "color": f"#{normalized}", "reason": reason, "nearest": nearest}


def prompt_snippet(manifest: dict) -> str:
    palette = manifest["palette"]
    return "\n".join(
        [
            "2026 腾讯云粤港澳大湾区架构师峰会品牌约束：",
            f"- 标题、章节标题、主题短语：腾讯体 W7，#{palette['title']}。",
            f"- 中文/英文说明正文：腾讯体 W3，#{palette['body']}。",
            f"- 图表系列优先顺序：{' -> '.join('#' + color for color in palette['chartSeries'])}。",
            "- 只使用 brand-manifest.json 中批准的背景、色块和 Logo 禁入区。",
            "- 第 4 页以后不限制卡片、图表、流程、分栏或其他结构；结构必须服务内容。",
            "- 不添加独立峰会 Logo；官方标识已经烘焙在批准背景中。",
            "- 字体替换后必须重新渲染并修复重叠、换行、裁切和溢出。",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt", action="store_true", help="Print a prompt snippet for a companion PPT Skill")
    group.add_argument("--validate", metavar="#RRGGBB", help="Validate one color")
    group.add_argument("--nearest", metavar="#RRGGBB", help="Find the nearest approved color")
    group.add_argument("--chart", action="store_true", help="Print the approved chart sequence")
    group.add_argument("--list", action="store_true", help="Print the complete machine palette")
    parser.add_argument("--json", action="store_true", help="Emit JSON where applicable")
    args = parser.parse_args()

    manifest = load_manifest()
    palette = manifest["palette"]
    if args.prompt:
        print(prompt_snippet(manifest))
        return
    if args.validate:
        result = validate_color(args.validate, manifest)
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result["reason"])
        raise SystemExit(0 if result["safe"] else 1)
    if args.nearest:
        value = args.nearest.upper().lstrip("#")
        if not re.fullmatch(r"[0-9A-F]{6}", value):
            parser.error("--nearest expects #RRGGBB")
        result = nearest_palette_color(value, allowed_colors(manifest))
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"#{result['to']} (ΔE={result['deltaE']})")
        return
    if args.chart:
        result = [f"#{color}" for color in palette["chartSeries"]]
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else " -> ".join(result))
        return
    result = {
        "text": [f"#{color}" for color in palette["allowedText"]],
        "chart": [f"#{color}" for color in palette["chartSeries"]],
        "blocks": palette["colorBlocks"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
