# Source Intake

Use the lightest companion capability that can faithfully inspect the source. Always run `scripts/summit_adapter.py` first when the format is supported.

## PPTX

- Inventory slide order, masters/layouts, local objects, grouped objects, notes, hyperlinks, charts, tables, media, and embedded files.
- Detect legacy full-slide overlays separately from true content images.
- Preserve editable local objects. Do not use a rendered slide as the migrated body.
- Treat signed negative chart axis IDs as an importer compatibility issue. Repair only an output copy.

## Legacy PPT

- Preserve the source unchanged.
- Convert a copy to PPTX with PowerPoint, WPS, or LibreOffice.
- Compare the converted render with the original before migration because old chart, font, animation, and OLE behavior may change.

## PDF

- Render every page for visual evidence and extract selectable text first.
- Use OCR only where necessary and verify names, numbers, units, and punctuation against the page.
- Rebuild editable text, tables, and diagrams when feasible.
- Preserve a high-resolution crop only for an irrecoverable individual visual. Record the editability limitation.

## HTML And Markdown

- Preserve heading hierarchy, lists, code, images, links, tables, citations, and source order.
- Resolve local assets relative to the source file.
- Let the companion presentation-authoring Skill decide pagination and slide structure.
- Do not claim this template Skill researched, outlined, or independently generated the content.

## Missing Information

- Never invent speaker names, job titles, portraits, organization names, data, citations, or logos.
- Leave the optional speaker page blank when verified profile inputs are unavailable.
- Mark unreadable or unsupported source elements for review instead of silently omitting them.
