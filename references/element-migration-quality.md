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
  "hyperlinksPreserved": true,
  "visualReview": {
    "renderedAtFullSize": true,
    "surfaceContrastReviewed": true,
    "textBackingShapesAdded": 0,
    "status": "passed",
    "notes": []
  }
}
```

Every source-object count loss must be explained by a specific deleted template/background element. Brand-only additions and individual rasterizations must be listed separately. Aggregate counts are valid for split and merged mappings.

For schema version 3, set `notesPreserved` and `hyperlinksPreserved` to `true` only after comparison, including when both source and destination have none. Hyperlink validation compares relationship targets, not only counts. Declare every approved wording edit as `{"before":"...","after":"...","reason":"..."}`; a nonempty placeholder no longer bypasses text fidelity.

## Safe Template Replacement

1. Import the original deck with the native presentation importer.
2. Save the original slide object references and element inventory.
3. Detach legacy masters/layouts by assigning a blank destination layout when inherited page furniture must disappear.
4. Apply an approved summit image as the true slide background fill so existing local z-order is unchanged.
   Never add a large navy content field above imported objects.
5. Delete only inventoried local background or legacy chrome objects. Never delete by broad text or object-type heuristics.
6. Reposition existing title objects out of Logo exclusion zones; do not add duplicate titles over the source title.
7. Restyle the existing source objects in place. Keep image, table, chart, connector, and text objects independent.
8. Traverse nested groups and table cells. Set run-level Latin/East Asian/complex-script fonts and adapt text to the verified surface without adding a backing fill.

## Fidelity Gate

- Compare normalized visible text from each source slide with its mapped destination slide.
- Compare shapes/connectors, images, tables, and charts against the ledger.
- Fail if a multi-object source page becomes one large body image.
- Fail if a destination image was added without an element-level rasterization entry.
- Render source and destination pages and inspect them side by side after the structural checks pass.
- Inspect white/light cards, table cells, separate sibling underlays, and dark/transparent regions for correct text contrast. Overflow checks do not detect occlusion or unreadable color pairs.
- Fail if a new rectangle, banner, or text-box fill exists only to make text readable.
- Fail if a large filled foreground shape or non-background full-slide picture covers the approved summit background.
- Count connectors from OOXML as connectors, not from a generic authoring-tool shape collection.
- Run `scripts/validate_element_migration.py` with both the completed ledger and migration map, then the overflow and brand validators.
- Run the brand validator with `--element-migration-ledger`. In this mode, fixed pages, approved body backgrounds, Logo zones, and Tencent run fonts remain strict; source-native body colors and overlaps are governed by the completed schema-version 3 visual review plus full-slide inspection because the actual surface can be a separate grouped sibling.
