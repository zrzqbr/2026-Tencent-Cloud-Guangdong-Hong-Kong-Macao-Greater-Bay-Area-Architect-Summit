---
name: create-gba-architect-summit-slides
description: "Apply the official 2026 Tencent Cloud Guangdong-Hong Kong-Macao Greater Bay Area Architect Summit PowerPoint template as a reusable brand, migration, typography-safety, repair, and validation layer. This is not a standalone PPT generator: pair it with a presentation-authoring Skill, plugin, or tool. Use it to create, migrate, adapt, audit, or validate summit decks while enforcing the canonical output slides 1-3, fixed final thank-you slide, approved logo-bearing backgrounds, Tencent W7/W3 fonts, text colors, color blocks, editable element migration, and anti-overlap release checks. Keep content structures flexible after slide 3. Supports PPT/PPTX/PDF/HTML/Markdown intake."
---

# 2026 GBA Architect Summit PPT Template

This is the template, brand, migration, and release-gate layer for the 2026 Tencent Cloud Guangdong-Hong Kong-Macao Greater Bay Area Architect Summit. It does not independently research a topic, create an outline, choose the narrative, design every content slide, or export a complete PPTX.

Pair it with the user's preferred presentation-authoring Skill/tool. The companion owns content and slide construction; this Skill owns summit identity, migration rules, safe repairs, and acceptance checks.

## Required Boundary

- Do not present this Skill as a standalone PPT generator.
- Do not force the sample template's cards, circles, columns, chart treatment, or layouts after slide 3.
- Do not invent speaker details, portraits, claims, data, citations, or Logos.
- Do not flatten an editable source PPTX into slide screenshots.
- Do not overwrite a source deck during repair or migration.

## Start Here

1. Identify the companion presentation-authoring/reading tool.
2. Read [references/template-contract.md](references/template-contract.md). It overrides all general guidance.
3. Read [references/brand-guidelines.md](references/brand-guidelines.md), [references/text-color-system.md](references/text-color-system.md), [references/color-block-system.md](references/color-block-system.md), and [references/typography-safety.md](references/typography-safety.md).
4. For an existing source, run the dry-run adapter and read [references/migration-workflow.md](references/migration-workflow.md).
5. Let the companion tool build or migrate the deck while this Skill supplies the fixed pages, backgrounds, fonts, colors, Logo zones, and validation rules.
6. Render every slide, repair text fit/overlap, then run the automated gates.

## Canonical Page Mapping

- Template source slide 1 -> output slide 1, fixed main KV.
- Template source slide 2 -> optional SVG asset library only; never output.
- Template source slide 3 -> output slide 2, exact title/subtitle/speaker fields.
- Template source slide 4 -> output slide 3, optional speaker profile. Populate verified data/photo or leave the approved background blank.
- Template source slides 5-12 -> examples only, never required structures.
- Template source slide 13 -> final output slide, unchanged canonical rendered image.
- Put the talk's own conclusion/Q&A/contact page immediately before the final thank-you slide.

Read [references/template-source-map.md](references/template-source-map.md) for package details and the known signed chart-axis compatibility issue.

## New Deck Workflow

1. Let the companion Skill research, outline, plan, author, and export.
2. Start from `assets/0815-architect-summit-template.pptx` when preserving embedded Tencent fonts and master/layout behavior is useful.
3. Lock output slides 1-3 and the final slide before authoring the body.
4. From output slide 4 onward, let structure follow the content.
5. Apply one approved background per slide, protect its Logo zones, use approved text roles/colors, and keep the talk conclusion penultimate.

## Migration Workflow

Run:

```bash
python3 scripts/summit_adapter.py \
  --source /absolute/path/source.pptx \
  --output-dir /absolute/path/migration-work
```

Use the generated report, map, ledger stub, and companion instructions. For PPTX migration, preserve textboxes, shapes, connectors, images, tables, charts, notes, and hyperlinks as independent objects. Read [references/element-migration-quality.md](references/element-migration-quality.md) and [references/source-intake.md](references/source-intake.md).

Safe package-level repair is optional and conservative:

```bash
python3 scripts/safe_repair_deck.py \
  --input /absolute/path/input.pptx \
  --output /absolute/path/repaired-copy.pptx \
  --report /absolute/path/repair-report.json
```

Structural migration, reflow, split/merge decisions, fixed-page insertion, and final rendered QA remain the companion tool's responsibility. Read [references/automation-and-reporting.md](references/automation-and-reporting.md).

## Non-Negotiable Brand Rules

- 16:9 only.
- Title/display/name roles: `腾讯体 W7`; body/explanation/chart-label roles: `腾讯体 W3`.
- Set Latin, East Asian, and complex-script font fields to the exact Tencent font name.
- Normal titles: `#FD9D50`; normal Chinese/English body copy: `#FFFFFF`.
- Use only approved semantic exceptions and color blocks from the references and `assets/brand-manifest.json`.
- Treat identity baked into backgrounds as authoritative. Never duplicate, redraw, recolor, crop, distort, or cover it.
- Keep every foreground object outside the background-specific Logo exclusion zones.
- Use preview fallbacks only for local rendering. Do not write fallback fonts into the delivered PPTX. Read [references/font-installation.md](references/font-installation.md).
- Font replacement is incomplete until every slide is rerendered and all overlaps, clipping, and bad line breaks are fixed.

## Release Gate

For every deck:

```bash
python3 scripts/validate_deck_brand.py /absolute/path/deck.pptx
```

For migrated PPTX decks, also run:

```bash
python3 scripts/validate_element_migration.py \
  --source /absolute/path/source.pptx \
  --destination /absolute/path/deck.pptx \
  --ledger /absolute/path/element-migration-ledger.json \
  --migration-map /absolute/path/migration-map.json
```

Passing XML checks alone is insufficient. The companion tool must run its overflow checks, render all slides, visually inspect at full size, fix every issue, and rerun the gates.

## Assets And Utilities

- `assets/brand-manifest.json`: machine-readable source of truth.
- `assets/backgrounds/`: approved backgrounds.
- `assets/fixed-pages/`: fixed output slide assets.
- `assets/icons/`: optional SVGs extracted from template source slide 2.
- `assets/color-blocks/`: approved color-block assets.
- `scripts/brand_palette.py`: prompt/palette validation and CIEDE2000 nearest-color queries.
- `scripts/extract_template_assets.py`: staged, hash-checked template refresh.
- `scripts/render_deck_preview.py`: preview-only font fallback rendering.

Use the source template as an identity and asset source, not as a mandatory page blueprint.
