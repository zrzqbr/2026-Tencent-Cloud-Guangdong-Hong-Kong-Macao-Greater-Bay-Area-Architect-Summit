# Mandatory Surface-Aware Text-Color System

Apply typography by semantic role and by the verified visual surface beneath the text. Do not infer readability from a text box's own fill alone.

## Required Mapping

| Text role and surface | Required color |
| --- | --- |
| Slide/section title on the normal summit surface | `#FD9D50` |
| Speaker/person name after slide 3 | `#FD9D50` |
| Body/explanation on a dark summit background or navy panel | `#FFFFFF` |
| Body/explanation on a verified white/light card or table cell | `#00365F`, `#111111`, or `#000000` |
| Text on orange, blue, or green compact semantic blocks | `#FFFFFF` |
| Text on warm-highlight `#FFE7B9` blocks | `#00365F` |
| Closing-page primary words | `#FFE7B9` |
| Closing-page supporting sentence | `#FD9D50` |

## Strict Rules

- On slide 2, the complete speaker field is the fixed `#FFFFFF` template exception.
- Keep normal titles orange when contrast permits. If an inherited decorative title fill no longer belongs, clear that fill after visual confirmation; do not add a new backing plate.
- Body copy is not universally white. Use dark text naturally on white/light surfaces and white text on dark surfaces.
- Set `腾讯体 W7` for title/display runs and `腾讯体 W3` for body/explanatory runs. Set Latin, East Asian, and complex-script fields explicitly.
- Normalize near-white source text to `#FFFFFF` only when it is confirmed to sit on a dark surface.
- Do not add gradients, glow, outlines, shadows, or a text-box fill as a readability workaround.
- Do not perform global color replacement before resolving sibling underlays, group z-order, and table-cell fills.

## Surface Resolution

Follow [contrast-aware-migration.md](contrast-aware-migration.md). A white card may be a separate shape behind a transparent text box inside the same group. Render when the XML hierarchy is ambiguous.

## Emphasis And Diagrams

- Use orange for title-level hierarchy, short emphasis, selected names, and major identifiers, not whole paragraphs.
- Use gray only for low-priority chart ticks, sources, footnotes, and disabled states when contrast remains readable.
- Preserve meaningful source-native semantic series colors when they encode data. Do not blind-recolor a chart or diagram.
- The isolated source-blue phrase exception remains permissible only when it encodes a real contrast and is not a paragraph-wide decoration.

## Validation

Before delivery, verify at full rendered size:

- title roles are orange unless a documented surface exception is required;
- light cards and table cells use dark readable text;
- dark/transparent areas use white readable text;
- no new rectangle, banner, or text fill was added solely behind text;
- grouped shapes and table cells were included in font/color review;
- every schema-version 3 migration ledger entry records a passed visual review.
