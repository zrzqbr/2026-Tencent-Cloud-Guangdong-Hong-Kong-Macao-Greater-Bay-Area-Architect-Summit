# Mandatory Text-Color System

Apply font colors by semantic role exactly as observed in the source deck. Do not choose font colors freely from the broader palette.

## Required Mapping

| Text role | Required color | Examples |
| --- | --- | --- |
| Slide title | `#FD9D50` | Page title, content-page heading |
| Section title | `#FD9D50` | Chapter name, section divider title |
| Chinese subtitle or thematic phrase | `#FD9D50` | Short supporting headline below a title |
| Speaker/person name after slide 3 | `#FD9D50` | Name on a dedicated introduction page |
| Key label or title-level number | `#FD9D50` | Chapter number, highlighted index, major KPI label |
| Chinese explanatory body | `#FFFFFF` | Paragraphs, descriptions, bullet content |
| English explanatory body | `#FFFFFF` | Supporting paragraph, source note when readable |
| Speaker role/organization | `#FFFFFF` | Job title, department, organization |
| Ordinary numbers and units | `#FFFFFF` | Body-level values, percentages, units |
| Closing-page primary words | `#FFE7B9` | `谢谢观看`, `THANKS` or equivalent closing prompt |
| Closing-page supporting sentence | `#FD9D50` | Final quote or short concluding line |

## Strict Rules

- On slide 2, the complete speaker field, including `主讲人：` and any supplied name, is the fixed `#FFFFFF` exception required by the template contract.
- Set all normal slide and section titles to `#FD9D50`. Do not use white titles merely for variety.
- Set all Chinese body copy to `#FFFFFF`. Do not use gray, pale blue, or orange for normal explanatory paragraphs.
- Keep a title orange and its explanation white even when the composition or container structure changes.
- Use orange only for title-level hierarchy, short emphasis, selected names, and major identifiers. Do not color entire paragraphs orange.
- Use `#FFE7B9` only for the closing-page primary message or an exceptionally soft ceremonial phrase. Do not use it as a routine subtitle color.
- Normalize near-white source text such as `#F9FBFA` to the required `#FFFFFF`; do not preserve near-white variants in a delivered deck.
- Do not use gradients, multicolor letters, glowing text, outlined display text, or decorative text shadows.

## Rare Exception

The source deck uses `#4A6FE8` for one deliberately isolated phrase inside a quotation. Allow this blue only when all conditions apply:

- The text is a short inline phrase, not a full title or paragraph.
- The color encodes a meaningful contrast.
- Orange and white already establish the primary hierarchy.
- The blue phrase appears no more than once on the slide.

Otherwise use orange-gold for emphasis.

## Text On Filled Blocks

- On primary and secondary navy panels, use orange-gold for headings and white for body copy.
- On orange, blue, or green compact blocks, use `#FFFFFF` for text.
- On warm-highlight `#FFE7B9` blocks, use deep navy `#00365F` only when text must sit inside the fill.
- Do not place long paragraphs inside orange, blue, green, or warm-highlight blocks.

## Charts And Diagrams

- Use white for ordinary labels, node descriptions, axis labels, and legends.
- Use orange-gold for the selected node, active path, primary series label, or main takeaway.
- Use `#A7A7A7` or `#8B8C8C` only for low-priority chart ticks, sources, footnotes, and disabled states. Never use gray for narrative body copy.
- Use blue or green text only when it directly labels the matching semantic series or status.

## Validation

Before delivery, inspect every slide and confirm:

- Every normal title is `#FD9D50`.
- Every normal Chinese paragraph is `#FFFFFF`.
- No body paragraph is gray, blue, green, or orange.
- Warm yellow is limited to the closing-page primary message.
- Blue text is absent unless it satisfies the rare inline-exception rule.
- Text placed on colored blocks follows the documented contrast mapping.
