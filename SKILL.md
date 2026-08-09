---
name: create-gba-architect-summit-slides
description: "Apply the official 2026 Tencent Cloud Guangdong-Hong Kong-Macao Greater Bay Area Architect Summit PowerPoint template as a reusable brand, typography-safety, migration, and validation layer. This is not a standalone PPT generator: use it with a presentation-authoring skill, plugin, or tool. It can create or migrate summit decks while enforcing the fixed first three slides, fixed final thank-you slide, approved logo-bearing backgrounds, Tencent W7/W3 typography, text colors, color blocks, and anti-overlap release checks. Keep content structures flexible after slide 3. Use for creating, migrating, adapting, reviewing, or validating summit speaker decks, agendas, technical talks, case studies, and data stories."
---

# 2026 GBA Architect Summit PPT Template

Apply the summit's official template assets and brand rules to a PowerPoint workflow. Treat this skill as a reusable template and compliance layer, not as the engine that independently researches, outlines, designs, and exports a presentation.

> 定位说明：这是“2026 腾讯云粤港澳大湾区架构师峰会 PPT 模板 Skill”，不是独立的 PPT 生成 Skill。请把它与常用的 PPT 生成、内容研究、图表、图片、PDF 读取或 PPT 编辑 Skill 配合使用；其他 Skill 负责内容提取和制作，本 Skill 负责新 PPT 的模板适配、旧 PPT/PDF 的品牌迁移与最终验收。

## Role And Responsibility

Use this skill together with whichever presentation-authoring skill, plugin, or tool the user normally relies on.

- Let the companion authoring skill own topic research, source collection, outline, narrative, slide planning, layout construction, charts, images, speaker notes, PPTX export, and rendering.
- Let the companion reading or editing capability inspect every source slide or PDF page, extract content, preserve notes and data, and rebuild editable presentation elements where possible.
- Let this template skill own source-to-destination migration rules, the first-three-slide and final-slide contracts, canonical backgrounds, baked-in logos, Logo exclusion zones, Tencent font roles, text colors, approved color blocks, typography safety, and final validation.
- Keep the companion skill's slide structures after slide 3 unless they violate a brand rule. Do not force the sample deck's cards, circles, columns, charts, or page composition onto the companion skill.
- Require the companion skill to render every slide, run its own overflow checks, and revise any text collision before this skill performs the final brand gate. Passing the XML brand validator alone is never sufficient.
- When no authoring skill is named, select an available PowerPoint creation or editing capability, then apply this template skill alongside it. Do not represent this skill alone as a complete PPT generation system.

## Combination Patterns

### Generate A New Deck

1. Use the user's preferred content, research, outline, and presentation-authoring skills to develop the talk and build the PPTX.
2. Apply this template skill throughout authoring so slides 1-3, the final slide, typography spacing, and all brand rules are correct from the start.
3. Put the talk's own conclusion on the penultimate slide and append the canonical final thank-you slide unchanged.
4. Render with the authoring capability, inspect text at full size, run overflow checks, and then run this skill's validator before delivery.

Example request:

> Use my usual PPT generation skill to create a technical talk, and use `$create-gba-architect-summit-slides` as the 2026 summit template and brand-validation layer.

### Migrate An Existing PPT Or PDF

1. Read [references/migration-workflow.md](references/migration-workflow.md) and inventory every source slide or PDF page before editing.
2. Use a PowerPoint or PDF capability to extract the source content, narrative, data, notes, images, and diagrams.
3. Use this template skill to map the source title into slide 2, keep slides 1 and 3 fixed, migrate the remaining content from slide 4 onward, and append the canonical final thank-you slide.
4. Remove the old template skin and adapt every destination slide to the approved backgrounds, baked-in Logo treatment, Tencent fonts, text colors, color blocks, and Logo exclusion zones.
5. Preserve the source's information structure without copying its old visual theme. Rebuild editable elements when possible and record any PDF-derived element that must remain rasterized.
6. Compare source and destination page by page, then validate the migrated `.pptx` with the bundled script.

Example request:

> Migrate this existing PPT or PDF to the 2026 Tencent Cloud Greater Bay Area Architect Summit with `$create-gba-architect-summit-slides`; preserve all content and data while adapting backgrounds, logos, fonts, and brand colors.

### Validate Only

Use this skill without rewriting the narrative when the user only needs a compliance review. Inspect the rendered slides and run `scripts/validate_deck_brand.py <deck.pptx>`.

Example request:

> Use `$create-gba-architect-summit-slides` to check whether this deck complies with the summit template; report violations without changing the content.

## Workflow

1. Identify the companion skill or tool responsible for PPT creation or editing.
2. Read [references/template-contract.md](references/template-contract.md) first. Treat it as authoritative when another reference appears ambiguous.
3. Read [references/brand-guidelines.md](references/brand-guidelines.md), [references/text-color-system.md](references/text-color-system.md), [references/color-block-system.md](references/color-block-system.md), and [references/typography-safety.md](references/typography-safety.md) before the companion capability designs or edits slides.
4. For a source PPT, PPTX, or PDF, read [references/migration-workflow.md](references/migration-workflow.md), create a complete source-to-destination map, and account for every source page before authoring.
5. Let the companion capability inspect the user's content, audience, duration, and output requirements and develop or preserve the narrative.
6. Lock slides 1-3 and the final thank-you slide before authoring the remaining content. Use the canonical assets in `assets/fixed-pages/` and do not substitute lookalike images.
7. Let the companion capability choose the most suitable slide architecture from slide 4 onward. Treat the source deck's circles, cards, charts, and image arrangements as examples only.
8. Apply the branded backgrounds in `assets/backgrounds/` or start from `assets/0815-architect-summit-template.pptx` when native PowerPoint masters are useful.
9. Preserve the summit logo, event identity, palette, exact Tencent font roles, and atmospheric background system without taking ownership of the deck's content structure.
10. Let the companion capability render the deck for visual inspection, including text fit, line spacing, text-box clearance, and every Logo exclusion zone. If LibreOffice renders Chinese as missing-glyph boxes, use `scripts/render_deck_preview.py` with the companion skill's `soffice.py` wrapper. Run the authoring skill's overflow test and complete at least one fix-and-rerender cycle.
11. Run `scripts/validate_deck_brand.py <deck.pptx>`. For migrations, also compare every source page against its destination mapping. Do not deliver until visual inspection, typography safety, migration completeness, and automated validation pass.

## Design Freedom

- Freely create grids, diagrams, timelines, tables, charts, full-bleed images, code views, architecture maps, or asymmetric editorial layouts.
- Freely change the number, size, placement, and style of content containers.
- Do not require cards. Do not repeat the sample deck's circular numbering, three-column layouts, percentage bubbles, or chart treatment unless they serve the content.
- Prefer one strong idea per slide and use composition to express hierarchy.
- Adapt density to the material: keynote pages may be sparse; technical architecture pages may be information-dense but must remain legible.

## Non-Negotiable Identity

- Keep the 16:9 aspect ratio.
- Follow the fixed first-three-slide contract exactly. Never reinterpret it from memory; use `references/template-contract.md` and `assets/fixed-pages/`.
- Retain a recognizable summit background or approved summit illustration on every slide.
- Keep the event logo visible in its established corner position unless the cover or closing artwork already contains the identity prominently.
- Use the specified dark navy, orange-gold, white, and supporting accent palette.
- Set title and display text to `腾讯体 W7`; set body and explanatory text to `腾讯体 W3`. Use fallbacks only for local preview when the Tencent fonts cannot be rendered.
- Start from the original template when portable embedded Tencent fonts are required. When generating a new package, set every run to the exact Tencent font names and do not transplant embedded font parts across unrelated packages.
- Apply text colors strictly by semantic role: orange-gold titles and white Chinese body copy. Follow the text-color reference without creative substitutions.
- Do not recolor, distort, crop, recreate, or obscure the event logo.
- Keep every foreground object, including page numbers and transparent overlays, outside the background-specific Logo exclusion zones in `references/template-contract.md`.
- Keep independent text boxes from substantially intersecting after slide 3. Do not use auto-shrink as the primary layout strategy; follow `references/typography-safety.md` and reflow or shorten content instead.
- Keep the final thank-you page unchanged as a single canonical full-slide asset. Place the talk's own summary, Q&A, or conclusion immediately before it.
- Do not introduce an unrelated corporate template, dominant gradient, or competing visual theme.
- Use only the approved color-block families and opacity ranges from the color-block reference. Do not invent additional large-area block colors.

## Asset Selection

- `background-01-cover.jpg`: opening cover with full event illustration and title artwork.
- `background-02-content.jpg`: standard content background with blue summit identity.
- `background-03-section.jpg`: section or chapter transition background.
- `background-04-content-alt.jpg`: alternate content background.
- `background-05-content-alt.jpg`: alternate content background.
- `background-06-closing.jpg`: closing/thank-you illustration.
- `0815-architect-summit-template.pptx`: original editable reference deck with native masters, embedded fonts, and vector icon examples.
- `fixed-pages/`: canonical, checksum-stable assets for slides 1-3. Use these instead of the ambiguously named general backgrounds.
- `fixed-pages/slide-final-thanks.png`: canonical, font-independent final thank-you page. Use it as the only object on the final slide.
- `color-blocks/`: exact-color transparent PNG blocks and a visual reference sheet.

Run `scripts/generate_color_blocks.py` to rebuild the color-block assets deterministically after changing the approved palette.

Run `scripts/render_deck_preview.py <deck.pptx> --soffice <path-to-soffice-or-wrapper>` when a normal LibreOffice preview cannot render Tencent-font Chinese. The aliases affect preview only and never modify the delivered PPTX.

Run `scripts/validate_deck_brand.py <deck.pptx>` before every delivery. It verifies canonical asset hashes, fixed-slide object counts, the final thank-you page, background order/cropping, slide-2 geometry, direct text runs, and high-risk text-box intersections. A failure is a release blocker, not a warning.

Use the original deck as an asset source, not as a mandatory page blueprint.
