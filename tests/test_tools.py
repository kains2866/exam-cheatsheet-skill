"""Behavioral tests for page limits and the editable Word layout."""
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from docx import Document
from docx.oxml.ns import qn
from pypdf import PdfWriter
from pypdf.generic import FloatObject, NameObject


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "build-exam-cheatsheet" / "scripts"


def loadTool(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PdfTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "sheet.pdf"

    def writePdf(self, count=2, width=595.276, height=841.89, rotation=0):
        writer = PdfWriter()
        for _ in range(count):
            page = writer.add_blank_page(width, height)
            if rotation:
                page.rotate(rotation)
        writer.write(self.path)

    def test_two_a4_pages_need_separate_visual_review(self):
        self.writePdf()
        result = loadTool("check_pdf").checkPdf(self.path)
        self.assertTrue(result["compliant"])
        self.assertEqual(result["page_count"], 2)
        self.assertEqual(result["visual_review"], "required")

    def test_three_pages_rejected(self):
        self.writePdf(count=3)
        result = loadTool("check_pdf").checkPdf(self.path)
        self.assertFalse(result["compliant"])
        self.assertTrue(result["issues"])

    def test_letter_landscape_and_rotated_pages_rejected(self):
        for width, height, rotation in [(612, 792, 0), (841.89, 595.276, 0), (595.276, 841.89, 90)]:
            with self.subTest(size=(width, height), rotation=rotation):
                self.writePdf(width=width, height=height, rotation=rotation)
                self.assertFalse(loadTool("check_pdf").checkPdf(self.path)["compliant"])

    def test_cropped_a4_rejected(self):
        writer = PdfWriter()
        page = writer.add_blank_page(595.276, 841.89)
        page.cropbox.upper_right = (400, 700)
        writer.write(self.path)
        self.assertFalse(loadTool("check_pdf").checkPdf(self.path)["compliant"])

    def test_pdf_user_unit_changes_physical_dimensions(self):
        writer = PdfWriter()
        page = writer.add_blank_page(595.276, 841.89)
        page[NameObject("/UserUnit")] = FloatObject(2)
        writer.write(self.path)
        self.assertFalse(loadTool("check_pdf").checkPdf(self.path)["compliant"])
        writer = PdfWriter()
        page = writer.add_blank_page(595.276 / 2, 841.89 / 2)
        page[NameObject("/UserUnit")] = FloatObject(2)
        writer.write(self.path)
        self.assertTrue(loadTool("check_pdf").checkPdf(self.path)["compliant"])
        for unit in (0, -1):
            page[NameObject("/UserUnit")] = FloatObject(unit)
            writer.write(self.path)
            self.assertFalse(loadTool("check_pdf").checkPdf(self.path)["compliant"])

    def test_empty_pdf_and_invalid_limits_rejected(self):
        self.writePdf(count=0)
        self.assertFalse(loadTool("check_pdf").checkPdf(self.path)["compliant"])
        for limit in [0, 3, -1]:
            with self.assertRaises(ValueError):
                loadTool("check_pdf").checkPdf(self.path, maxPages=limit)

    def test_cli_errors_are_explicit_and_machine_readable(self):
        self.writePdf(count=3)
        result = subprocess.run([sys.executable, str(SCRIPTS / "check_pdf.py"), str(self.path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["compliant"])
        self.path.write_text("invalid PDF")
        result = subprocess.run([sys.executable, str(SCRIPTS / "check_pdf.py"), str(self.path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("error", json.loads(result.stdout))

    def test_main_exit_codes(self):
        tool = loadTool("check_pdf")
        for count, expected in [(2, 0), (3, 1)]:
            self.writePdf(count=count)
            with patch.object(sys, "argv", ["check_pdf.py", str(self.path)]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(tool.main(), expected)
        with patch.object(sys, "argv", ["check_pdf.py", str(self.path.parent / "missing.pdf")]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tool.main(), 2)


class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "sheet.docx"

    def test_template_has_plain_headings_three_columns_and_reserved_area(self):
        loadTool("make_template").makeTemplate(self.path)
        document = Document(self.path)
        self.assertEqual(len(document.sections), 2)
        for section in document.sections:
            self.assertAlmostEqual(section.page_width.mm, 210, delta=0.1)
            self.assertAlmostEqual(section.page_height.mm, 297, delta=0.1)
            self.assertEqual(section._sectPr.find(qn("w:cols")).get(qn("w:num")), "3")
        self.assertAlmostEqual(document.sections[0].bottom_margin.mm, 4, delta=0.1)
        self.assertAlmostEqual(document.sections[1].bottom_margin.mm, 49, delta=0.1)
        self.assertEqual(document.styles["Normal"].font.name, "Arial Narrow")
        self.assertEqual(document.styles["Normal"].font.size.pt, 6)
        self.assertEqual(document.styles["Heading 1"].font.size.pt, 7)
        self.assertTrue(document.styles["Heading 1"].font.bold)
        fonts = document.styles["Heading 1"]._element.find(qn("w:rPr")).find(qn("w:rFonts"))
        self.assertIsNone(fonts.get(qn("w:asciiTheme")))
        self.assertFalse(document._element.xpath(".//w:shd"))
        self.assertTrue(document.tables)

    def test_reserve_is_configurable_and_output_is_not_overwritten(self):
        tool = loadTool("make_template")
        tool.makeTemplate(self.path, reserveMm=60)
        self.assertAlmostEqual(Document(self.path).sections[1].bottom_margin.mm, 64, delta=0.1)
        with self.assertRaises(FileExistsError):
            tool.makeTemplate(self.path)
        for reserve in [-1, 251, float("nan")]:
            with self.assertRaises(ValueError):
                tool.makeTemplate(Path(self.temp.name) / "bad.docx", reserveMm=reserve)

    def test_template_cli(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "make_template.py"), str(self.path), "--reserve-mm", "30"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.path.exists())
        result = subprocess.run([sys.executable, str(SCRIPTS / "make_template.py"), str(self.path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)

    def test_template_main_propagates_creation_errors(self):
        tool = loadTool("make_template")
        with patch.object(sys, "argv", ["make_template.py", str(self.path)]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tool.main(), 0)
        with patch.object(sys, "argv", ["make_template.py", str(self.path)]), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                tool.main()
            self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
