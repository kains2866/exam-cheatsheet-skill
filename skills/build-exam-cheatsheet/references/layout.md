# Compact plain-text A4 preset

This preset reflects a dense English reference-sheet style, revised to use plain headings. User-provided exam/template requirements take precedence. The 45mm reserve below is a configurable starting point, not a measurement from a reference document.

| Setting | Default |
|---|---|
| Printable document | At most 2 A4 portrait pages, 210×297mm |
| Margins | Top/bottom 4mm, left/right 5mm |
| Body | Three equal columns, gap 70 twips ≈1.23mm |
| Font | Arial Narrow; explicit 宋体 for Chinese |
| Body size/line spacing | 6pt / exact 6.7pt; no default paragraph gap |
| Headings | 7pt, black, bold; optional numbering/italic; no fill |
| Heading spacing | Before 2pt, after 1pt; keep with following content |
| Emphasis | Bold/italic first; sparse red text if useful; usable in grayscale |
| Later paste-in space | Default full-width 45mm band at foot of page 2, inside the 2-page budget |

Check font availability before generation; don't silently substitute Arial Narrow. Describe an available substitute and recheck wrapping. Verify mixed Chinese, equations, superscripts and symbol glyphs at the final size. A 6pt preset is not proof of legibility; complex figures may require larger text and less prose. Check that fixed line spacing doesn't clip math/Chinese glyphs.

## Create a scaffold

Run from the skill directory with Python 3.10+, `python-docx` and `pypdf` available:

```sh
python scripts/make_template.py sheet.docx --reserve-mm 45
```

If the dependencies are absent, install `scripts/requirements.txt` in a suitable Python environment before running the helpers. Do not install packages into an unrelated project as a side effect of making notes.

This creates **sample content to replace**, not a completed cheatsheet. It uses two page sections and enlarges page 2's bottom margin by the reserved height, leaving a truly blank full-width band. Existing output is refused. It does not measure your final content or guarantee pagination. Both tables and images require final rendering. To paste into the reserved band later, reduce page 2's extra bottom margin by the chosen height and insert the material; then render/recheck the edited document. Don't append another page.

Use available Word/PDF tooling to render; one option, when LibreOffice is installed, is:

```sh
soffice --headless --convert-to pdf --outdir preview sheet.docx
python scripts/check_pdf.py preview/sheet.pdf
```

Use a new output directory to avoid reading a stale PDF after failed conversion. Exit codes: 0 = physical constraints pass, **visual review still required**; 1 = page count/size fails; 2 = file/read error. PDF checks cover MediaBox, CropBox and rotation. They don't prove the PDF matches the intended final DOCX, detect blank extra content, or judge legibility. Record the render command and output timestamp so the final Word/PDF pair is identifiable.

## Tables and diagrams

Plan required assets first. Use native Word tables when possible; preserve meaningful headers, axis/category labels, cell relations, totals, legends and units. A full-width continuous one-column section can accommodate an important wide table; restore columns afterward and re-render because section breaks affect balancing. Thin table borders may aid reading; heading color bands are unnecessary.

Faithful transcription of a fully legible source table into native Word cells is ordinary document composition: verify every label/value against the source. This differs from redrawing a diagram or reconstructing unclear/missing information, which requires clarification and user approval. Never infer an unreadable cell from surrounding values.

For pictures, preserve aspect ratio and crop only empty margins. Prefer source PDF/vector export or the original high-resolution image to a screenshot. At scale factor `s`, a label originally `f` points tall is effectively `f*s` points. Inspect at print scale and compare against readable adjacent body text. Pixel count or DPI alone doesn't establish legibility, and upscaling doesn't restore lost letter detail.

If a figure fails: widen its area, reduce surrounding prose, request a clearer original, or ask whether to recreate it faithfully with editable text/vectors. Never change values/arrows/labels to make it fit or redraw on implied approval. Leave an explicit unresolved gap if the figure cannot be read reliably.

## Final acceptance

- Final Word rendered to fresh PDF; 1–2 portrait A4 pages, no third page.
- Every page visually inspected, including the bottom/right edges and column transitions.
- Plain readable headings; no filled bands; complete formula glyphs and table labels.
- Important table preserved; pasted images readable at actual size; agreed blank area remains.
- After any edit, substitution or reconstruction, render and validate again.
- Deliver separate source coverage notes, not an extra page in the cheatsheet.
