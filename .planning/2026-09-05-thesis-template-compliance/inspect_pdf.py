import collections
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf


pdf_path = Path(sys.argv[1]).resolve()
output_dir = Path(sys.argv[2]).resolve()
output_dir.mkdir(parents=True, exist_ok=True)
document = pymupdf.open(pdf_path)
page_reports = []
caption_locations = {}
reference_links = []
baseline_gaps = collections.Counter()
superscript_spans = []
overflows = []
all_text = []

for page in document:
    page_number = page.number + 1
    raw = page.get_text("dict")
    lines = [line for block in raw["blocks"] for line in block.get("lines", [])]
    spans = [span for line in lines for span in line["spans"]]
    text = unicodedata.normalize("NFKC", page.get_text(sort=True))
    all_text.append(f"\n--- Page {page_number} ---\n{text}")
    body_origins = []
    captions = []
    for line in lines:
        line_text = unicodedata.normalize("NFKC", "".join(span["text"] for span in line["spans"]))
        match = re.match(r"^(그림|표)\s*(\d+)\.", line_text)
        if match:
            label = f"{match[1]} {match[2]}"
            location = {"page": page_number, "bbox": list(line["bbox"]), "text": line_text}
            caption_locations[label] = location
            captions.append({"label": label, **location})
        if any(abs(span["size"] - 10.5) < 0.02 and re.search(r"[가-힣]", span["text"]) for span in line["spans"]):
            body_origins.append(round(line["spans"][0]["origin"][1], 3))
    ordered_origins = sorted(set(body_origins))
    for previous, current in zip(ordered_origins, ordered_origins[1:]):
        baseline_gaps[round(current - previous, 2)] += 1
    for block in page.get_text("rawdict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                for character in span["chars"]:
                    if character["c"].strip() and character["bbox"][1] < 778:
                        if character["bbox"][0] < 84.0 or character["bbox"][2] > 516.0:
                            overflows.append({"page": page_number, "text": character["c"], "bbox": list(character["bbox"])})
    for span in spans:
        if re.search(r"\[\d+(?:[–,\d ]*)\]", span["text"]) and span["size"] < 9:
            superscript_spans.append({"page": page_number, "text": span["text"], "size": span["size"], "origin": span["origin"]})
    for link in page.get_links():
        label_text = unicodedata.normalize("NFKC", page.get_textbox(link["from"]))
        match = re.search(r"(그림|표|식)\s*(\d+)", label_text)
        if match and "page" in link:
            reference_links.append({"label": f"{match[1]} {match[2]}", "source_page": page_number, "destination_page": link["page"] + 1, "destination": list(link["to"]), "source_bbox": list(link["from"])})
    footer = [line.strip() for line in text.splitlines() if re.fullmatch(r"- \d+ -", line.strip())]
    assert footer == [f"- {page_number} -"], (page_number, footer)
    assert abs(page.rect.width - 595.276) < 0.02 and abs(page.rect.height - 841.89) < 0.02
    page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(output_dir / f"page-{page_number:02}.png")
    page_reports.append({"page": page_number, "size_pt": list(page.rect)[2:], "characters_including_whitespace": len(text), "captions": captions, "footer": footer[0], "fonts": sorted(set((span["font"], round(span["size"], 2)) for span in spans))})

for link in reference_links:
    if link["label"] in caption_locations:
        link["actual_caption_page"] = caption_locations[link["label"]]["page"]
        link["destination_matches_actual_page"] = link["destination_page"] == link["actual_caption_page"]
        assert link["destination_matches_actual_page"], link

first_mentions = {}
for link in reference_links:
    first_mentions.setdefault(link["label"], link["source_page"])
placement = []
for label, caption in caption_locations.items():
    assert label in first_mentions, label
    delta = caption["page"] - first_mentions[label]
    assert delta in (0, 1), (label, delta)
    placement.append({"label": label, "first_mention_page": first_mentions[label], "caption_page": caption["page"], "relation": "same-page" if delta == 0 else "next-page; top placement requires visual check"})

assert len(caption_locations) == 10, caption_locations.keys()
assert baseline_gaps[21.0] > 200, baseline_gaps
assert len(superscript_spans) >= 13, superscript_spans
assert not overflows, overflows
report = {
    "scope": "PDF geometry, typography, numbering and cross-reference checks; not research efficacy or full submission compliance",
    "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
    "pages": page_reports,
    "metadata": document.metadata,
    "body_baseline_gaps_pt": dict(baseline_gaps.most_common()),
    "superscript_citations": superscript_spans,
    "reference_links": reference_links,
    "figure_table_placement": placement,
    "nonblank_character_horizontal_overflow": overflows,
    "horizontal_tolerance": "left >= 84 pt, right <= 516 pt; excludes whitespace and permits <= 3 pt optical punctuation overhang",
}
(output_dir / "pdf-checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
(output_dir / "all-text.txt").write_text("".join(all_text))
print(json.dumps({"pages": len(document), "captions": len(caption_locations), "links": len(reference_links), "baseline_21pt_gaps": baseline_gaps[21.0], "superscript_citations": len(superscript_spans), "placement": placement}, ensure_ascii=False, indent=2))
