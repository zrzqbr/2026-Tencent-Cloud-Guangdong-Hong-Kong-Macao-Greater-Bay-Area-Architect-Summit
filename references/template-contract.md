# Mandatory Template Contract

This is the highest-priority human-readable contract. `assets/brand-manifest.json` is the machine-readable source of truth.

## Canonical Source Mapping

The official template has 13 source slides, but they do not map one-to-one into a finished speaker deck.

| Template source slide | Role | Finished-deck use |
| --- | --- | --- |
| 1 | Main KV | Output slide 1, unchanged |
| 2 | SVG icon material library | Never output; optional asset source only |
| 3 | Talk title page | Output slide 2 |
| 4 | Speaker profile page | Output slide 3 when verified profile data exists; otherwise blank approved background |
| 5-12 | Layout examples | Examples only; never mandatory structures |
| 13 | Thank-you page | Output final slide, unchanged rendered asset |

Keep content structure free from output slide 4 onward. The sample cards, circles, columns, charts, and image arrangements are not a component system.

The fixed opening sequence is output slides 1-3. No outline, agenda, chapter, migrated body page, or other content page may replace or move ahead of them. The first outline/body content starts on output slide 4.

## Canvas

- Use 16:9.
- Preserve `18288000 x 10287000` EMU when editing the canonical template package.
- Use `12192000 x 6858000` EMU for a standard widescreen package.
- Never crop, recolor, blur, regenerate, or simulate canonical backgrounds.

## Output Slide 1: Fixed Main KV

- Use template source slide 1 or `assets/fixed-pages/slide-01-main-kv.jpg`.
- Keep it unchanged. Add no title, speaker, page number, panel, duplicate Logo, overlay, or transparent mask.
- Canonical SHA-256: `136768a6a056da9eb227e2d92c90f2eb1d0bd23f29b67d960b6b38bd2cb0d8cf`.

## Output Slide 2: Fixed Talk Title

- Use the background from template source slide 3: `assets/fixed-pages/slide-02-title-background.jpg`.
- Preserve the source page structure. Replace only the three canonical text roles; do not add, remove, regroup, resize, or reposition objects.
- Keep exactly three nonempty text shapes: main title, subtitle, and the speaker field.
- Do not invent a speaker name. When none is supplied, retain only the canonical speaker label (for example `主讲人：`) and leave the name portion empty; this still counts as the required nonempty speaker field.
- Split a long topic between main title and subtitle without changing meaning.

| Field | Standard canvas, inches | Original canvas, inches | Font | Size | Color |
| --- | --- | --- | --- | --- | --- |
| Main title | x 1.9991, y 2.0409, w 9.3038, h 1.2338 | x 2.9986, y 3.0614, w 13.9557, h 1.8507 | `腾讯体 W7` | 88 pt | `#FD9D50` |
| Subtitle | x 3.0443, y 3.2223, w 7.2133, h 0.7569 | x 4.5665, y 4.8335, w 10.8200, h 1.1354 | `腾讯体 W7` | 54 pt | `#FD9D50` |
| Speaker | x 5.1966, y 5.2728, w 2.8696, h 0.3926 | x 7.7949, y 7.9092, w 4.3044, h 0.5889 | `腾讯体 W3` | 28 pt | `#FFFFFF` |

Canonical background SHA-256: `d5cee654757974dbee9debe855ce2602750ce5d2478b48021e7ea6196edd6ac3`.

## Output Slide 3: Optional Speaker Profile

- Use the background and roles from template source slide 4.
- Preserve the original self-introduction page structure and circular photo group. Replace only the verified name, role, and photo within their canonical roles.
- When verified speaker name, role, and photo exist, populate the exact roles below.
- When those inputs are missing, use only `assets/fixed-pages/slide-03-original-background.jpg` and leave the page blank.
- Never invent speaker data or substitute a generated portrait.
- Do not place outline or body content on this page. The first such content belongs on output slide 4.

| Role | Standard canvas, inches | Font | Size | Color |
| --- | --- | --- | --- | --- | --- |
| Section label | x 0.7876, y 0.3375, w 3.0336, h 0.4245 | `腾讯体 W7` | 32 pt | `#FD9D50` |
| Speaker name | x 6.1458, y 2.4479, w 3.8939, h 1.0097 | `腾讯体 W7` | 72 pt | `#FD9D50` |
| Speaker role | x 6.1458, y 3.5275, w 4.9167, h 0.4486 | `腾讯体 W3` | 32 pt | `#FFFFFF` |
| Circular photo | x 3.3563, y 2.2917, w 2.3919, h 2.3919 | Circle crop | - | - |

Multiply standard coordinates by 1.5 for the original canvas. Canonical background SHA-256: `a05520185110930bcfd659528f6d5241d026ee04598932db9417e4fcc00145a3`.

## Output Final Slide: Fixed Thank You

- Use `assets/fixed-pages/slide-final-thanks.png` as the only visible object.
- Place it full-slide without cropping and add nothing.
- Put the talk's own conclusion, Q&A, or contact information on the penultimate slide.
- Canonical SHA-256: `3621e27a622845f06136d4f1e8f3ae9ce84cd7cc6f5cfaeca9728b1c702223f4`.

## Background And Logo Contract

- Use exactly one approved summit background on every slide. A layout-inherited background is valid.
- The identity already baked into each background is authoritative. Never duplicate, redraw, recolor, mask, or cover it.
- Keep foreground content out of the exclusion zones in `assets/brand-manifest.json`. The validator reads those zones directly.
- Use the cover and closing artwork only in their intended roles.

Approved background hashes:

| Asset | SHA-256 |
| --- | --- |
| `background-01-cover.jpg` | `136768a6a056da9eb227e2d92c90f2eb1d0bd23f29b67d960b6b38bd2cb0d8cf` |
| `background-02-content.jpg` | `d5cee654757974dbee9debe855ce2602750ce5d2478b48021e7ea6196edd6ac3` |
| `background-03-section.jpg` | `a05520185110930bcfd659528f6d5241d026ee04598932db9417e4fcc00145a3` |
| `background-04-content-alt.jpg` | `20ca3aed69d2630163567e66c9f1136e1c39411058f8b3de816bc9776e18f937` |
| `background-05-content-alt.jpg` | `8f9feac98bc5b1262463a4ae37cc8a81488cacec39efc23f9fb1384f749bcbde` |
| `background-06-closing.jpg` | `3a337f7867a7abf3e2ee6cc782d65225547bb8fce7f01adfb4f163d4fff1e866` |

## Typography And Color

- Title, section, display, highlighted-name, and title-level numeric runs: `腾讯体 W7`, normally `#FD9D50`.
- Body, explanation, organization, chart label, annotation, and speaker role runs: `腾讯体 W3`; use `#FFFFFF` on dark surfaces and `#00365F`, `#111111`, or `#000000` on verified white/light cards and table cells. Fixed-page field colors remain exact.
- Set Latin, East Asian, and complex-script run fonts explicitly to the same required Tencent font.
- Use `#FFE7B9`, muted gray, chart blue, and status green only for the semantic exceptions documented in the color references.
- Font substitution changes metrics. Render after every typography pass and repair overlaps, clipping, and bad line breaks.

## Release Gate

1. Run the companion presentation tool's overflow checks.
2. Confirm output slides 1-3 remain the canonical fixed opening sequence and body content begins on slide 4.
3. Render and visually inspect every slide at full size.
4. Complete migration mapping and the schema-version 3 element ledger, including full-size render, surface-contrast, and zero-text-backing review fields, when migrating an existing PPTX.
5. Run `scripts/validate_element_migration.py` for PPTX migration.
6. Run `scripts/validate_deck_brand.py` for every deck.
7. Fix every error, rerender affected slides, and rerun both gates.
