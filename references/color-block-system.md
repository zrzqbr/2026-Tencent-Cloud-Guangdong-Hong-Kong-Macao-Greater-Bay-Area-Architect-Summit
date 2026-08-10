# Approved Color-Block System

Use only the following families for filled rectangles, bands, labels, diagram groups, chart callouts, and content panels. Layout and dimensions remain free.

## Structural Blocks

| Block | Fill | Opacity | Shape | Use |
| --- | --- | --- | --- | --- |
| Primary panel | `#063B64` | 88-94% | Rectangle or 0-4 px corner radius | Main text, code, diagrams, dense content |
| Secondary panel | `#0A527E` | 72-84% | Rectangle or 0-4 px corner radius | Grouping, comparison, secondary layers |

- Use no more than three structural panels on a typical slide.
- Prefer open composition without panels when the background remains readable.
- For new summit-native layouts, prefer open composition or approved navy panels. During migration, preserve white/light source-native cards when they carry real information structure or are needed for faithful image/table/diagram contrast.
- Never insert a large or full-slide primary panel above migrated content. Approved artwork must be a true background fill or the bottom-most full-slide image.

## Emphasis Blocks

| Block | Fill | Opacity | Shape | Use |
| --- | --- | --- | --- | --- |
| Orange accent | `#FD9D50` | 100% | Thin band, compact label, number block | Primary emphasis and active focus |
| Warm highlight | `#FFE7B9` | 100% | Compact label or small highlight field | Quotes, key evidence, softer emphasis |

- Keep orange-filled area below roughly 15% of a content slide.
- Keep warm-highlight area below roughly 10% of a content slide.
- Use deep navy text on warm-highlight blocks and white text on orange blocks. Follow `text-color-system.md` for all typography colors.

## Semantic Blocks

| Block | Fill | Opacity | Shape | Use |
| --- | --- | --- | --- | --- |
| Blue information | `#4A6FE8` | 90-100% | Small label, node, chart series | Information, neutral technical category |
| Green status | `#4D9557` | 90-100% | Small label, node, chart series | Success, validated state, positive outcome |

- Use semantic blocks only when the color carries meaning.
- Do not use blue or green as a decorative large-area background.
- Limit a slide to one semantic blue and one semantic green treatment.

## Neutral Treatment

- Use `#FFFFFF` for main text on dark surfaces and thin outlines. On verified white/light cards and table cells, use `#00365F`, `#111111`, or `#000000`.
- Use `#A7A7A7` or `#8B8C8C` for muted annotations and subdued dividers.
- Do not use gray as a large filled block.
- Prefer 1-1.5 pt white outlines at 25-45% opacity for unfilled groups.

## Geometry Rules

- Prefer rectangles, slim bands, underlines, cropped corner tabs, or open outlined groups.
- Keep corner radius visually small: square corners or approximately 0-4 px at 1920 x 1080.
- Allow a radius up to 12 px only for a compact status chip or image mask.
- Avoid pill-shaped containers unless representing status or a short category label.
- Avoid large circles as default content containers; reserve circles for data with an intrinsic radial meaning.
- Avoid stacked translucent glass panels, bevels, heavy shadows, glossy effects, and gradients inside blocks.
- Do not add any block solely as a backing plate for text readability. Change the text color to match the actual surface.

## Combination Limits

- Use one structural blue plus orange accent as the default combination.
- Add either warm highlight or one semantic color when the content requires it.
- Do not use all six block colors on one slide unless displaying a data legend that genuinely needs them.
- Keep at least 60% of the slide visually governed by the summit background and negative space rather than filled blocks.
- In element migration, preserve meaningful source containers and count only genuinely new brand objects in the ledger. Do not classify preserved source cards as brand additions.

## Assets

Use `assets/color-blocks/color-block-reference.png` as the visual overview. Individual transparent PNG files in the same folder are exact raster references. Prefer native PowerPoint shapes with the listed fills and opacity values when editability matters.
