---
name: create-gba-architect-summit-slides
description: Create, redesign, validate, or extend PowerPoint presentations for the Guangdong-Hong Kong-Macao Greater Bay Area Architect Summit while strictly preserving the supplied main KV, fixed first-three-slide contract, logo-bearing backgrounds, Tencent W7/W3 typography, text colors, and approved color blocks. Use for branded summit decks, speaker presentations, agendas, technical talks, case studies, data stories, or edits to .pptx files that must retain the exact visual identity of the 0815 architect summit template while allowing flexible content layouts after slide 3.
---

# Create GBA Architect Summit Slides

Create polished 16:9 summit presentations that preserve the event identity without copying the sample deck's page structures.

## Workflow

1. Read [references/template-contract.md](references/template-contract.md) first. Treat it as authoritative when another reference appears ambiguous.
2. Read [references/brand-guidelines.md](references/brand-guidelines.md), [references/text-color-system.md](references/text-color-system.md), and [references/color-block-system.md](references/color-block-system.md) before designing or editing slides.
3. Inspect the user's content, audience, talk duration, and output requirements. Infer a clear narrative when these are not specified.
4. Lock slides 1-3 before designing the remaining content. Use the canonical assets in `assets/fixed-pages/` and do not substitute lookalike images.
5. Choose the most suitable slide architecture for slides 4 onward. Treat the source deck's circles, cards, charts, and image arrangements as examples only.
6. Use the branded backgrounds in `assets/backgrounds/` or start from `assets/0815-architect-summit-template.pptx` when native PowerPoint masters are useful.
7. Preserve the summit logo, event identity, palette, exact Tencent Sans font roles, and atmospheric background system.
8. Build each content slide around its communication purpose: statement, comparison, process, architecture, timeline, evidence, demo, or conclusion.
9. Render the deck for visual inspection, including every Logo exclusion zone, then run `scripts/validate_deck_brand.py <deck.pptx>`. Do not deliver until both visual inspection and automated validation pass.

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
- `color-blocks/`: exact-color transparent PNG blocks and a visual reference sheet.

Run `scripts/generate_color_blocks.py` to rebuild the color-block assets deterministically after changing the approved palette.

Run `scripts/validate_deck_brand.py <deck.pptx>` before every delivery. It verifies canonical asset hashes, fixed-slide object counts, background order/cropping, slide-2 geometry, and every direct text run. A failure is a release blocker, not a warning.

Use the original deck as an asset source, not as a mandatory page blueprint.
