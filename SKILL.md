---
name: create-gba-architect-summit-slides
description: Create, redesign, or extend PowerPoint presentations for the Guangdong-Hong Kong-Macao Greater Bay Area Architect Summit using the supplied summit background system, theme colors, typography, and logos while keeping slide structures and content layouts flexible. Use for branded summit decks, speaker presentations, agendas, technical talks, case studies, data stories, or edits to .pptx files that must retain the visual identity of the 0815 architect summit template.
---

# Create GBA Architect Summit Slides

Create polished 16:9 summit presentations that preserve the event identity without copying the sample deck's page structures.

## Workflow

1. Read [references/brand-guidelines.md](references/brand-guidelines.md), [references/text-color-system.md](references/text-color-system.md), and [references/color-block-system.md](references/color-block-system.md) before designing or editing slides.
2. Inspect the user's content, audience, talk duration, and output requirements. Infer a clear narrative when these are not specified.
3. Choose the most suitable slide architecture for the content. Treat the source deck's circles, cards, charts, and image arrangements as examples only.
4. Use the branded backgrounds in `assets/backgrounds/` or start from `assets/0815-architect-summit-template.pptx` when native PowerPoint masters are useful.
5. Preserve the summit logo, event identity, palette, exact Tencent Sans font roles, and atmospheric background system.
6. Build each slide around its communication purpose: statement, comparison, process, architecture, timeline, evidence, demo, or conclusion.
7. Keep the first three slides fixed: use the original main KV unchanged on slide 1; format a detected talk title on slide 2 using the source template's exact 88/54/28 pt title-page specification; use the original slide-3 template background unchanged on slide 3.
8. Verify readability, alignment, contrast, image quality, Tencent font run names, and visual consistency. Render the deck for visual inspection before delivery whenever tools allow.

## Design Freedom

- Freely create grids, diagrams, timelines, tables, charts, full-bleed images, code views, architecture maps, or asymmetric editorial layouts.
- Freely change the number, size, placement, and style of content containers.
- Do not require cards. Do not repeat the sample deck's circular numbering, three-column layouts, percentage bubbles, or chart treatment unless they serve the content.
- Prefer one strong idea per slide and use composition to express hierarchy.
- Adapt density to the material: keynote pages may be sparse; technical architecture pages may be information-dense but must remain legible.

## Non-Negotiable Identity

- Keep the 16:9 aspect ratio.
- Do not add, remove, crop, cover, or overlay anything on slide 1. The original cover main KV must remain unchanged.
- Use `background-02-content.jpg` on slide 2. Set the main title to `腾讯体 W7`, 88 pt, `#FD9D50`; the subtitle to `腾讯体 W7`, 54 pt, `#FD9D50`; and the speaker field to `腾讯体 W3`, 28 pt, `#FFFFFF`. Use the fixed source-template coordinates from the brand reference.
- Use `background-03-section.jpg` unchanged on slide 3. Add no visible object unless the user explicitly supplies content for that original template page.
- Retain a recognizable summit background or approved summit illustration on every slide.
- Keep the event logo visible in its established corner position unless the cover or closing artwork already contains the identity prominently.
- Use the specified dark navy, orange-gold, white, and supporting accent palette.
- Set title and display text to `腾讯体 W7`; set body and explanatory text to `腾讯体 W3`. Use fallbacks only for local preview when the Tencent fonts cannot be rendered.
- Start from the original template when portable embedded Tencent fonts are required. When generating a new package, set every run to the exact Tencent font names and do not transplant embedded font parts across unrelated packages.
- Apply text colors strictly by semantic role: orange-gold titles and white Chinese body copy. Follow the text-color reference without creative substitutions.
- Do not recolor, distort, crop, recreate, or obscure the event logo.
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
- `color-blocks/`: exact-color transparent PNG blocks and a visual reference sheet.

Run `scripts/generate_color_blocks.py` to rebuild the color-block assets deterministically after changing the approved palette.

Use the original deck as an asset source, not as a mandatory page blueprint.
