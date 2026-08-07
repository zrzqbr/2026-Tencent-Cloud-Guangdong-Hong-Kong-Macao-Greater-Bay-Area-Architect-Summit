#!/usr/bin/env python3
"""Generate exact-color PPT block assets and a visual reference sheet."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "color-blocks"

BLOCKS = [
    ("01-primary-panel", "#063B64", 235, "Primary content panel"),
    ("02-secondary-panel", "#0A527E", 210, "Secondary grouping panel"),
    ("03-orange-accent", "#FD9D50", 255, "Primary emphasis"),
    ("04-warm-highlight", "#FFE7B9", 255, "Soft highlight"),
    ("05-blue-info", "#4A6FE8", 255, "Information/data accent"),
    ("06-green-status", "#4D9557", 255, "Positive/status accent"),
]


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def font(size: int):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def create_blocks() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, color, alpha, _ in BLOCKS:
        image = Image.new("RGBA", (1200, 360), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        fill = (*hex_rgb(color), alpha)
        draw.rounded_rectangle((8, 8, 1192, 352), radius=16, fill=fill)
        image.save(OUT / f"{name}.png")


def create_reference_sheet() -> None:
    width, height = 1600, 1000
    sheet = Image.new("RGB", (width, height), "#00365F")
    draw = ImageDraw.Draw(sheet)
    title_font = font(52)
    label_font = font(28)
    meta_font = font(22)
    draw.text((90, 58), "GBA Architect Summit / Approved Color Blocks", fill="white", font=title_font)
    draw.text((92, 125), "Exact colors for PowerPoint; layout remains flexible", fill="#FFE7B9", font=meta_font)

    for index, (name, color, alpha, usage) in enumerate(BLOCKS):
        column = index % 2
        row = index // 2
        x = 90 + column * 760
        y = 205 + row * 235
        rgba = (*hex_rgb(color), alpha)
        overlay = Image.new("RGBA", sheet.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle((x, y, x + 650, y + 130), radius=12, fill=rgba)
        sheet = Image.alpha_composite(sheet.convert("RGBA"), overlay)
        draw = ImageDraw.Draw(sheet)
        text_color = "#00365F" if name in {"04-warm-highlight"} else "white"
        draw.text((x + 28, y + 24), name.replace("-", " ").upper(), fill=text_color, font=label_font)
        draw.text((x + 28, y + 75), f"{color}  /  {round(alpha / 255 * 100)}%", fill=text_color, font=meta_font)
        draw.text((x, y + 150), usage, fill="#D8E5EF", font=meta_font)

    draw.rounded_rectangle((90, 900, 1510, 904), radius=2, fill="#FD9D50")
    draw.text((90, 925), "Avoid: purple gradients, glass effects, large rounded cards, random saturated colors.", fill="white", font=meta_font)
    sheet.convert("RGB").save(OUT / "color-block-reference.png", quality=95)


if __name__ == "__main__":
    create_blocks()
    create_reference_sheet()
