# Brand Guidelines

## Visual Principle

Express a technology summit rooted in the Greater Bay Area: deep maritime blue, city silhouettes, warm orange-gold light, wave motifs, and an energetic urban-future atmosphere. Preserve this identity while allowing each presentation to develop its own information architecture.

## Canvas And Backgrounds

- Format: widescreen 16:9, designed around 1920 x 1080 source artwork.
- Primary content field: dark navy with a subtle city/harbor scene and ample low-contrast space for content.
- Cover and closing pages: use the full illustrated streetscape and wave artwork.
- Section pages: use a branded blue background with a stronger wave accent or event-title marker.
- Do not place opaque full-slide panels over the background. Preserve enough atmospheric context to identify the event.
- Add localized dark overlays only when required for text contrast.

## Color System

Use these observed source-deck colors as the core palette:

| Role | Color | Guidance |
| --- | --- | --- |
| Primary background | `#00365F` to `#063B64` | Deep maritime navy; sample from the supplied background when possible |
| Primary warm accent | `#FD9D50` | Titles, numbers, dividers, emphasis, wave-linked highlights |
| Text on dark | `#FFFFFF` | Main body and high-priority labels |
| Soft warm highlight | `#FFE7B9` | Supporting emphasis and closing-page warmth |
| Muted text | `#A7A7A7` or `#8B8C8C` | Secondary annotations only |
| Blue data accent | `#4A6FE8` or `#026BFF` | Charts and technical categories |
| Green data accent | `#4D9557` | Positive/status or comparison series |

Keep orange-gold as the dominant accent. Use blue and green as secondary data colors, not as competing themes. Maintain accessible contrast against the dark background.

## Typography

- Required Chinese display/title: `腾讯体 W7`.
- Required Chinese body: `腾讯体 W3`.
- Approved fallback order: `微软雅黑`, `PingFang SC`, `Microsoft YaHei`, then a neutral sans-serif.
- English fallback: `Helvetica`, then `Arial`.
- Use bold or W7 for major titles and numeric emphasis; use W3/regular for explanatory text.
- Preserve natural letter spacing. Avoid decorative display fonts that conflict with the event artwork.
- Size text for projection. As a practical baseline, use approximately 30-44 pt for slide titles and 18-26 pt for body text, then adjust to content and room size.
- The source cover demonstrates 88 pt main-title and 54 pt subtitle scale, but these are references rather than mandatory values.
- Apply all font colors according to [text-color-system.md](text-color-system.md). Treat those mappings as mandatory, not as palette suggestions.
- Set the actual PowerPoint run font names to `腾讯体 W7` and `腾讯体 W3`; do not merely imitate their visual weight with another font.
- Preserve the original template's embedded Tencent font resources when editing from that template. For a newly generated package, retain the exact `腾讯体 W7` and `腾讯体 W3` run names and require those fonts on the presentation machine.

## Logo And Identity

- The event identity appears in the supplied backgrounds, normally near the top-left or top-right depending on page type.
- Use the background artwork as the authoritative logo treatment.
- Keep clear space around the logo and avoid placing text, charts, or decorative shapes over it.
- Do not extract and rebuild the logo from text, apply effects, change colors, or combine it with new marks.
- On cover and closing pages, let the large illustrated event title remain the primary identity signal.

## Composition

- Derive structure from the message, not from the source deck's sample layouts.
- Use a consistent safe area and align content to a deliberate grid.
- Favor strong hierarchy, generous negative space, and a limited number of focal points.
- For dense architecture diagrams, use thin light connectors, restrained orange highlights, and grouped labels instead of many floating cards.
- For charts, use direct labeling where practical and keep axes/gridlines subdued.
- For photography, use high-resolution relevant images with purposeful crops; integrate them using clean rectangular frames or full-bleed regions.
- Avoid excessive rounding, shadows, glass effects, gradients, or generic SaaS-dashboard styling.

## Page Roles

- Slide 1, main KV: use `background-01-cover.jpg` unchanged as the entire slide. Add no talk title, subtitle, speaker identity, panel, shape, or overlay.
- Slide 2, talk information: use `background-02-content.jpg` and preserve the source title-page typography and coordinates on a 13.333 x 7.5 inch canvas:
  - Main title: x 2.00, y 2.04, w 9.31, h 1.23; `腾讯体 W7`; 88 pt; `#FD9D50`.
  - Subtitle: x 3.05, y 3.22, w 7.21, h 0.76; `腾讯体 W7`; 54 pt; `#FD9D50`.
  - Speaker: x 5.19, y 5.27, w 2.87, h 0.39; `腾讯体 W3`; 28 pt; `#FFFFFF`.
  - Split a long detected topic into a concise main title and subtitle without changing its meaning. Add a speaker name only when supplied; otherwise leave the name portion empty.
- Slide 3, original template page: use `background-03-section.jpg` unchanged and add no visible object. Populate it only when the user explicitly supplies content intended for this page.
- Section divider: one short chapter statement with a strong numeral or thematic phrase.
- Content: choose any structure suitable for the idea, including diagrams, comparisons, evidence, images, code, or narrative statements.
- Closing: use the closing illustration and a concise final message, contact detail, or Q&A prompt.

These roles guide narrative rhythm only. They do not prescribe fixed component arrangements.

## Quality Check

- Confirm the deck remains recognizably part of the summit when viewed without context.
- Confirm no content covers the event logo or key illustration details.
- Confirm all body text is readable at presentation scale.
- Confirm the presentation is not merely a sequence of copied sample layouts.
- Confirm charts, diagrams, and images use the brand palette without sacrificing clarity.
- Confirm there are no overlaps, clipped text, broken fonts, or low-resolution assets in the rendered output.
- Confirm every text run follows the mandatory role-to-color mapping: orange-gold titles, white explanatory copy, and only the documented exceptions.
- Confirm title runs use `腾讯体 W7` and body runs use `腾讯体 W3`. If embedded-font portability is required, confirm the deck was derived from the original template package.
- Confirm slide 1 exactly matches the untouched main KV; slide 2 uses the exact 88/54/28 pt title-page typography and coordinates; slide 3 uses the original template background unchanged.
