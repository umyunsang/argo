import hashlib
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ElementTree
from pathlib import Path

import pymupdf


root = Path(sys.argv[1]).resolve()
output_directory = Path(sys.argv[2]).resolve()
plan = root / ".planning/2026-09-05-thesis-two-column-revision"
manuscript = root / "paper/manuscript"
original_path = plan / "before/thesis-ko.qmd"
current_path = manuscript / "thesis-ko.qmd"
pdf_path = manuscript / "thesis-boundary-20260905.pdf"
original = original_path.read_text()
current = current_path.read_text()
document = pymupdf.open(pdf_path)
forbidden = re.compile(
    r"\b(?:ARGO|NAIS|Prime[ -]Agent|OpenResearch|Exa|pi-mono)\b"
    r"|/Users/|해커톤|프로토타입|마일스톤|로드맵|native implementation remains paused",
    re.IGNORECASE,
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publication_matches(text):
    return sorted(set(match.group(0) for match in forbidden.finditer(unicodedata.normalize("NFKC", text))))


def extract_invariants(text):
    return {
        "table_rows": re.findall(r"^\|.*\|$", text, re.MULTILINE),
        "table_identifiers": re.findall(r"\{#tbl-[\w-]+\}", text),
        "figure_identifiers": re.findall(r"\{#fig-[\w-]+", text),
        "citations_in_order": re.findall(r"@(?!fig-|tbl-|eq-)([A-Za-z][\w:-]+)", text),
        "display_equations": re.findall(r"\$\$.*?\$\$\s*\{#eq-[\w-]+\}", text, re.DOTALL),
        "inline_equations": re.findall(r"(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)", text, re.DOTALL),
        "evidence_cutoff": re.findall(r"2026년 9월 5일 05시 13분 55초\(한국 표준시\)", text),
    }


original_invariants = extract_invariants(original)
current_invariants = extract_invariants(current)
invariant_checks = {key: original_invariants[key] == value for key, value in current_invariants.items()}
abstract = re.search(r"# Abstract[^\n]*\n\n(.*?)\n\nKeyword", current, re.DOTALL).group(1)
keywords = re.search(r"^Keyword\s*:\s*(.+)$", current, re.MULTILINE).group(1).split(",")
captions = re.findall(r"^!\[(.*?)\]\(figures/[^\n]+", current, re.MULTILINE)
surfaces = {
    "qmd": publication_matches(current),
    "layout_source": publication_matches((manuscript / "thesis-template.typ").read_text()),
    "citation_style": publication_matches((manuscript / "thesis-publication.csl").read_text()),
    "bibliography": publication_matches((manuscript / "references-template.bib").read_text()),
    "pdf_text": publication_matches("\n".join(page.get_text() for page in document)),
    "pdf_metadata": publication_matches(json.dumps(document.metadata, ensure_ascii=False)),
    "pdf_xmp": publication_matches(document.get_xml_metadata()),
    "pdf_bookmarks": publication_matches(json.dumps(document.get_toc(), ensure_ascii=False)),
}
figure_checks = []
for relative_path in re.findall(r"\]\((figures/[^)]+\.svg)\)", current):
    path = manuscript / relative_path
    tree = ElementTree.fromstring(path.read_bytes())
    matches = publication_matches(path.read_text())
    surfaces[relative_path] = matches
    figure_checks.append({"path": relative_path, "sha256": digest(path), "xml_valid": True, "elements": len(list(tree.iter())), "excluded_terms": matches})
preserved = json.loads((plan / "preserved-artifacts-before.json").read_text())
changed_preserved = [relative_path for relative_path, expected in preserved.items() if not (root / relative_path).is_file() or digest(root / relative_path) != expected]
font_identifiers = sorted({font[0] for page in document for font in page.get_fonts(full=True) if font[0] > 0})
fonts_embedded = {str(identifier): bool(document.extract_font(identifier)[3]) for identifier in font_identifiers}
checks = {
    "publication_surfaces_clear": not any(surfaces.values()),
    "all_invariants_equal": all(invariant_checks.values()),
    "seven_tables": len(current_invariants["table_identifiers"]) == 7,
    "three_figures": len(figure_checks) == len(captions) == 3,
    "thirteen_citations": len(current_invariants["citations_in_order"]) == 13,
    "abstract_at_most_500_characters": len(abstract) <= 500,
    "at_most_five_keywords": len(keywords) <= 5,
    "concise_captions_at_most_60_characters": all(len(caption) <= 60 for caption in captions),
    "one_column_in_both_sources": "    columns: 1\n" in current and "  columns: 1," in (manuscript / "thesis-template.typ").read_text(),
    "publication_citation_style_selected": "csl: thesis-publication.csl\n" in current,
    "prior_artifacts_unchanged": not changed_preserved,
    "all_fonts_embedded": bool(fonts_embedded) and all(fonts_embedded.values()),
    "no_raster_images": all(not page.get_images() for page in document),
    "no_pdf_attachments": document.embfile_count() == 0,
}
report = {
    "scope": "Editorial boundary, source invariants and PDF asset checks; semantic and visual review are separate, not scientific validation or submission approval",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "qmd_sha256": digest(current_path),
    "pdf_sha256": digest(pdf_path),
    "page_count": len(document),
    "source_invariant_checks": invariant_checks,
    "invariant_counts": {key: len(value) for key, value in current_invariants.items()},
    "source_invariants": current_invariants,
    "excluded_term_matches_by_surface": surfaces,
    "abstract_characters_including_spaces": len(abstract),
    "keyword_count": len(keywords),
    "captions": [{"text": caption, "characters": len(caption)} for caption in captions],
    "figures": figure_checks,
    "fonts_embedded": fonts_embedded,
    "prior_artifact_count": len(preserved),
    "changed_prior_artifacts": changed_preserved,
    "research_executed": False,
}
output_directory.mkdir(parents=True, exist_ok=True)
(output_directory / "boundary-checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"status": report["status"], "checks": checks, "pages": len(document), "abstract_characters": len(abstract), "caption_characters": [len(caption) for caption in captions]}, ensure_ascii=False, indent=2))
sys.exit(0 if all(checks.values()) else 1)
