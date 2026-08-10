# Mandatory Typography Safety

Use these rules with the companion PPT authoring skill. Correct font names and colors do not prove that a slide is readable; the deck must also survive the target renderer without text collisions, clipping, or unintended shrinking.

## Responsibility Split

- The companion authoring skill owns text measurement, text-box sizing, wrapping, rendering, and overflow testing.
- This template skill owns the required Tencent font roles, fixed-page geometry, minimum spacing rules, visual release gate, and brand validator.
- Do not deliver a deck merely because `validate_deck_brand.py` passes. That script cannot replace rendered visual inspection.

## Authoring Rules

- Set every title or display run to `腾讯体 W7` and every body or explanatory run to `腾讯体 W3` before measuring the layout.
- Treat font fallback as preview-only. Tencent fonts and fallback fonts have different widths, ascenders, descenders, and line heights.
- Use one text box per semantic block. Do not stack duplicate or partially overlapping text boxes to simulate a multiline heading.
- After slide 3, keep at least 0.12 inch of vertical clearance between independent title, kicker, subtitle, body, caption, and footer text boxes. Keep at least 0.15 inch between adjacent text columns.
- Do not let two independent text boxes intersect by more than 0.04 inch on both axes. The validator treats this as a collision risk.
- Account for text-box internal margins when aligning boxes. Use zero margins only when the authoring tool measures the resulting line height correctly.
- For multiline text, budget at least 1.25 times the font size per line for W7 and 1.30 times the font size per line for W3, plus the box's top and bottom margins.
- Keep ordinary content-page titles at 30 pt or larger and body copy at 18 pt or larger. Reduce wording or split the slide before reducing below these floors.
- Do not use `fit`, `shrinkText`, `autoFit`, or equivalent behavior as the primary layout method. It may remain as a final safety net only when the rendered result stays above the font-size floors.
- Do not use negative character spacing or negative line spacing. Preserve natural letter spacing.

## Fixed Pages

- Slide 2 keeps the exact template boxes and 88/54/28 pt sizes. If the topic is too long, split it into the required main-title and subtitle fields; never shrink or move the fixed fields.
- The final slide must use `assets/fixed-pages/slide-final-thanks.png` as its only visible object. Do not recreate `谢谢观看` and `THANKS` as editable text because renderer-specific font metrics can change their spacing.
- Put the talk's custom conclusion, Q&A, contact information, or closing statement on the penultimate slide.

## Common Failure Patterns

- A small English kicker touches the orange Chinese title because their boxes share the same vertical band.
- A label box extends under a neighboring value or description box even though the visible words appear separated in one renderer.
- A two-line Chinese heading uses a box sized for one line and relies on automatic shrinking.
- A chart label sits on top of a value label or bar-end label after fallback-font substitution.
- White text is applied to a white sibling card because the repair pass inspected only the text box's own transparent fill.
- A navy rectangle is inserted behind a title or paragraph instead of adapting the font color to the actual surface.
- The template thank-you page is rebuilt with separate text boxes, causing `谢谢观看` and `THANKS` to move or overlap on another machine.

## Required Verification Loop

1. Generate or migrate the PPTX with exact Tencent font names.
2. Run the companion authoring skill's overflow or slide-layout test.
3. Render every slide to PDF and images. Prefer a renderer with Tencent fonts. If LibreOffice shows missing-glyph boxes, use the bundled preview alias helper instead of inspecting an unreadable render:

   ```bash
   python3 scripts/render_deck_preview.py /absolute/path/deck.pptx \
     --soffice /absolute/path/to/companion-ppt-skill/scripts/office/soffice.py
   ```

   The helper changes only the preview renderer's font aliases; it never changes the PPTX font fields.
4. Inspect every slide at full size for glyph overlap, line collision, clipping, excessive auto-shrink, text touching other text/charts/Logo zones, and light-on-light or dark-on-dark contrast. Include grouped sibling underlays and table cells.
5. Fix issues by adapting text color to the verified surface, enlarging or moving boxes, increasing clearance, shortening copy, or splitting slides. Do not fix a collision or contrast problem by hiding it behind a new shape.
6. Rerender every changed slide and perform a second full-deck pass.
7. Run `scripts/validate_deck_brand.py <deck.pptx>` and require a zero exit status.

The release gate requires both a clean rendered pass and a clean automated validation pass.
