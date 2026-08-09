# Mandatory Template Contract

This contract has the highest priority inside this skill. Apply it literally. Do not trade fidelity for creative variation.

## Canvas

- Use a 16:9 PowerPoint canvas. Preserve the original 20 x 11.25 inch canvas when editing the source template; use 13.333 x 7.5 inches for a newly generated standard widescreen deck.
- Place every canonical background at x 0, y 0 and scale it to exactly the full canvas without cropping.
- Do not crop, stretch, recolor, blur, darken, mask, or regenerate canonical backgrounds.

## Fixed Slide 1: Main KV

- Use `assets/fixed-pages/slide-01-main-kv.jpg` as the only visible object.
- Keep the main KV completely unchanged.
- Add no title, subtitle, speaker, page number, logo, panel, shape, overlay, animation object, or transparent mask.
- Do not add a second logo. The approved event identity is already baked into the KV.

Canonical SHA-256:

`f8a7f1a3f6536f632b6a54511c545ca1940b6d4d94fd4585430535f4e09f05ac`

## Fixed Slide 2: Talk Title

- Use `assets/fixed-pages/slide-02-title-background.jpg` as the full-slide background.
- Add exactly the source title hierarchy: main title, subtitle, and speaker field. Add no other visible object.
- Derive the main title and subtitle from the user's content or outline. Split a long topic without changing its meaning.
- Do not invent a speaker name. Render `主讲人：` with an empty name when none is supplied.

| Field | Standard 13.333 x 7.5 position | Original 20 x 11.25 position | Font | Size | Color | Alignment |
| --- | --- | --- | --- | --- | --- | --- |
| Main title | x 2.00, y 2.04, w 9.31, h 1.23 | x 3.00, y 3.06, w 13.96, h 1.85 | `腾讯体 W7` | 88 pt | `#FD9D50` | Center |
| Subtitle | x 3.05, y 3.22, w 7.21, h 0.76 | x 4.57, y 4.83, w 10.82, h 1.14 | `腾讯体 W7` | 54 pt | `#FD9D50` | Center |
| Speaker | x 5.19, y 5.27, w 2.87, h 0.39 | x 7.79, y 7.91, w 4.30, h 0.59 | `腾讯体 W3` | 28 pt | `#FFFFFF` | Center |

Canonical background SHA-256:

`1654ba475d1c3e35c3b8ed25772fe7871f7f08137f86b3a1d226975087b6c68c`

## Fixed Slide 3: Original Template Page

- Use `assets/fixed-pages/slide-03-original-background.jpg` as the only visible object.
- Add no title, speaker profile, photo frame, label, line, placeholder, page number, logo, or explanatory text.
- Populate this page only when the user explicitly instructs Codex to change slide 3. Otherwise preserve it unchanged.

Canonical SHA-256:

`a05520185110930bcfd659528f6d5241d026ee04598932db9417e4fcc00145a3`

## Fixed Final Slide: Thank You

- Use `assets/fixed-pages/slide-final-thanks.png` as the only visible object on the final slide.
- Place it at x 0, y 0 and scale it to the full canvas without cropping.
- Add no custom text, editable recreation, page number, panel, shape, overlay, animation object, or transparent mask.
- Keep the template wording and composition unchanged: `浪会一直来, 而我们学会了看海!`, `谢谢观看`, and `THANKS` are already baked into the canonical asset.
- Put the talk's own conclusion, Q&A, contact information, or closing statement on the penultimate slide.
- Do not rebuild the final text with separate text boxes. The fixed image avoids font-metric changes and text overlap across PowerPoint, WPS, LibreOffice, and machines without Tencent fonts.

Canonical SHA-256:

`f45e79d23692ef6af37ab48e0a0f06c8d7bde3866ff1980dadd7a68def9a29d6`

## Logo And Background Contract

- Treat logos baked into supplied backgrounds as the authoritative logo artwork.
- Never extract, redraw, recolor, distort, replace, duplicate, or cover a logo.
- Use one approved full-slide background on every slide. Do not construct a visually similar background from gradients or generated images.
- Keep all content out of the logo's established corner or top-center clear space.
- Use the cover and closing illustrations only in their intended roles.

### Logo Exclusion Zones

Treat the boxes below as no-content zones. Coordinates use the standard 13.333 x 7.5 inch canvas; multiply every value by 1.5 on the original 20 x 11.25 inch canvas. Do not let text, shapes, charts, images, page numbers, or translucent overlays intersect these boxes.

| Background | Protected identity | Standard-canvas exclusion box |
| --- | --- | --- |
| `background-01-cover.jpg` | Top-left alliance logo | x 0.25, y 0.20, w 2.75, h 0.60 |
| `background-02-content.jpg` | Top-left alliance logo | x 0.25, y 0.20, w 2.75, h 0.60 |
| `background-02-content.jpg` | Top-center summit mark | x 5.00, y 0.20, w 3.35, h 1.82 |
| `background-03-section.jpg` | Top-right alliance logo | x 10.30, y 0.20, w 2.78, h 0.60 |
| `background-04-content-alt.jpg` | Top-left alliance logo | x 0.25, y 0.20, w 2.75, h 0.60 |
| `background-05-content-alt.jpg` | Top-right alliance logo | x 10.30, y 0.20, w 2.78, h 0.60 |
| `background-05-content-alt.jpg` | Bottom-right summit mark | x 11.30, y 6.35, w 1.78, h 1.00 |
| `background-06-closing.jpg` | Top-left alliance logo | x 0.25, y 0.20, w 2.75, h 0.60 |

The boxes protect baked identity artwork only; they do not prescribe a content grid outside those zones.

## Typography Contract

- Set title, section, display, highlighted-name, and title-level numeric runs to `腾讯体 W7`.
- Set body, explanatory, speaker-field, organization, chart-label, and annotation runs to `腾讯体 W3`.
- Set the actual PowerPoint run font names. Do not only simulate the weight with another typeface.
- Use a fallback only for local rendering when Tencent fonts are unavailable; do not write the fallback into the delivered PPTX.
- Preserve natural letter spacing and use no text gradient, glow, outline, bevel, or decorative shadow.
- Follow [typography-safety.md](typography-safety.md). After slide 3, independent text boxes must not substantially overlap; reflow or split content instead of relying on automatic shrinking.

## Text Color Contract

- Use `#FD9D50` for normal titles, section titles, thematic subtitles, selected names, and title-level identifiers.
- Use `#FFFFFF` for Chinese and English explanatory copy, ordinary values, speaker roles, and diagram labels.
- Use `#FFE7B9` only for the primary closing message.
- Use `#A7A7A7` or `#8B8C8C` only for low-priority chart ticks, sources, footnotes, or disabled states.
- Use `#4A6FE8` or `#4D9557` for text only when directly labeling a matching semantic data series or status.
- Never use gray, blue, green, or orange for ordinary narrative paragraphs.

## Approved Background Checksums

| Asset | SHA-256 |
| --- | --- |
| `background-01-cover.jpg` | `f8a7f1a3f6536f632b6a54511c545ca1940b6d4d94fd4585430535f4e09f05ac` |
| `background-02-content.jpg` | `1654ba475d1c3e35c3b8ed25772fe7871f7f08137f86b3a1d226975087b6c68c` |
| `background-03-section.jpg` | `a05520185110930bcfd659528f6d5241d026ee04598932db9417e4fcc00145a3` |
| `background-04-content-alt.jpg` | `20ca3aed69d2630163567e66c9f1136e1c39411058f8b3de816bc9776e18f937` |
| `background-05-content-alt.jpg` | `4ec6d12f308a16a1df35518ace49e283ee7e278e5b1cca458219d4d4a970510b` |
| `background-06-closing.jpg` | `3a337f7867a7abf3e2ee6cc782d65225547bb8fce7f01adfb4f163d4fff1e866` |

## Release Gate

1. Run the companion authoring skill's overflow test.
2. Render every slide and visually inspect text fit, line spacing, contrast, Logo clear space, and unintended overlaps.
3. Confirm every text run explicitly stores `腾讯体 W7` or `腾讯体 W3` for Latin, East Asian, and complex-script font fields and uses a direct approved sRGB color.
4. Confirm the final slide is the canonical single-image thank-you page and the talk conclusion is penultimate.
5. Run `scripts/validate_deck_brand.py <deck.pptx>`.
6. Fix every reported error, rerender affected slides, and rerun both checks.
7. Deliver only after the rendered pass and automated validator both succeed.
