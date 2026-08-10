# Template Source Map

Canonical template SHA-256: `786e11bf78c4f70c8e7525697ca3f357d69bb4f277f5bf49b1b82309f2d64b56`.

The file contains 13 slides, 6 layouts, 1 master, 125 media entries, 12 embedded font parts, and one chart.

| Source slide | Purpose | Rule |
| --- | --- | --- |
| 1 | Main KV | Fixed output slide 1 |
| 2 | 56 SVG icon examples | Asset library only; exclude from output |
| 3 | Talk title | Fixed output slide 2 |
| 4 | Speaker profile | Fixed-structure output slide 3; populate verified roles or retain the blank canonical background |
| 5 | Agenda example | Optional reference |
| 6 | Section example | Optional reference |
| 7-12 | Content examples | Optional reference; no structural mandate |
| 13 | Thank-you artwork | Fixed final output slide |

The chart contains signed negative axis IDs (`-756365072`, `-756369360`). Some importers reject them even though PowerPoint opens the source. Report the issue during intake; repair only a copy using `safe_repair_deck.py --repair-import-compatibility`.

The SVGs extracted to `assets/icons/` are optional visual material. They may support a companion author's layout, but they never impose card, grid, or icon-count requirements.
