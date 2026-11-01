"""Create an editable plain-heading scaffold, not a pagination guarantee."""
import argparse
import math
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.text import WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor


def makeTemplate(path: Path, reserveMm: float = 45) -> None:
    """Reserve a full-width blank band inside the second A4 page's margins."""
    if not math.isfinite(reserveMm) or not 0 <= reserveMm <= 250:
        raise ValueError("reserveMm must be a finite value between 0 and 250")
    document = Document()
    normal = document.styles["Normal"]
    normal.font.name = "Arial Narrow"
    normal.font.size = Pt(6)
    normal._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "宋体")
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    normal.paragraph_format.line_spacing = Pt(6.7)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)
    heading = document.styles["Heading 1"]
    heading.font.name = "Arial Narrow"
    heading.font.size = Pt(7)
    heading.font.bold = True
    heading.font.color.rgb = RGBColor(0, 0, 0)
    heading.paragraph_format.space_before = Pt(2)
    heading.paragraph_format.space_after = Pt(1)
    heading.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    heading.paragraph_format.keep_with_next = True
    for style in (normal, heading):
        fonts = style._element.get_or_add_rPr().rFonts
        for attribute in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
            fonts.attrib.pop(qn(f"w:{attribute}"), None)
        fonts.set(qn("w:eastAsia"), "宋体")
        fonts.set(qn("w:cs"), "Arial Narrow")
    document.add_heading("1. Concepts and distinctions", level=1)
    document.add_paragraph("Replace with source-grounded definitions, conditions and useful contrasts.")
    document.add_heading("2. Formula and worked example", level=1)
    document.add_paragraph("Keep variable meanings, signs, units, calculation steps and the decision reason together.")
    document.add_section(WD_SECTION_START.NEW_PAGE)
    document.add_heading("3. Application and important table", level=1)
    document.add_paragraph("Replace this ORIGINAL sample; retain meaningful row/column headings and totals.")
    table = document.add_table(rows=4, cols=4)
    table.autofit = False
    for row, values in zip(table.rows, [("Group", "Pass", "Fail", "Total"), ("A", "30", "10", "40"), ("B", "15", "45", "60"), ("Total", "45", "55", "100")]):
        for cell, value in zip(row.cells, values):
            cell.text = value
            cell.width = Mm(15)
    for column in table.columns:
        column.width = Mm(15)
    document.add_heading("4. Exam cues", level=1)
    document.add_paragraph("Use brief reminders here. The blank band below is for later pasted material.")
    for index, section in enumerate(document.sections):
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(4)
        section.bottom_margin = Mm(4 + (reserveMm if index == 1 else 0))
        section.left_margin = Mm(5)
        section.right_margin = Mm(5)
        section.header_distance = Mm(0)
        section.footer_distance = Mm(0)
        columns = section._sectPr.find(qn("w:cols"))
        columns.set(qn("w:num"), "3")
        columns.set(qn("w:space"), "70")
        columns.set(qn("w:equalWidth"), "1")
    document.core_properties.title = "Two-page A4 exam cheatsheet scaffold"
    document.core_properties.author = ""
    document.core_properties.last_modified_by = ""
    # Exclusive creation protects an existing user's document.
    with path.open("xb") as stream:
        document.save(stream)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--reserve-mm", type=float, default=45)
    args = parser.parse_args()
    try:
        makeTemplate(args.output, args.reserve_mm)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Cannot create template: {error}\n")
    print(f"Created {args.output}; render to PDF and review before use.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
