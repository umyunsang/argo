from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata

import pymupdf
from PIL import Image, ImageDraw


root = Path(__file__).resolve().parents[2]
work = Path(__file__).resolve().parent
output = work / "qa-final"
output.mkdir(exist_ok=True)
manuscript = root / "paper/manuscript/thesis-ko.qmd"
baseline = root / "paper/manuscript/versions/2026-09-05-two-column/before/thesis-ko.qmd"
pdf = root / "paper/manuscript/thesis-two-column-20260905.pdf"
old_pdf = root / "paper/manuscript/versions/2026-09-05-current-evidence/thesis-current-evidence-20260905.pdf"


def normalized_body(source):
    body = source.split("---", 2)[2]
    body = body.replace("#pagebreak()\n", "")
    body = re.sub(r"\\(?:begin|end)\{aligned\}", "", body)
    body = body.replace("\\\\", "").replace("\\qquad", "").replace("&", "")
    body = body.replace("\\left[", "[").replace("\\right]", "]")
    body = body.replace("\\Big[", "[").replace("\\Big]", "]")
    return re.sub(r"\s+", "", body)


def text_inventory(document):
    characters = Counter()
    for page in document:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                if line["bbox"][1] > page.rect.height - 55:
                    continue
                text = "".join(span["text"] for span in line["spans"])
                characters.update(character for character in unicodedata.normalize("NFKC", text) if character.isalnum())
    return characters


current = manuscript.read_text()
previous = baseline.read_text()
assert normalized_body(current) == normalized_body(previous), "Scientific content changed"
document = pymupdf.open(pdf)
old_document = pymupdf.open(old_pdf)
previous_inventory = text_inventory(old_document)
current_inventory = text_inventory(document)
page_results = []
outside = []
for index, page in enumerate(document):
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4), alpha=False)
    pixmap.save(output / f"page-{index + 1:02d}.png")
    left = right = 0
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            bounds = line["bbox"]
            if bounds[0] < 0 or bounds[1] < 0 or bounds[2] > page.rect.width + 0.5 or bounds[3] > page.rect.height + 0.5:
                outside.append({"page": index + 1, "bbox": bounds})
            body_spans = [span for span in line["spans"] if 9.9 < span["size"] < 10.1]
            if body_spans:
                left += bounds[0] < 290 and bounds[2] < 300
                right += bounds[0] > 299
    page_results.append({"page": index + 1, "size": [page.rect.width, page.rect.height], "left_body_lines": left, "right_body_lines": right})

for first in range(0, len(document), 4):
    sheet = Image.new("RGB", (1200, 1750), "#dddddd")
    draw = ImageDraw.Draw(sheet)
    for offset in range(min(4, len(document) - first)):
        image = Image.open(output / f"page-{first + offset + 1:02d}.png")
        image.thumbnail((570, 820))
        left = 15 + (offset % 2) * 600
        top = 32 + (offset // 2) * 870
        sheet.paste(image, (left, top))
        draw.text((left, top - 22), f"Page {first + offset + 1}", fill="black")
    sheet.save(output / f"contact-{first + 1:02d}-{min(first + 4, len(document)):02d}.png")

results = {
    "pdf": str(pdf.relative_to(root)),
    "pdf_sha256": sha256(pdf.read_bytes()).hexdigest(),
    "page_count": len(document),
    "source_scientific_content_preserved": True,
    "normalization_scope": "Only frontmatter, bibliography page break and equation alignment/delimiter sizing ignored",
    "citation_keys_preserved": set(re.findall(r"@([A-Za-z][\w:-]+)", current)) == set(re.findall(r"@([A-Za-z][\w:-]+)", previous)),
    "figure_count": len(re.findall(r"\{#fig-", current)),
    "table_count": len(re.findall(r"\{#tbl-", current)),
    "alphanumeric_missing": dict(previous_inventory - current_inventory),
    "alphanumeric_added": dict(current_inventory - previous_inventory),
    "outside_page_lines": outside,
    "pages": page_results,
}
(output / "checks.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({key: value for key, value in results.items() if key != "pages"}, ensure_ascii=False, indent=2))
