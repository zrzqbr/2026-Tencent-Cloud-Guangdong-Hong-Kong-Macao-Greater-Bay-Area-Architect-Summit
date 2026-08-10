# Automation And Reporting

## Dry-Run Adapter

`summit_adapter.py` is the preferred first command. It does not generate slides or mutate the source.

```bash
python3 scripts/summit_adapter.py \
  --source /absolute/path/source.pptx \
  --output-dir /absolute/path/work
```

Outputs:

- `adapter-report.json`: source inventory, page classification, font/color replacement candidates, background/overlay checks, boundary/collision warnings, and chart compatibility issues.
- `migration-map.json`: fixed-page mapping plus flexible body mappings.
- `element-migration-ledger.json`: a stub the companion authoring tool must complete.
- `companion-instructions.md`: concise execution contract for another PPT Skill/tool.

Use `--destination /absolute/path/output.pptx` to add brand validation of an existing migrated output.

The map always reserves output slides 1-3 and starts outline/body content on slide 4. If the source already contains a canonical opening sequence or canonical final thank-you page, the map marks those pages for preservation instead of rebuilding them.

## Palette Queries

```bash
python3 scripts/brand_palette.py --prompt
python3 scripts/brand_palette.py --validate '#FD9D50' --json
python3 scripts/brand_palette.py --nearest '#F6A05A' --json
python3 scripts/brand_palette.py --chart
```

Color matching uses CIEDE2000. A near result is a suggestion, not permission for uncontrolled global recoloring.

## Safe Repairs

Run `safe_repair_deck.py` without `--output` for a dry-run report. With `--output`, it writes a new package and never overwrites the source.

Safe automatic scope:

- explicit Latin/East Asian/complex-script Tencent font names;
- fixed-page colors plus explicit object/table colors from a reviewed contrast map;
- chart text fonts; chart text/series colors only in reviewed strict-color mode;
- optional signed chart-axis compatibility conversion.

The repair tool preserves unlisted body colors. `--strict-colors` requires `--contrast-map` so it cannot blindly turn light-card text white. It visits grouped shapes and table-cell runs and never adds or changes shape fills.

Use 1-based slide/table numbers and OOXML `p:cNvPr` shape ids in the reviewed map:

```json
{
  "slides": {
    "10": {
      "shapeColors": {"15": "00365F", "24": "111111"},
      "tableTextColors": {"1": "00365F"},
      "tableCellTextColors": {"1": {"1,1": "FFFFFF", "2,1": "111111"}}
    },
    "25": {
      "shapeColors": {"9": "FFFFFF"},
      "tableTextColor": "FFFFFF"
    }
  },
  "normalizeChartColors": false
}
```

Unlisted shapes, cells, and charts retain their source colors. Set `normalizeChartColors` to `true` only after reviewing chart semantics.

Structural work remains owned by the companion presentation tool: fixed pages, background/master replacement, content reflow, split/merge decisions, editable element migration, and final rendered QA.

## Template Refresh

```bash
python3 scripts/extract_template_assets.py \
  --template /absolute/path/new-template.pptx \
  --rendered-thanks /absolute/path/rendered-slide-13.png \
  --output-dir /absolute/path/stage
```

Inspect `template-extraction-report.json`. Use `--apply` only after the template hash, all background/fixed-page hashes, slide count, geometry, and compatibility warnings match the intentionally updated manifest.
