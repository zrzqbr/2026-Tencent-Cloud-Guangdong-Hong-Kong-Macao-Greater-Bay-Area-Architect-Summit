# PPT, PDF, HTML, And Markdown Migration Workflow

Use this workflow when content already exists outside the summit template. The output is a new branded PPTX; this Skill supplies the constraints, plan, assets, and release gates while a companion presentation tool performs the actual authoring.

## Intake First

Run the dry-run adapter before editing:

```bash
python3 scripts/summit_adapter.py \
  --source /absolute/path/source.pptx \
  --output-dir /absolute/path/migration-work
```

It writes `adapter-report.json`, `migration-map.json`, `element-migration-ledger.json`, and `companion-instructions.md`.

- `.pptx`: inspect slides, object counts, visible text, run fonts/colors, backgrounds, overlays, Logo zones, boundaries, collisions, and chart-axis compatibility.
- `.ppt`: preserve the original and convert a copy to PPTX before element-level migration.
- `.pdf`: recover editable text, tables, diagrams, and images where possible. Rasterize only irrecoverable individual objects, not every page.
- `.html` / `.md`: treat headings, body content, images, code, and links as source evidence for migration. This does not turn this Skill into a standalone content generator.

See [source-intake.md](source-intake.md) for format-specific requirements.

## Mapping Rules

- Destination slide 1: canonical template source slide 1, unchanged.
- Destination slide 2: template source slide 3, populated with the detected title hierarchy and supplied speaker field.
- Template source slide 2: excluded from output; use its SVGs only as optional visual assets.
- Destination slide 3: template source slide 4. Populate verified speaker details/photo or leave the approved background blank.
- Destination slide 4 onward: migrate source content with flexible structure.
- Penultimate destination slide: the talk's own conclusion, Q&A, contact page, or closing statement.
- Final destination slide: canonical rendered template source slide 13, unchanged.

Account for every source page. One source page may split into several destination slides and several source pages may merge into one destination slide. Record the mapping explicitly. Omission requires user approval.

## Element-Level PPTX Migration

Read [element-migration-quality.md](element-migration-quality.md) before editing.

- Preserve each textbox, shape, connector, image, table, chart, hyperlink, and note as an independent object.
- Detach or replace legacy masters/layouts without flattening local content.
- Delete only inventoried legacy background or template furniture.
- Use an approved summit background as a true background fill or bottom-most full-slide picture.
- Restyle imported objects in place when possible.
- Rasterize only one unsupported element at a time and record it in `rasterizedElements`.
- Complete `element-migration-ledger.json` with aggregate counts for one-to-one, split, or merge mappings.

## Brand Adaptation

- Remove obsolete event branding, old page chrome, duplicated summit Logos, and legacy full-slide overlays.
- Preserve customer/product/partner Logos when they are actual content and keep them outside summit Logo zones.
- Set title/display text to `腾讯体 W7`; set body/explanatory/chart-label text to `腾讯体 W3`.
- Apply orange-gold titles, white body text, and only the documented semantic color exceptions.
- Translate large theme blocks and charts conservatively into the approved palette. Do not perform blind global recoloring.
- After assigning Tencent fonts, reflow content and rerender. Font-name replacement alone does not prove layout safety.

For conservative package-preserving repairs on a copy:

```bash
python3 scripts/safe_repair_deck.py \
  --input /absolute/path/input.pptx \
  --output /absolute/path/repaired-copy.pptx \
  --report /absolute/path/repair-report.json
```

Add `--strict-colors` only after reviewing the dry-run report. Add `--repair-import-compatibility` when signed chart axis IDs prevent an importer from opening the package. Never overwrite the source.

## Content Fidelity

- Preserve wording, numbers, units, scales, citations, sources, notes, and hyperlinks unless editorial changes are requested.
- Preserve original-resolution source images where possible.
- Recompute editable charts from embedded or supplied data when possible.
- Record approved text changes, deletions, additions, and rasterization reasons in the ledger.
- Do not invent missing speaker details, portraits, logos, claims, data, or sources.

## Release Gate

1. Confirm the migration map covers every source page intended for body migration.
2. Complete the ledger; no `after`, notes, or hyperlink status may remain unresolved when applicable.
3. Run:

```bash
python3 scripts/validate_element_migration.py \
  --source /absolute/path/source.pptx \
  --destination /absolute/path/destination.pptx \
  --ledger /absolute/path/element-migration-ledger.json \
  --migration-map /absolute/path/migration-map.json
```

4. Run the companion tool's overflow checks, render all slides, and compare source/destination pages at full size.
5. Confirm the talk conclusion is penultimate and the canonical thank-you slide is final.
6. Run `python3 scripts/validate_deck_brand.py /absolute/path/destination.pptx`.
7. Fix every error, rerender, and rerun both validators before delivery.
