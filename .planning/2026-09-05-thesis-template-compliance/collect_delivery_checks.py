import hashlib
import html
import json
import re
import subprocess
import unicodedata
import xml.etree.ElementTree as element_tree
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pymupdf


task_dir = Path(__file__).resolve().parent
repo_dir = task_dir.parents[1]
manuscript_dir = repo_dir / "paper/manuscript"
qa_dir = task_dir / "qa-final"
pdf_path = manuscript_dir / "thesis-template-20260905.pdf"
document = pymupdf.open(pdf_path)
pdf_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
qmd_path = manuscript_dir / "thesis-ko.qmd"
qmd_text = qmd_path.read_text()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name, payload):
    (qa_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def title_key(value):
    value = html.unescape(re.sub(r"<[^>]+>", "", value))
    value = unicodedata.normalize("NFKC", value).replace("’", "'")
    return re.sub(r"\s+", "", value).rstrip(",")


display_references = json.loads(subprocess.run(
    ["quarto", "pandoc", "references-template.bib", "--from=biblatex", "--to=csljson"],
    cwd=manuscript_dir, check=True, capture_output=True, text=True,
).stdout)
write_json("references-display.json", display_references)
references_by_id = {entry["id"]: entry for entry in display_references}
citation_order = list(dict.fromkeys(
    match for match in re.findall(r"@([\w:.-]+)", qmd_text)
    if match in references_by_id
))
assert len(citation_order) == len(references_by_id) == 13
pdf_text = unicodedata.normalize("NFKC", "\n".join(page.get_text() for page in document))
bibliography_heading = re.search(r"참\s*고\s*문\s*헌\s*\(References\)", pdf_text)
assert bibliography_heading
bibliography_text = pdf_text[bibliography_heading.end():]
rendered_titles = re.findall(r"“(.*?)”", bibliography_text, re.DOTALL)
assert len(rendered_titles) == 13
title_checks = []
for citation_id, rendered_title in zip(citation_order, rendered_titles):
    assert title_key(rendered_title) == title_key(references_by_id[citation_id]["title"]), citation_id
    title_checks.append({
        "key": citation_id,
        "rendered_title": re.sub(r"\s+", " ", rendered_title).rstrip(","),
        "display_title_match": True,
    })
reference_labels = re.findall(r"(?m)^\[(\d+)\]", bibliography_text)
assert reference_labels == [str(number) for number in range(1, 14)], reference_labels
assert "W.-T.Yih" in title_key(bibliography_text)
assert "W.-tauYih" not in title_key(bibliography_text)
write_json("final-title-checks.json", {
    "pdf_sha256": pdf_hash,
    "normalization": "PDF line wrapping, BibTeX protection markup, terminal CSL comma and straight/curly apostrophe only; letter case remains exact",
    "first_citation_order": citation_order,
    "reference_labels": reference_labels,
    "title_checks": title_checks,
    "hyphenated_initial": "W.-T. Yih",
})

body_counts = []
colored_text = []
colored_paths = []
raw_channel_differences = []
raster_counts = []
font_xrefs = set()
for page in document:
    spans = [span for block in page.get_text("dict")["blocks"]
             for line in block.get("lines", []) for span in line["spans"]]
    body = "".join(span["text"] for span in spans if abs(span["size"] - 10.5) < 0.02)
    body_counts.append({
        "page": page.number + 1,
        "body_10_5pt_characters_including_spaces": len(body),
        "body_10_5pt_characters_excluding_whitespace": len(re.sub(r"\s", "", body)),
    })
    for span in spans:
        channels = ((span["color"] >> 16) & 255, (span["color"] >> 8) & 255, span["color"] & 255)
        if len(set(channels)) != 1:
            colored_text.append({"page": page.number + 1, "text": span["text"], "rgb_8bit": channels})
    for drawing in page.get_drawings():
        for kind in ("color", "fill"):
            channels = drawing.get(kind)
            if channels is None:
                continue
            quantized = [round(channel * 255) for channel in channels]
            record = {"page": page.number + 1, "kind": kind, "raw_rgb": channels, "rgb_8bit": quantized}
            if max(channels) - min(channels) > 0.0001:
                raw_channel_differences.append(record)
            if len(set(quantized)) != 1:
                colored_paths.append(record)
    raster_counts.append({"page": page.number + 1, "raster_images": len(page.get_images())})
    font_xrefs.update(font[0] for font in page.get_fonts())
embedded_fonts = []
for font_xref in sorted(font_xrefs):
    name, extension, kind, font_bytes = document.extract_font(font_xref)
    assert font_bytes, name
    embedded_fonts.append({"name": name, "extension": extension, "kind": kind, "embedded_bytes": len(font_bytes)})
figure_dir = repo_dir / "paper/figures/template-20260905"
palettes = {}
for figure_path in sorted(figure_dir.glob("*.svg")):
    element_tree.parse(figure_path)
    colors = sorted(set(re.findall(r"#[0-9a-fA-F]{3,8}\b", figure_path.read_text())))
    for color in colors:
        value = color[1:]
        if len(value) == 3:
            value = "".join(character * 2 for character in value)
        assert len(value) == 6 and value[:2] == value[2:4] == value[4:6], color
    palettes[figure_path.name] = colors
assert len(palettes) == 3
assert not colored_text and not colored_paths and not any(row["raster_images"] for row in raster_counts)
write_json("additional-checks.json", {
    "scope": "Font embedding, vector/8-bit-neutral output and descriptive text density; not a page-length compliance decision",
    "pdf_sha256": pdf_hash,
    "density_definition": "Only extracted 10.5 pt spans, including headings/keywords of that size but excluding other-size caption/table/diagram/reference text; whitespace counts are separate. Not an institutional 1000-character counting rule.",
    "body_text_counts": body_counts,
    "non_grayscale_text": colored_text,
    "non_grayscale_paths_8bit": colored_paths,
    "raw_path_channel_differences": raw_channel_differences,
    "color_check_note": "Raw RGB differences over 0.0001 are retained; drawing colors must have equal channels after explicit round(channel*255). Source SVG palette is separately checked for exact grayscale.",
    "svg_source_directory": str(figure_dir.relative_to(repo_dir)),
    "svg_source_palettes": palettes,
    "raster_image_counts": raster_counts,
    "embedded_fonts": embedded_fonts,
})

abstract = qmd_text.split("# Abstract {.unnumbered}\n\n", 1)[1].split("\n\nKeyword :", 1)[0]
keywords = qmd_text.split("Keyword : ", 1)[1].split("\n", 1)[0].split(", ")
assert len(abstract) == 446 and len(keywords) == 5
provenance = json.loads((qa_dir / "source-provenance.json").read_text())
for relative_path, expected_hash in provenance["preserved_inputs"].items():
    assert digest(repo_dir / relative_path) == expected_hash, relative_path
for relative_path, expected_hash in provenance["figures_unchanged_from_two_column_edition"].items():
    assert digest(repo_dir / relative_path) == expected_hash, relative_path
reviewed_form = qmd_text.replace("bibliography: references-template.bib", "bibliography: references-current-evidence.bib", 1)
assert reviewed_form.count("](figures/template-20260905/") == 3
reviewed_form = reviewed_form.replace("](figures/template-20260905/", "](figures/current-evidence-20260905/")
lineage = provenance["independent_review_lineage"]
assert hashlib.sha256(reviewed_form.encode()).hexdigest() == lineage["reviewed_qmd_sha256"]
restored_body = reviewed_form.split("---", 2)[2].encode()
assert hashlib.sha256(restored_body).hexdigest() == "c1046ffa3b5d55a19ac9ecd730e1e3a7fb701068bea35a2c41e27597ea408170"
provenance.update({
    "verified_at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
    "pdf_sha256": pdf_hash,
    "pages": len(document),
    "source_files": {name: digest(manuscript_dir / name) for name in provenance["source_files"]},
    "display_figures": {str(path.relative_to(repo_dir)): digest(path) for path in sorted(figure_dir.glob("*.svg"))},
    "figure_display_change_scope": "Six exact case-only substitutions in separate SVG copies: four headings and two prose NO tokens. Geometry and semantic wording preserved. See figure-case-checks.json.",
    "abstract_characters_including_spaces": len(abstract),
    "keywords": keywords,
})
lineage.update({
    "final_qmd_sha256": digest(qmd_path),
    "only_subsequent_qmd_change": "Front matter bibliography path plus three figure paths pointing to sentence-case display copies; reversing exactly these four paths reconstructs the independently reviewed QMD hash.",
    "body_after_front_matter_sha256": hashlib.sha256(qmd_text.split("---", 2)[2].encode()).hexdigest(),
    "body_after_restoring_three_figure_paths_sha256": hashlib.sha256(restored_body).hexdigest(),
})
write_json("source-provenance.json", provenance)
print(json.dumps({"pages": len(document), "pdf_sha256": pdf_hash, "titles": len(title_checks), "embedded_fonts": len(embedded_fonts), "abstract_characters": len(abstract), "keywords": len(keywords), "scientific_body_lineage": "verified"}, ensure_ascii=False, indent=2))
