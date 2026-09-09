from collections import Counter
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import json
import re
import shutil
import subprocess


root = Path(__file__).resolve().parents[2]
plan = root / ".planning/2026-09-05-thesis-evidence-draft"
destination = root / "paper/manuscript/evidence/current-evidence-20260905"
destination.mkdir(parents=True, exist_ok=True)


def digest(filename):
    return sha256(filename.read_bytes()).hexdigest()


def save_json(filename, data):
    filename.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def retain(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    assert digest(source) == digest(target)
    return {
        "original_path": str(source.relative_to(root)),
        "frozen_path": str(target.relative_to(destination)),
        "sha256": digest(target),
        "bytes": target.stat().st_size,
    }


source_specs = [
    ("besta2024got", "root-sources/besta2024.pdf", "AAAI 2024", "Abstract and section 3: architecture, graph of operations versus graph reasoning state", "Graph representations motivate explicit dependencies; graph presence alone does not establish provenance or efficacy."),
    ("hu2025adas", "root-sources/hu2025.pdf", "ICLR 2025", "Section 3: archive, candidate generation, feedback, evaluation; limitations", "Iterative architecture search motivates separate harness versions; it does not validate this proposed dual-refinement design."),
    ("baek-etal-2025-researchagent", "domain-sources/researchagent-naacl2025.pdf", "NAACL 2025", "Physical pages 4-6 and 10: method, evaluation and limitations", "Iterative research-idea generation is not the same outcome as scientific experiment success."),
    ("chen2025scienceagentbench", "domain-sources/scienceagentbench-iclr2025.pdf", "ICLR 2025", "Section 2 and Appendix A: benchmark construction and task/evaluation contract", "102 tasks from 44 papers motivate executable task contracts; those tasks do not cover the entire autonomous research lifecycle."),
    ("pmlr-v267-huang25n", "domain-sources/popper-icml2025.pdf", "ICML 2025", "Sections 2.3-2.4, Remark 5 and footnote 2", "Sequential falsification requires information-history and validity assumptions; no blanket transfer of guarantees."),
    ("Asai2026", "domain-sources/openscholar-nature2026.pdf", "Nature 2026", "Physical page 6 limitations and pages 8-9 methods", "Citation-grounded synthesis motivates claim-to-passage checking; it does not establish downstream research-decision validity."),
    ("astabench2026", "domain-sources/astabench-iclr2026.pdf", "ICLR 2026", "Physical page 5 sections 3/4.1; page 10 section 6; pages 41-42 Appendix E.9-E.10", "Stage-specific and end-to-end research benchmarks motivate explicit scope; task domains and provision conditions still require matching."),
    ("agarwal2021statistical", "statistics-sources/s2-agarwal2021.pdf", "NeurIPS 2021", "Physical pages 2-3 section 2; pages 5-6 section 4.1; Figure 6 caption, not quantitative plot reading", "Few-run uncertainty motivates reporting task and run variation; RL resampling choices are not transferred without checking the sampling design."),
    ("dror2018hitchhikers", "statistics-sources/s3-dror2018.pdf", "ACL 2018", "Physical pages 5-6 (printed 1387-1388), section 3.2.2; page 8 (1390), section 5", "Test selection depends on measurement level, pairing and dependence; no test was run on current instrument counts."),
    ("nosek2018preregistration", "statistics-sources/s4-pmc.html", "PNAS 2018", "Retained full-text HTML sections s3-s8 and s20; PDF access attempt was not a valid PDF", "Separate exploratory choices from later confirmation; current hypotheses are proposals, not completed preregistration."),
    ("yang2024sweagent", "fairness-sources/R2-swe-agent-2024.pdf", "NeurIPS 2024", "Physical pages 5-6: sections 4 and 5.1", "Agent interfaces and history handling can be meaningful interventions; cost/information matching here is our proposed comparison contract."),
    ("zheng2023judge", "fairness-sources/R3-llm-judge-2023.pdf", "NeurIPS 2023", "Physical pages 4-6: sections 3.3-3.4", "Position, verbosity and reasoning limitations motivate separating preference ratings from factual/scientific validity; universal self-enhancement is not asserted."),
    ("JMLR:v22:20-303", "fairness-sources/R4-reproducibility-2021.pdf", "JMLR 2021", "Section 2.5 pages 5-6; section 4 page 10; section 6 pages 12-13; Figure 8 page 20", "Methods, resources and artifacts support reproducibility reporting; disclosure does not itself establish a successful replication."),
]
bibliography = (root / "paper/manuscript/references-current-evidence.bib").read_text()
bib_matches = list(re.finditer(r"(?m)^@\w+\{([^,]+),", bibliography))
bib_blocks = {
    match.group(1): bibliography[match.start():bib_matches[index + 1].start() if index + 1 < len(bib_matches) else len(bibliography)]
    for index, match in enumerate(bib_matches)
}
assert set(bib_blocks) == {spec[0] for spec in source_specs}
sources = []
for key, relative_file, venue, locator, application in source_specs:
    source = plan / relative_file
    slug = re.sub(r"[^a-zA-Z0-9-]+", "-", key)
    record = retain(source, destination / "sources" / (slug + source.suffix))
    for field in ["url", "doi", "year"]:
        match = re.search(r"\b" + field + r"\s*=\s*[\{\"]([^}\"]+)", bib_blocks[key], re.I)
        if match:
            record[field] = match.group(1)
    record.update({"citation_key": key, "publication": venue, "publication_status": "published", "read_scope": "selected_full_text_sections", "locator": locator, "application_and_limit": application})
    extracted = source.with_suffix(".txt")
    if source.suffix == ".html":
        extracted = source.parent / "s4-pmc-html.txt"
    if extracted.exists():
        record["text_extraction"] = retain(extracted, destination / "sources" / (slug + ".txt"))
    sources.append(record)
save_json(destination / "sources.json", {"schema_version": 1, "source_count": len(sources), "full_papers_read_cover_to_cover": False, "sources": sources})

packet = root / ".planning/2026-09-04-argo-paper-research-audit/review-packet"
closure_file = packet / "oracle-isolation-v4/stage0-observer-closure.json"
closure = json.loads(closure_file.read_text())
receipt_records = {"stage0_closure": retain(closure_file, destination / "receipts/stage0-closure.json")}
for section in ["import_probe", "environment_parity", "task_scorers", "runtime_policy"]:
    for prefix in ["receipt", "validation"]:
        path_key = prefix + "_path"
        if path_key not in closure[section]:
            continue
        source = Path(closure[section][path_key])
        assert digest(source) == closure[section][prefix + "_sha256"], str(source)
        receipt_id = section + "_" + prefix
        receipt_records[receipt_id] = retain(source, destination / "receipts" / (receipt_id + ".json"))
overlay = packet / "03-admissibility-corrections.json"
receipt_records["legacy_editorial_overlay"] = retain(overlay, destination / "receipts/legacy-editorial-overlay.json")
receipt_records["legacy_editorial_overlay"]["status"] = "proposed_unapplied_overlay_not_canonical_admission_state"

scorer = json.loads((destination / receipt_records["task_scorers_receipt"]["frozen_path"]).read_text())
task_rows = []
domain_counts = Counter()
for task in scorer["tasks"]:
    runs = task["runs"]
    assert len(runs) == 6
    assert all(run["score"] == run["expected_score"] and run["exit_code"] == 0 and not run["timed_out"] for run in runs)
    fixtures = Counter(run["fixture"] for run in runs)
    assert fixtures == {"positive": 3, "corrupt": 3}
    domain_counts[task["domain"]] += 1
    task_rows.append({"instance_id": task["instance_id"], "domain": task["domain"], "task_sha256": task["task_sha256"], "mutation": task["mutation"], "checks": len(runs), "positive_checks": fixtures["positive"], "corrupt_checks": fixtures["corrupt"], "all_expected_decisions": True})
assert len(task_rows) == 16 and sum(item["checks"] for item in task_rows) == 96
summary = {"tasks": 16, "fixture_checks": 96, "positive_checks": 48, "corrupt_checks": 48, "domain_task_counts": dict(domain_counts), "model_generated_answers_in_fixture_checks": 0, "independent_scientific_task_runs_estimated": False, "integrated_certified_tasks": closure["limits"]["fully_certified_task_count"], "admitted_efficacy_results": closure["limits"]["efficacy_results"], "new_model_experiments_in_this_editorial_task": 0}
assert summary["integrated_certified_tasks"] == 0 and summary["admitted_efficacy_results"] == 0
save_json(destination / "measurement-summary.json", {"schema_version": 1, "scope": "recalculation_from_frozen_receipt_not_a_new_experiment", "summary": summary, "tasks": task_rows})

review_names = ["statistics-review.md", "domain-methods-review.md", "fairness-reader-review.md", "writing-review.md", "final-draft-review.md", "figures-review.md"]
review_records = []
for name in review_names:
    source = plan / name
    if source.exists():
        review_records.append(retain(source, destination / "reviews" / name))
save_json(destination / "snapshot.json", {"schema_version": 1, "created_at": datetime.now().astimezone().isoformat(), "measurement_cutoff": closure["closed_at"], "repository_head_at_freeze": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(), "ownership": "local thesis editorial snapshot; not a canonical runtime graph", "source_receipt_hashes_match_closure": True, "receipt_count": len(receipt_records), "receipts": receipt_records, "reviews": review_records, "private_local_only": True, "raw_task_data_or_models_copied": False})

claims = [
    ("C01", "observed_instrument", "16 tasks produced 96 expected fixture decisions, not 96 agent runs", "Ⅲ.6 / Ⅳ.1; tbl-domains; fig-measurement", ["task_scorers_receipt", "task_scorers_validation"], []),
    ("C02", "observed_environment", "15 imports passed; 91 Python and 95 Debian package entries matched", "Ⅳ.2; tbl-measurement-results", ["import_probe_receipt", "environment_parity_receipt"], []),
    ("C03", "observed_bounded_probe", "Separate agent/scorer roles passed the specified runtime-policy probes", "Ⅲ.6 / Ⅳ.2; fig-measurement", ["runtime_policy_validation"], []),
    ("C04", "not_evaluated", "Zero fully certified integrated tasks and zero admitted efficacy results at cutoff", "Abstract / Ⅰ.3 / Ⅳ.2 / Ⅴ", ["stage0_closure"], []),
    ("C05", "editorial_exclusion", "Legacy exploratory records do not supply current efficacy estimates", "Ⅳ.3; tbl-legacy-limits", ["legacy_editorial_overlay"], []),
    ("C06", "proposed_not_implemented", "Typed provenance, recheck propagation and separate research/harness revisions are design proposals", "Ⅲ.1-3; fig-architecture; fig-graph", [], ["besta2024got", "hu2025adas"]),
    ("C07", "proposed_not_preregistered", "H1 selection, H2 handoff and H3 dependency update remain unexecuted hypotheses", "Ⅲ.4; tbl-hypotheses", [], ["nosek2018preregistration"]),
    ("C08", "proposed_comparison_contract", "Separate whole-system comparison from information-matched mechanism diagnostics; log full declared costs", "Ⅲ.5", [], ["yang2024sweagent", "JMLR:v22:20-303"]),
    ("C09", "proposed_estimand_not_estimate", "Budget-conditioned effect is a proposed target; no effect size, interval, or significance test is available", "Ⅲ.7; tbl-analysis-status", [], ["agarwal2021statistical", "dror2018hitchhikers", "nosek2018preregistration"]),
    ("C10", "scope_limitation", "Content synthesis, executable tasks, research proposals and end-to-end scientific validity are distinct outcomes", "Ⅱ.1; tbl-literature; Ⅳ.5", [], ["baek-etal-2025-researchagent", "Asai2026", "chen2025scienceagentbench", "astabench2026", "pmlr-v267-huang25n"]),
    ("C11", "design_constraint", "LLM preference judgments are not independent scientific validation", "Ⅲ.3 / Ⅲ.5 / Ⅳ.5", [], ["zheng2023judge"]),
    ("C12", "research_program", "Thesis evidence precedes integrated design decisions, native implementation and NAIS prototype validation", "Ⅰ.1 / Ⅴ", [], []),
]
claim_rows = [{"id": item[0], "status": item[1], "claim": item[2], "manuscript_locator": item[3], "receipt_ids": item[4], "literature_keys": item[5], "interpretation": "literature motivates proposals; it is never evidence of ARGO efficacy"} for item in claims]
save_json(destination / "claims.json", {"schema_version": 1, "claims": claim_rows})

nodes = []
edges = []
for source in sources:
    nodes.append({"id": "S:" + source["citation_key"], "type": "source", "status": "published_selected_sections_read", "locator": source["locator"], "sha256": source["sha256"], "file": source["frozen_path"]})
for receipt_id, record in receipt_records.items():
    nodes.append({"id": "R:" + receipt_id, "type": "artifact", "status": record.get("status", "frozen_receipt"), "sha256": record["sha256"], "file": record["frozen_path"]})
for claim in claim_rows:
    nodes.append({"id": claim["id"], "type": "claim", "status": claim["status"], "label": claim["claim"], "locator": claim["manuscript_locator"]})
    for receipt_id in claim["receipt_ids"]:
        edges.append({"source": "R:" + receipt_id, "target": claim["id"], "relation": "supports_within_scope" if receipt_id != "legacy_editorial_overlay" else "documents_editorial_exclusion"})
    for key in claim["literature_keys"]:
        edges.append({"source": "S:" + key, "target": claim["id"], "relation": "motivates_or_limits"})
for hypothesis_id in ["H1", "H2", "H3"]:
    nodes.append({"id": hypothesis_id, "type": "experiment", "status": "proposed_not_run_not_preregistered"})
    edges.append({"source": hypothesis_id, "target": "C07", "relation": "derived_from"})
artifact_bindings = {"fig-architecture": ["C06"], "fig-graph": ["C06"], "fig-measurement": ["C01", "C03", "C04"], "tbl-scope": ["C01", "C04", "C06"], "tbl-literature": ["C10"], "tbl-hypotheses": ["C07"], "tbl-analysis-status": ["C09"], "tbl-domains": ["C01"], "tbl-measurement-results": ["C01", "C02", "C03", "C04"], "tbl-legacy-limits": ["C05"]}
for artifact_id, parents in artifact_bindings.items():
    nodes.append({"id": artifact_id, "type": "artifact", "status": "manuscript_element", "locator": "thesis-ko.qmd#" + artifact_id})
    for parent in parents:
        edges.append({"source": artifact_id, "target": parent, "relation": "derived_from"})
nodes.append({"id": "D01", "type": "decision", "status": "applied_to_manuscript_only", "label": "Report current instrument evidence; withhold efficacy claims"})
for parent in ["C01", "C04", "C05"]:
    edges.append({"source": "D01", "target": parent, "relation": "derived_from"})
identifiers = {node["id"] for node in nodes}
assert len(identifiers) == len(nodes)
assert all(edge["source"] in identifiers and edge["target"] in identifiers for edge in edges)
save_json(destination / "context-graph.json", {"schema_version": "thesis-editorial-graph/1", "scope": "local editorial evidence map only", "canonical_runtime_graph_modified": False, "canonical_integration_status": "not_applied", "relations": {"supports_within_scope": "receipt to bounded manuscript claim", "motivates_or_limits": "literature to design motivation or interpretive limit, not efficacy", "derived_from": "dependent record to its parent record", "documents_editorial_exclusion": "proposed overlay supporting this editorial exclusion, not canonical admission change"}, "on_retraction": "Mark dependent records requires_recheck; do not automatically declare them false or mutate canonical state", "nodes": nodes, "edges": edges})
print(json.dumps({"sources": len(sources), "receipts": len(receipt_records), "summary": summary, "graph_nodes": len(nodes), "graph_edges": len(edges)}, ensure_ascii=False, indent=2))
