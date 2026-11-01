"""Check physical PDF page constraints; visual legibility is a separate review."""
import argparse
import json
import math
from pathlib import Path

from pypdf import PdfReader


A4_WIDTH_PT = 595.276
A4_HEIGHT_PT = 841.89
TOLERANCE_PT = 2


def isPortraitA4(page) -> bool:
    unit = float(page.user_unit)
    if not math.isfinite(unit) or unit <= 0 or page.rotation % 360 != 0:
        return False
    for box in (page.mediabox, page.cropbox):
        width, height = float(box.width) * unit, float(box.height) * unit
        if not math.isfinite(width) or not math.isfinite(height):
            return False
        if abs(width - A4_WIDTH_PT) > TOLERANCE_PT or abs(height - A4_HEIGHT_PT) > TOLERANCE_PT:
            return False
    return all(abs(float(a) - float(b)) * unit <= TOLERANCE_PT for a, b in zip(page.mediabox, page.cropbox))


def checkPdf(path: Path, maxPages: int = 2) -> dict:
    """Reject empty, over-limit, cropped, rotated or non-portrait-A4 output."""
    if maxPages not in (1, 2):
        raise ValueError("maxPages must be 1 or 2")
    reader = PdfReader(path)
    count = len(reader.pages)
    countIssues = [] if 1 <= count <= maxPages else [f"Expected 1..{maxPages} pages; found {count}"]
    sizeIssues = [
        f"Page {index}: expected uncropped portrait A4 with zero rotation"
        for index, page in enumerate(reader.pages, start=1)
        if not isPortraitA4(page)
    ]
    issues = countIssues + sizeIssues
    return {
        "compliant": not issues,
        "page_count": count,
        "max_pages": maxPages,
        "issues": issues,
        "visual_review": "required",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--max-pages", type=int, choices=(1, 2), default=2)
    args = parser.parse_args()
    try:
        result = checkPdf(args.pdf, args.max_pages)
    except Exception as error:
        print(json.dumps({"compliant": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["compliant"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
