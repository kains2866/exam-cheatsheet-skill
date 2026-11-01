# Project instructions

- This repository ships a portable agent skill, two small Python helpers and original tests.
- Main entry: `skills/build-exam-cheatsheet/SKILL.md`; keep it concise and link detailed references.
- The default output is at most two portrait A4 pages. Headings are plain text, no filled bands. Reserve tables/images before prose.
- No real course documents, student information, local absolute paths, credentials or generated test artifacts in commits.
- Python 3.10+, python-docx and pypdf. Test: `python -m unittest discover -s tests -v`.
- Test meaningful behavior before changing scripts. Render Word output and inspect page images after layout changes.
- Packaging includes only `skills/build-exam-cheatsheet/`, with that folder at archive root.
- Keep project design/plans and release artifacts outside this Git repository, in sibling `../docs/` and `../assets/`.
- Public release requires user authorization; this initial 0.1.0 publication is authorized in the creation chat. Later releases require their own applicable authorization.
