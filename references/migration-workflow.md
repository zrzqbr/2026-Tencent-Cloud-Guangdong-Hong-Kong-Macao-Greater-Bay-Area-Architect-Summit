# PPT And PDF Migration Workflow

Use this workflow when the source deck was not created with the 2026 summit template. Produce a new `.pptx` that preserves the source's meaning and evidence while replacing its template skin with the summit system.

## Migration Objective

- Preserve the source's titles, body copy, data, tables, diagrams, images, citations, links, speaker notes, and narrative order unless the user requests editorial changes.
- Replace source backgrounds, template chrome, decorative marks, theme fonts, and theme colors with the summit backgrounds and brand rules.
- Rebuild editable PowerPoint text, shapes, tables, and charts when the source provides enough information. Do not flatten an editable PPTX into page screenshots.
- Keep structures flexible after slide 3. Preserve information architecture, not the old template's visual containers.

## Source Intake

- For `.pptx`, inspect every slide, master, layout, note, chart, table, image, link, and embedded media before editing.
- For legacy `.ppt`, preserve the original file, convert a copy to `.pptx` with an available presentation tool, then compare every converted slide with the original render before migration.
- For `.pdf`, render every page, extract selectable text and images, use OCR only where needed, and verify OCR results against the page image. Treat a PDF as flattened source material, not as an editable template.
- Never omit a source page because extraction is difficult. Mark unreadable or unsupported elements for explicit review.

## Source-To-Destination Map

Create `migration-map.json` in the temporary working directory before building the destination deck. Account for every source slide or PDF page with one of these actions: `map-to-title`, `migrate`, `split`, `merge`, or `omit-with-user-approval`.

```json
{
  "source": "/absolute/path/source.pdf",
  "sourceType": "pdf",
  "pages": [
    {"sourcePage": 1, "action": "map-to-title", "destinationSlides": [2]},
    {"sourcePage": 2, "action": "migrate", "destinationSlides": [4]}
  ]
}
```

Do not use `omit-with-user-approval` without explicit user approval. Record every split or merge so source coverage remains auditable.

## Fixed-Page Mapping

1. Insert the canonical main KV as destination slide 1 without changes.
2. Map the source deck's talk title, subtitle, and supplied speaker name into the fixed slide-2 fields. Do not duplicate the old cover as a later content slide.
3. Insert the canonical slide 3 unchanged and empty.
4. Migrate source body content from destination slide 4 onward. Preserve an existing speaker biography or headshot page after slide 3 when the source contains one; do not invent it.
5. Map a source closing message, conclusion, Q&A, or contact page to the penultimate destination slide when relevant.
6. Append `assets/fixed-pages/slide-final-thanks.png` unchanged as the final slide. Do not rebuild or place source content on top of it.

## Brand Adaptation

- Remove the source template's background artwork, master decoration, page chrome, old event branding, and duplicated template logos.
- Preserve customer, product, partner, certification, or sponsor logos only when they are actual content. Use authentic source assets and keep them outside the summit Logo exclusion zones.
- Place one approved summit background full-slide and bottom-most on every destination slide. Never add a separate summit logo because identity artwork is already baked into the background.
- Set all destination title and display runs to `腾讯体 W7`; set body, explanation, chart-label, and annotation runs to `腾讯体 W3`.
- Apply the mandatory role-to-color mapping: orange-gold titles, white explanatory copy, and only documented exceptions.
- Replace source-theme fills with approved color blocks. Keep charts semantically readable while translating series colors into the summit palette.
- Reflow, split, or redesign content when necessary for legibility. Do not preserve a source layout when it causes overlap, tiny text, or Logo obstruction.
- Apply [typography-safety.md](typography-safety.md). Font substitution changes text metrics, so every migrated slide must be rerendered and checked for collisions after Tencent fonts are assigned.

## Content Fidelity

- Preserve wording and numerical precision unless the user asks for rewriting or summarization.
- Preserve source footnotes, citations, hyperlinks, units, legends, chart scales, table headers, and speaker notes.
- Recompute charts from embedded or supplied data when possible. If PDF chart data cannot be recovered, preserve a clean high-resolution chart crop and record the editability limitation in the handoff.
- Extract source images at their original resolution when possible; avoid screenshots containing obsolete backgrounds or page furniture.
- Do not invent missing data, speaker details, logos, claims, or citations.

## Release Gate

1. Confirm every source page appears in `migration-map.json` and every mapped destination slide exists.
2. Compare each source page with its destination slide at full size for content loss, OCR errors, altered numbers, missing notes, and incorrect crops.
3. Run the companion authoring skill's overflow test and inspect the entire destination deck for narrative continuity, text fit, editable elements, background consistency, and Logo clear space.
4. Confirm the talk's own conclusion is penultimate and the canonical thank-you page is final.
5. Rerender every changed slide after fixing a typography issue.
6. Run `scripts/validate_deck_brand.py <destination.pptx>` and require a zero exit status.
7. Deliver only after content fidelity, rendered typography safety, template compliance, and automated brand validation all pass.
