# Tencent Font Handling

The canonical template embeds Tencent font parts for portability, but embedded fonts are not standalone redistributable font files.

- Prefer editing from `assets/0815-architect-summit-template.pptx` when embedded-font portability matters.
- Set every delivered text run's Latin, East Asian, and complex-script font fields explicitly to `腾讯体 W7` or `腾讯体 W3`.
- Do not extract, copy, or redistribute proprietary font binaries from other repositories or Office packages.
- When the presentation machine has licensed Tencent fonts, install them through the organization's approved font distribution path.
- Use `scripts/render_deck_preview.py` only when a local LibreOffice preview cannot render Tencent-font Chinese. Its fallbacks are preview-only and must not alter the delivered PPTX.
- Font assignment changes line metrics. Always rerender after font changes and repair overlaps, clipping, line breaks, and undersized text.

Use PowerPoint or WPS for the final venue-machine check when possible because LibreOffice, PowerPoint, and WPS can measure the same embedded font differently.
