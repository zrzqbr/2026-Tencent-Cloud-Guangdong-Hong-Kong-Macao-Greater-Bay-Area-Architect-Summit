# Background-Aware Text And Surface Migration

Use this reference for every editable PPT/PPTX migration. Readability follows the actual rendered surface, not a universal body-text color.

## Non-Negotiable Principle

Do not add a rectangle, banner, translucent navy panel, or fill on a text box solely to make the text readable. If the visible surface is light, use dark text. If it is dark, use light text. Preserve meaningful cards, table cells, diagram nodes, images, and source-native color relationships.

## Resolve The Actual Surface

Determine the surface in this order:

1. Explicit fill on the table cell or semantic container that owns the text.
2. Topmost overlapping sibling beneath the text, respecting object and group z-order.
3. Group or parent container fill.
4. Approved slide background or bottom-most full-slide background image.
5. Full-size render inspection when XML structure is ambiguous, inherited, transparent, image-based, or grouped.

A text shape's own `noFill` does not mean the text sits on the summit background. White cards are often separate sibling shapes. Inspect the group and rendered slide before changing the text.

## Contrast Mapping

| Verified visual surface | Text treatment |
| --- | --- |
| Dark summit background, transparent text box, navy panel | `腾讯体 W3` `#FFFFFF` body; `腾讯体 W7` `#FD9D50` title |
| White or very light card/table cell | `腾讯体 W3` `#00365F`, `#111111`, or `#000000`; title/emphasis may remain orange when readable |
| Orange, blue, or green compact semantic block | `#FFFFFF` |
| Warm `#FFE7B9` block | `#00365F` |
| Image or gradient | Move text to a naturally readable region, adjust text color, or preserve an existing semantic container; do not manufacture a readability-only backing plate |

Use black naturally on white when that is the clearest faithful result. The requirement is readable contrast plus summit typography, not white text everywhere.

## Groups, Tables, And Decorative Fills

- Traverse text in nested groups and set Latin, East Asian, and complex-script font fields on every run.
- Treat a table as cell surfaces plus cell text. Update each cell/run; a `p:sp`-only pass misses table text.
- For mixed-fill tables, record `tableCellTextColors` by 1-based `row,column`; a whole-table default is insufficient when header and body cells use different surfaces.
- Preserve real information cards, tables, diagram nodes, badges, and callouts.
- Remove a source title/caption fill only when it is obsolete decorative furniture and the title remains readable on the summit background.
- Never delete or recolor by a broad rule such as “all rectangles,” “all blue shapes,” or “all body text.”
- Use OOXML counts for the migration ledger. Some authoring APIs include connectors in a generic shape collection, so that collection is not a reliable element inventory.

## Required Review Record

Complete this object for every schema-version 3 ledger entry:

```json
{
  "visualReview": {
    "renderedAtFullSize": true,
    "surfaceContrastReviewed": true,
    "textBackingShapesAdded": 0,
    "status": "passed",
    "notes": ["Light cards retain dark text; dark/transparent regions use white text."]
  }
}
```

If a backing shape existed in the source as a meaningful semantic container, preserve it and identify it in `notes`; do not count it as a newly added readability-only backing shape.

## Release Audit

Render every slide after font and color changes. At full size, verify:

- no full-slide or large navy foreground panel covers migrated content;
- no text box gained a new fill solely for contrast;
- every white/light card and table cell uses dark readable text;
- every transparent text region on a dark surface uses light readable text;
- source-native cards, tables, groups, charts, and connectors remain editable and correctly layered;
- no stale output produced before the current Skill revision is delivered.

Overflow checks detect clipping, not occlusion or poor contrast. Passing them does not replace this audit.
