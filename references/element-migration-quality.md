# Element-Level PPT Migration Quality

Use this reference for PPT/PPTX migrations. The source page is content evidence, not a bitmap payload.

## Non-Negotiable Rule

- Import the source PPTX and preserve each textbox, shape, connector, image, table, chart, hyperlink, and note as an independent object.
- Never place a rendered source slide, screenshot, PDF page image, or contact-sheet tile as the destination body.
- A source element that is already an image remains an image. This is preservation, not slide flattening.
- If an unsupported object must be rasterized, rasterize only that object and record its source element id, type, and reason. Require explicit user approval before rasterizing a whole slide.

## Required Ledger

Create `element-migration-ledger.json` with one entry per one-to-one, split, or merge mapping:

```json
{
  "sourcePages": [8],
  "destinationSlides": [10, 11],
  "before": {"shapes": 17, "connectors": 1, "images": 2, "tables": 2, "charts": 0},
  "deleted": [{"type": "shape", "id": "9", "reason": "legacy full-slide background"}],
  "addedBrandElements": [{"type": "shape", "name": "GBA brand content field"}],
  "rasterizedElements": [],
  "after": {"shapes": 17, "connectors": 1, "images": 2, "tables": 2, "charts": 0},
  "notesPreserved": true,
  "hyperlinksPreserved": true
}
```

Every source-object count loss must be explained by a specific deleted template/background element. Brand-only additions and individual rasterizations must be listed separately. Aggregate counts are valid for split and merged mappings.

## Safe Template Replacement

1. Import the original deck with the native presentation importer.
2. Save the original slide object references and element inventory.
3. Detach legacy masters/layouts by assigning a blank destination layout when inherited page furniture must disappear.
4. Apply an approved summit image as the true slide background fill so existing local z-order is unchanged.
5. Delete only inventoried local background or legacy chrome objects. Never delete by broad text or object-type heuristics.
6. Reposition existing title objects out of Logo exclusion zones; do not add duplicate titles over the source title.
7. Restyle the existing source objects in place. Keep image, table, chart, connector, and text objects independent.

## Fidelity Gate

- Compare normalized visible text from each source slide with its mapped destination slide.
- Compare shapes/connectors, images, tables, and charts against the ledger.
- Fail if a multi-object source page becomes one large body image.
- Fail if a destination image was added without an element-level rasterization entry.
- Render source and destination pages and inspect them side by side after the structural checks pass.
- Run `scripts/validate_element_migration.py` with both the completed ledger and migration map, then the overflow and brand validators.
- Run the brand validator with `--element-migration-ledger`. In this mode, fixed pages and approved backgrounds remain strict; preserved legacy grouped/table runs and source-native overlaps are governed by the element ledger plus full-slide visual inspection because rewriting them can flatten or corrupt the imported objects.
