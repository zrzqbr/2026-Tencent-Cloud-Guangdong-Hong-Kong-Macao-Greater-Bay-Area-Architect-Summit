#!/usr/bin/env python3
"""Render a PPTX with preview-only Tencent-font aliases for visual QA."""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


FONT_FALLBACKS = [
    "Arial Unicode MS",
    "PingFang SC",
    "Microsoft YaHei",
    "Noto Sans CJK SC",
    "WenQuanYi Micro Hei",
]


def resolve_soffice(value: str | None) -> Path:
    candidates = []
    if value:
        candidates.append(Path(value).expanduser())
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    candidates.append(Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise SystemExit(
        "LibreOffice was not found. Pass --soffice with the binary or the companion PPT skill's "
        "scripts/office/soffice.py wrapper."
    )


def write_fontconfig(path: Path, cache: Path) -> None:
    font_dirs = [
        Path("/System/Library/Fonts"),
        Path("/System/Library/Fonts/Supplemental"),
        Path("/Library/Fonts"),
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
    ]
    dirs = "\n".join(f"  <dir>{item}</dir>" for item in font_dirs if item.exists())
    aliases = []
    for tencent_font in ("腾讯体 W7", "腾讯体 W3"):
        families = "\n".join(f"      <string>{name}</string>" for name in FONT_FALLBACKS)
        aliases.append(
            "  <match target=\"pattern\">\n"
            f"    <test name=\"family\"><string>{tencent_font}</string></test>\n"
            "    <edit name=\"family\" mode=\"prepend\">\n"
            f"{families}\n"
            "    </edit>\n"
            "  </match>"
        )
    path.write_text(
        "<?xml version=\"1.0\"?>\n"
        "<!DOCTYPE fontconfig SYSTEM \"fonts.dtd\">\n"
        "<fontconfig>\n"
        f"{dirs}\n"
        f"  <cachedir>{cache}</cachedir>\n"
        + "\n".join(aliases)
        + "\n  <config></config>\n</fontconfig>\n",
        encoding="utf-8",
    )


def run_checked(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise SystemExit(f"Command failed ({result.returncode}): {' '.join(command)}\n{detail}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--soffice", help="LibreOffice binary or companion soffice.py wrapper")
    parser.add_argument("--dpi", type=int, default=150)
    args = parser.parse_args()

    deck = args.pptx.expanduser().resolve()
    if not deck.is_file():
        raise SystemExit(f"PPTX not found: {deck}")
    output = (args.output_dir or deck.with_name(f"{deck.stem}-render")).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    soffice = resolve_soffice(args.soffice)
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise SystemExit("pdftoppm was not found; install Poppler or use the companion PPT skill's renderer.")

    with tempfile.TemporaryDirectory(prefix="gba-slide-render-") as temp_name:
        temp = Path(temp_name)
        fontconfig = temp / "fonts.conf"
        write_fontconfig(fontconfig, temp / "font-cache")
        env = os.environ.copy()
        env["FONTCONFIG_FILE"] = str(fontconfig)
        command = [str(soffice), "--headless", "--convert-to", "pdf", "--outdir", str(output), str(deck)]
        if soffice.suffix == ".py":
            command.insert(0, sys.executable)
        run_checked(command, cwd=output, env=env)

    pdf = output / f"{deck.stem}.pdf"
    if not pdf.is_file():
        raise SystemExit(f"Renderer completed but PDF was not created: {pdf}")
    run_checked(
        [pdftoppm, "-jpeg", "-r", str(args.dpi), str(pdf), str(output / "slide")],
        cwd=output,
    )
    slide_count = len(list(output.glob("slide-*.jpg")))
    if not slide_count:
        raise SystemExit("PDF conversion completed but no slide images were created")
    print(f"Rendered {slide_count} slides to {output}")
    print("Preview aliases do not modify the PPTX; keep exact Tencent font names in the delivered deck.")


if __name__ == "__main__":
    main()
