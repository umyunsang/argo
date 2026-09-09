import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pymupdf


original_path = Path(sys.argv[1]).resolve()
rebuilt_path = Path(sys.argv[2]).resolve()
archive_path = Path(sys.argv[3]).resolve()
output_path = Path(sys.argv[4]).resolve()
original = pymupdf.open(original_path)
rebuilt = pymupdf.open(rebuilt_path)
assert len(original) == len(rebuilt) == 18
page_checks = []
for page_index in range(len(original)):
    original_page = original[page_index]
    rebuilt_page = rebuilt[page_index]
    original_pixmap = original_page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
    rebuilt_pixmap = rebuilt_page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
    original_pixels = hashlib.sha256(original_pixmap.samples).hexdigest()
    rebuilt_pixels = hashlib.sha256(rebuilt_pixmap.samples).hexdigest()
    check = {
        "page": page_index + 1,
        "a4_rectangle_equal": original_page.rect == rebuilt_page.rect,
        "text_equal": original_page.get_text() == rebuilt_page.get_text(),
        "text_spans_and_geometry_equal": original_page.get_text("dict") == rebuilt_page.get_text("dict"),
        "pixels_equal": original_pixels == rebuilt_pixels,
        "original_pixel_sha256": original_pixels,
        "rebuilt_pixel_sha256": rebuilt_pixels,
    }
    assert all(check[key] for key in (
        "a4_rectangle_equal", "text_equal", "text_spans_and_geometry_equal", "pixels_equal"
    )), check
    page_checks.append(check)
output_path.write_text(json.dumps({
    "scope": "Fresh local extraction of the editable ZIP, Quarto render without execution, then full-page text, geometry and raster equivalence; not research reproduction",
    "verified_at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
    "result": "PASS",
    "command": "quarto render thesis-ko.qmd --to typst --no-execute",
    "original_pdf_sha256": hashlib.sha256(original_path.read_bytes()).hexdigest(),
    "rebuilt_pdf_sha256": hashlib.sha256(rebuilt_path.read_bytes()).hexdigest(),
    "archive_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
    "pdf_bytes_equal": original_path.read_bytes() == rebuilt_path.read_bytes(),
    "binary_comparison_note": "PDF metadata such as creation timestamps may differ; every page must match in text, span geometry and rendered pixels.",
    "rebuilt_pdf_path": str(rebuilt_path),
    "pages": page_checks,
    "research_executed": False,
    "font_scope": "Same locally verified macOS font environment; no claim of identical pagination with substitute fonts",
}, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"result": "PASS", "pages": len(page_checks), "output": str(output_path)}, ensure_ascii=False))
