import hashlib
import json
import sys
from pathlib import Path

import pymupdf


root = Path(sys.argv[1]).resolve()
plan = root / ".planning/2026-09-05-thesis-two-column-revision"
manuscript = root / "paper/manuscript"
current_qmd = manuscript / "thesis-ko.qmd"
reviewed_qmd = plan / "semantic-reviewed.qmd"
review = json.loads((plan / "publication-boundary-review.json").read_text())
figure_before = plan / "figure-worker-candidate.svg"
figure_after = root / "paper/figures/thesis-boundary-20260905/fig1-research-agent-architecture.svg"
old_phrase = "이 관측 결과를 새 실험의 과학적 타당성 전반과 동일시하지 않으며"
new_phrase = "향후 얻을 관측 결과를 새 실험의 과학적 타당성 전반과 동일시하지 않으며"
old_csl_reference = "csl: thesis-template.csl\n"
new_csl_reference = "csl: thesis-publication.csl\n"
original_csl = (manuscript / "thesis-template.csl").read_text()
publication_csl = (manuscript / "thesis-publication.csl").read_text()
expected_csl = original_csl.replace("<title>ARGO graduation-thesis template</title>", "<title>Graduation-thesis template</title>").replace("urn:argo:csl:thesis-template", "urn:thesis:csl:graduation-template")
figure_replacements = [
    ("Research refinement and workflow revision", "Research refinement and harness refinement"),
    (">Workflow revision<", ">Harness refinement<"),
    (">Compare workflow choices<", ">Compare retrieval, memory and tools<"),
]
figure_expected = figure_before.read_text()
for before_text, after_text in figure_replacements:
    assert figure_expected.count(before_text) == 1
    figure_expected = figure_expected.replace(before_text, after_text)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks = {
    "reviewed_qmd_hash_matches_review": digest(reviewed_qmd) == review["inputs"]["current_qmd"]["sha256"],
    "review_has_no_must_fix": not review["must_fix"],
    "qmd_only_root_tense_and_csl_reference": reviewed_qmd.read_text().count(old_phrase) == 1
    and reviewed_qmd.read_text().count(old_csl_reference) == 1
    and reviewed_qmd.read_text().replace(old_phrase, new_phrase).replace(old_csl_reference, new_csl_reference) == current_qmd.read_text(),
    "citation_style_only_neutral_identity_metadata": original_csl.count("<title>ARGO graduation-thesis template</title>") == 1
    and original_csl.count("urn:argo:csl:thesis-template") == 2
    and expected_csl == publication_csl,
    "figure_only_three_text_replacements": figure_expected == figure_after.read_text(),
}
worker_checks = json.loads((plan / "figure-boundary-checks.json").read_text())
checks["figure_worker_candidate_was_pass"] = worker_checks["status"] == "PASS"
original_path = plan / "visual-candidate-before-final.pdf"
final_path = manuscript / "thesis-boundary-20260905.pdf"
original_pdf = pymupdf.open(original_path)
final_pdf = pymupdf.open(final_path)
checks["page_count_stable"] = len(original_pdf) == len(final_pdf) == 18
page_checks = []
for page_index in range(min(len(original_pdf), len(final_pdf))):
    original_page = original_pdf[page_index]
    final_page = final_pdf[page_index]
    original_pixels = original_page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False).samples
    final_pixels = final_page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False).samples
    page_checks.append({
        "page": page_index + 1,
        "text_equal": original_page.get_text() == final_page.get_text(),
        "text_spans_and_geometry_equal": original_page.get_text("dict") == final_page.get_text("dict"),
        "pixels_equal": original_pixels == final_pixels,
        "final_pixel_sha256": hashlib.sha256(final_pixels).hexdigest(),
    })
changed_pages = [entry["page"] for entry in page_checks if not entry["pixels_equal"]]
report = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "scope": "Exact root integration delta after independent semantic review; no new scientific claims or measurement results. Visual inspection of changed pages remains a separate root check.",
    "checks": checks,
    "reviewed_qmd_sha256": digest(reviewed_qmd),
    "final_qmd_sha256": digest(current_qmd),
    "figure_worker_candidate_sha256": digest(figure_before),
    "final_architecture_figure_sha256": digest(figure_after),
    "final_pdf_sha256": digest(final_path),
    "qmd_replacement": {"before": old_phrase, "after": new_phrase},
    "citation_style_reference_replacement": {"before": old_csl_reference, "after": new_csl_reference},
    "publication_csl_sha256": digest(manuscript / "thesis-publication.csl"),
    "figure_replacements": figure_replacements,
    "changed_pages_requiring_visual_recheck": changed_pages,
    "pages": page_checks,
}
(plan / "qa/root-integration-checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"status": report["status"], "checks": checks, "changed_pages": changed_pages}, ensure_ascii=False))
sys.exit(0 if all(checks.values()) else 1)
