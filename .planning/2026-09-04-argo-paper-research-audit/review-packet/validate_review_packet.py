#!/usr/bin/env python3
"""Deterministically validate the uncommitted causal-realignment review packet."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REQUIRED = {
    "README.md", "stage0-certification-spec.json", "validate_stage0_spec.py", "stage0-spec-validation-receipt.json",
    "stage0-evaluator-semantics-receipt.json", "stage0-identity-validator-receipt.json",
    "stage0-legacy-identity-audit-receipt.json", "stage0-treatment-loader-receipt.json",
    "stage0-orphan-run-audit-receipt.json", "stage0-provenance-validator-receipt.json",
    "stage0-legacy-provenance-audit-receipt.json", "stage0-sab-dependency-inventory.json",
    "stage0-resource-ceiling-receipt.json", "stage0-scorer-boundary-receipt.json",
    "stage0-isolation-capability-receipt.json", "stage0-scorer-certification-receipt.json",
    "stage0-synthetic-scorer-anchor-receipt.json",
    "10-protocol-fingerprint-schema.json", "10-protocol-fingerprint-template.json",
    "validate_protocol_fingerprint.py", "10-protocol-fingerprint-template-validation-receipt.json",
    "11-design-choice-matrix.json", "11-integrated-experiment-design.md",
    "validate_design_synthesis.py", "11-design-synthesis-validation-receipt.json",
    "01-causal-design-decision-record.json", "02-treatment-manifest.json",
    "03-admissibility-corrections.json", "04-task-sampling-and-certification.md",
    "04-task-sampling-manifest.json", "stage-r-retrieval-screening.md",
    "05-preregistration-draft.md", "06-recovery-fault-injection.md",
    "07-context-graph-repair-overlay.json", "validate_context_overlay.py",
    "context-graph-validation-receipt.json", "08-cost-projection.md",
    "08-cost-projection.json", "resource-anchor-manifest.json",
    "09-nais-clean-room-lineage.md", "literature-anchor-map.md", "packet-manifest.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    started = time.perf_counter()
    failures: list[str] = []
    present = {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file()}
    missing = REQUIRED - present
    if missing:
        failures.append("missing deliverables: " + ", ".join(sorted(missing)))

    manifest = json.loads((HERE / "packet-manifest.json").read_text(encoding="utf-8"))
    expected_members = present - {"packet-manifest.json", "review-packet-validation-receipt.json"}
    declared = {row["path"] for row in manifest["files"]}
    if declared != expected_members:
        failures.append(f"manifest membership mismatch: missing={sorted(expected_members-declared)} unexpected={sorted(declared-expected_members)}")
    for row in manifest["files"]:
        path = HERE / row["path"]
        if path.is_file() and (sha(path) != row["sha256"] or path.stat().st_size != row["bytes"]):
            failures.append(f"manifest byte identity mismatch: {row['path']}")

    stage0 = json.loads((HERE / "stage0-certification-spec.json").read_text(encoding="utf-8"))
    stage0_receipt = json.loads((HERE / "stage0-spec-validation-receipt.json").read_text(encoding="utf-8"))
    if stage0.get("fixture_count") != 49 or len(stage0.get("categories", [])) != 13 or stage0.get("experiment_authorized") is not False:
        failures.append("Stage 0 acceptance spec coverage or authority mismatch")
    if not stage0_receipt.get("spec_validation_passed") or not stage0_receipt.get("mutation_tests", {}).get("passed") or stage0_receipt.get("stage0_runner_certified") is not False:
        failures.append("Stage 0 spec validation or runner-not-certified boundary mismatch")
    s0_script = HERE / "validate_stage0_spec.py"
    if stage0_receipt.get("validator_script_sha256") != sha(s0_script) or stage0_receipt.get("spec_sha256") != sha(HERE / "stage0-certification-spec.json") or stage0_receipt.get("exit_code") != 0:
        failures.append("Stage 0 validation receipt identity mismatch")

    evaluator_receipt = json.loads((HERE / "stage0-evaluator-semantics-receipt.json").read_text(encoding="utf-8"))
    code_change = evaluator_receipt.get("code_change", {})
    for path_key, hash_key in (("run_t1_path", "after_sha256"), ("existing_test_path", "existing_test_sha256"), ("new_test_path", "new_test_sha256")):
        path = HERE.parents[2] / code_change.get(path_key, "")
        if not path.is_file() or sha(path) != code_change.get(hash_key):
            failures.append(f"evaluator semantics code identity mismatch: {path_key}")
    for item in evaluator_receipt.get("validation", []):
        path = HERE.parents[2] / item.get("log_path", "")
        if item.get("exit_code") != 0 or not path.is_file() or sha(path) != item.get("log_sha256"):
            failures.append(f"evaluator semantics validation mismatch: {item.get('command')}")
    boundary = evaluator_receipt.get("evidence_boundary", {})
    if boundary.get("stage0_runner_certified") is not False or boundary.get("clean_environment_verified") is not False or boundary.get("existing_48_receipts_rewritten") is not False:
        failures.append("evaluator semantics receipt overstates certification or rewrites history")
    clean_clone = evaluator_receipt.get("clean_clone_validation", {})
    if clean_clone.get("passed") is not True or clean_clone.get("head") != "fbd20a779860762e0d29db1f3206b1cba991c77c":
        failures.append("evaluator semantics lacks committed-byte clean-clone proof")
    for item in clean_clone.get("tests", []):
        path = HERE.parents[2] / item.get("log_path", "")
        if item.get("exit_code") != 0 or not path.is_file() or sha(path) != item.get("log_sha256"):
            failures.append(f"clean-clone evaluator log mismatch: {item.get('command')}")
    if evaluator_receipt.get("repository_check", {}).get("exit_code") != 0:
        failures.append("repository npm check did not pass after evaluator change")

    identity_receipt = json.loads((HERE / "stage0-identity-validator-receipt.json").read_text(encoding="utf-8"))
    identity_audit = json.loads((HERE / "stage0-legacy-identity-audit-receipt.json").read_text(encoding="utf-8"))
    for item in identity_receipt.get("code", []):
        path = HERE.parents[2] / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            failures.append(f"identity component code mismatch: {item.get('path')}")
    identity_clean = identity_receipt.get("clean_clone_validation", {})
    if identity_clean.get("passed") is not True or identity_clean.get("head") != "d89c93aee68af73833c99992ee0a737a08b6e9fb":
        failures.append("identity component lacks committed-byte clean-clone proof")
    for item in identity_clean.get("tests", []):
        path = HERE.parents[2] / item.get("log_path", "")
        if item.get("exit_code") != 0 or not path.is_file() or sha(path) != item.get("log_sha256"):
            failures.append(f"clean-clone identity log mismatch: {item.get('command')}")
    identity_boundary = identity_receipt.get("evidence_boundary", {})
    if identity_boundary.get("future_runner_integration_verified") is not False or identity_boundary.get("stage0_runner_certified") is not False:
        failures.append("identity component overstates future-runner certification")
    if identity_audit.get("t3", {}).get("outer_inner_mismatch_count") != 117 or identity_audit.get("t3", {}).get("inner_seed_values") != [0] or identity_audit.get("t1prime", {}).get("observed_rng_seed_count") != 0:
        failures.append("legacy identity audit facts changed or are incomplete")
    if identity_audit.get("source_receipts_modified") is not False or identity_audit.get("efficacy_admissible") is not False:
        failures.append("legacy identity audit rewrites or re-admits old evidence")

    loader_receipt = json.loads((HERE / "stage0-treatment-loader-receipt.json").read_text(encoding="utf-8"))
    for item in loader_receipt.get("code", []):
        path = HERE.parents[2] / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            failures.append(f"treatment loader code mismatch: {item.get('path')}")
    if loader_receipt.get("config_count") != 8 or loader_receipt.get("removal_differences") != {"runner:g0c1f1:v1":["G"],"runner:g1c0f1:v1":["C"],"runner:g1c1f0:v1":["F"]}:
        failures.append("treatment loader factorial or removal audit mismatch")
    loader_clean = loader_receipt.get("clean_clone_validation", {})
    if loader_clean.get("passed") is not True or loader_clean.get("head") != "3e1daf3e4dbe089bb17fe61a5196a273f6e2e7cd":
        failures.append("treatment loader lacks committed-byte clean-clone proof")
    loader_boundary = loader_receipt.get("evidence_boundary", {})
    if loader_boundary.get("actual_runner_integration_verified") is not False or loader_boundary.get("stage0_runner_certified") is not False:
        failures.append("treatment loader overstates actual runner integration")

    run_state_receipt = json.loads((HERE / "stage0-orphan-run-audit-receipt.json").read_text(encoding="utf-8"))
    if run_state_receipt.get("classification", {}).get("status") != "ORPHANED_NO_VERDICT" or run_state_receipt.get("classification", {}).get("verdict") is not None:
        failures.append("orphan run classification changed or gained a verdict")
    for item in run_state_receipt.get("code", []):
        path = HERE.parents[2] / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            failures.append(f"run-state classifier code mismatch: {item.get('path')}")
    run_clean = run_state_receipt.get("clean_clone_validation", {})
    if run_clean.get("passed") is not True or run_clean.get("head") != "d2d6b8f446c46e6dd45524506a1dc513aefb34c8":
        failures.append("run-state classifier lacks committed-byte clean-clone proof")
    run_boundary = run_state_receipt.get("evidence_boundary", {})
    if run_boundary.get("registry_integration_verified") is not False or run_boundary.get("stage0_runner_certified") is not False:
        failures.append("run-state component overstates registry or runner integration")

    provenance_receipt = json.loads((HERE / "stage0-provenance-validator-receipt.json").read_text(encoding="utf-8"))
    provenance_audit = json.loads((HERE / "stage0-legacy-provenance-audit-receipt.json").read_text(encoding="utf-8"))
    for item in provenance_receipt.get("code", []):
        path = HERE.parents[2] / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            failures.append(f"provenance validator code mismatch: {item.get('path')}")
    prov_clean = provenance_receipt.get("clean_clone_validation", {})
    if prov_clean.get("passed") is not True or prov_clean.get("head") != "7f8f1dd426c4471306ded4b6c1e403181cc7d931":
        failures.append("provenance validator lacks committed-byte clean-clone proof")
    prov_boundary = provenance_receipt.get("evidence_boundary", {})
    if prov_boundary.get("future_runner_integration_verified") is not False or prov_boundary.get("legacy_efficacy_re_admitted") is not False:
        failures.append("provenance component overstates integration or re-admits legacy efficacy")
    if provenance_audit.get("t3", {}).get("fully_conforming_count") != 0 or provenance_audit.get("t1prime", {}).get("fully_conforming_count") != 0 or provenance_audit.get("source_receipts_modified") is not False:
        failures.append("legacy provenance audit changed or rewrote source receipts")

    environment_receipt = json.loads((HERE / "stage0-sab-dependency-inventory.json").read_text(encoding="utf-8"))
    if environment_receipt.get("candidate_task_count") != 38 or environment_receipt.get("distribution_candidate_count") != 26 or len(environment_receipt.get("domain_counts", {})) != 4:
        failures.append("ScienceAgentBench dependency inventory coverage mismatch")
    for item in environment_receipt.get("code", []):
        path = HERE.parents[2] / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            failures.append(f"environment validator code mismatch: {item.get('path')}")
    env_clean = environment_receipt.get("clean_clone_validation", {})
    if env_clean.get("passed") is not True or env_clean.get("head") != "2031cb2b479e951cb1a991229201489bcf38a03a":
        failures.append("environment validator lacks committed-byte clean-clone proof")
    env_boundary = environment_receipt.get("evidence_boundary", {})
    if env_boundary.get("exact_lock_built") is not False or env_boundary.get("installation_performed") is not False or env_boundary.get("agent_scorer_parity") is not False or env_boundary.get("certified_task_count") != 0:
        failures.append("environment inventory overstates lock, install, parity, or task certification")

    ceiling_receipt = json.loads((HERE / "stage0-resource-ceiling-receipt.json").read_text(encoding="utf-8"))
    for item in ceiling_receipt.get("code", []):
        path = HERE.parents[2] / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            failures.append(f"resource-ceiling code mismatch: {item.get('path')}")
    ceiling_clean = ceiling_receipt.get("clean_clone_validation", {})
    if ceiling_clean.get("passed") is not True or ceiling_clean.get("head") != "f8141d8654ab1eb4ef57b46b16b20a105868f91c":
        failures.append("resource-ceiling component lacks committed-byte clean-clone proof")
    ceiling_boundary = ceiling_receipt.get("evidence_boundary", {})
    if ceiling_boundary.get("actual_runner_integration_verified") is not False or ceiling_boundary.get("hard_caps_filled_in_protocol") is not False or ceiling_boundary.get("stage0_runner_certified") is not False:
        failures.append("resource-ceiling component overstates integration or cap authority")

    scorer_boundary_receipt = json.loads((HERE / "stage0-scorer-boundary-receipt.json").read_text(encoding="utf-8"))
    isolation_receipt = json.loads((HERE / "stage0-isolation-capability-receipt.json").read_text(encoding="utf-8"))
    for item in scorer_boundary_receipt.get("code", []):
        path = HERE.parents[2] / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            failures.append(f"scorer-boundary code mismatch: {item.get('path')}")
    scorer_clean = scorer_boundary_receipt.get("clean_clone_validation", {})
    if scorer_clean.get("passed") is not True or scorer_clean.get("head") != "aae695d282d42cc7325412b86404fbdcd2d169ae":
        failures.append("scorer-boundary component lacks committed-byte clean-clone proof")
    scorer_boundary = scorer_boundary_receipt.get("evidence_boundary", {})
    if scorer_boundary.get("linux_namespace_executed") is not False or scorer_boundary.get("oracle_isolation_verified") is not False or scorer_boundary.get("condition_blind_scorer_integrated") is not False:
        failures.append("scorer-boundary component overstates isolation or integration")
    if isolation_receipt.get("target_runtime_available") is not False or isolation_receipt.get("oracle_isolation_verified") is not False:
        failures.append("host capability audit unexpectedly claims Linux oracle isolation")

    scorer_cert_receipt = json.loads((HERE / "stage0-scorer-certification-receipt.json").read_text(encoding="utf-8"))
    anchor_receipt = json.loads((HERE / "stage0-synthetic-scorer-anchor-receipt.json").read_text(encoding="utf-8"))
    for item in scorer_cert_receipt.get("code", []):
        path = HERE.parents[2] / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            failures.append(f"scorer-certification code mismatch: {item.get('path')}")
    cert_clean = scorer_cert_receipt.get("clean_clone_validation", {})
    if cert_clean.get("passed") is not True or cert_clean.get("head") != "aa5f35ce59b97a64404efc643527eb8673921305":
        failures.append("scorer-certification component lacks committed-byte clean-clone proof")
    cert_boundary = scorer_cert_receipt.get("evidence_boundary", {})
    if cert_boundary.get("real_four_task_distribution_executed") is not False or cert_boundary.get("real_task_scorers_certified") is not False or cert_boundary.get("stage0_runner_certified") is not False:
        failures.append("scorer-certification component overstates real task or runner certification")
    if anchor_receipt.get("validation", {}).get("repeat_count") != 3 or anchor_receipt.get("development_distribution_executed") is not False or anchor_receipt.get("real_task_scorer_certified") is not False:
        failures.append("synthetic scorer anchor count or boundary mismatch")

    fingerprint_template = json.loads((HERE / "10-protocol-fingerprint-template.json").read_text(encoding="utf-8"))
    fingerprint_receipt = json.loads((HERE / "10-protocol-fingerprint-template-validation-receipt.json").read_text(encoding="utf-8"))
    fp_script = HERE / "validate_protocol_fingerprint.py"
    if not fingerprint_receipt.get("passed") or fingerprint_receipt.get("protocol_sealable") is not False or fingerprint_receipt.get("protocol_fingerprint") is not None:
        failures.append("protocol fingerprint template is not validly blocked")
    if fingerprint_receipt.get("validator_script_sha256") != sha(fp_script) or fingerprint_receipt.get("template_sha256") != sha(HERE / "10-protocol-fingerprint-template.json") or fingerprint_receipt.get("exit_code") != 0:
        failures.append("protocol fingerprint validation receipt identity mismatch")
    if fingerprint_template.get("status") != "DRAFT_BLOCKED" or fingerprint_template.get("human_approval", {}).get("approved") is not False:
        failures.append("protocol fingerprint template incorrectly permits sealing")

    design_matrix = json.loads((HERE / "11-design-choice-matrix.json").read_text(encoding="utf-8"))
    design_receipt = json.loads((HERE / "11-design-synthesis-validation-receipt.json").read_text(encoding="utf-8"))
    design_script = HERE / "validate_design_synthesis.py"
    if design_matrix.get("choice_count") != 15 or design_matrix.get("experiment_authorized") is not False:
        failures.append("integrated design choice coverage or authority mismatch")
    if not design_receipt.get("passed") or design_receipt.get("choice_count") != 15 or not design_receipt.get("mutation_tests", {}).get("passed"):
        failures.append("integrated design synthesis validation failed")
    if design_receipt.get("validator_script_sha256") != sha(design_script) or design_receipt.get("matrix_sha256") != sha(HERE / "11-design-choice-matrix.json") or design_receipt.get("design_sha256") != sha(HERE / "11-integrated-experiment-design.md") or design_receipt.get("exit_code") != 0:
        failures.append("integrated design validation receipt identity mismatch")

    decision = json.loads((HERE / "01-causal-design-decision-record.json").read_text(encoding="utf-8"))
    admission = decision.get("deterministic_admission_predicate", {})
    if set(admission.get("decision_rule", {})) != {"ADMIT", "REVISE", "BLOCK"} or not admission.get("fail_closed"):
        failures.append("causal decision lacks deterministic fail-closed admission predicate")

    treatment = json.loads((HERE / "02-treatment-manifest.json").read_text(encoding="utf-8"))
    cells = treatment["cells"]
    if len(cells) != 8 or {x["cell_id"] for x in cells} != {f"G{g}C{c}F{f}" for g in (0,1) for c in (0,1) for f in (0,1)}:
        failures.append("treatment manifest is not a complete eight-cell factorial")
    for cell in cells:
        if cell.get("runner_config_sha256") != canonical(cell.get("runner_config", {})):
            failures.append(f"runner config hash mismatch: {cell['cell_id']}")
    for key in ("candidate_independence_check", "g0_content_equivalence_check", "fail_closed_loader_check", "C_prior_work_boundary"):
        if not treatment.get(key):
            failures.append(f"treatment manifest missing {key}")
    if treatment["status"] != "DRAFT_NOT_EXECUTABLE":
        failures.append("treatment manifest incorrectly authorizes execution")

    correction = json.loads((HERE / "03-admissibility-corrections.json").read_text(encoding="utf-8"))
    if len(correction["corrections"]) != 4 or correction["source_receipts_modified"] != 0:
        failures.append("admissibility correction coverage or preservation rule failed")
    t1 = next((x for x in correction["corrections"] if x["scope"] == "T1 prime pilot and block"), None)
    if not t1 or "42/48" not in t1["reason"] or t1["new_status"] != "QUARANTINED_PRE_RECERTIFICATION":
        failures.append("T1 prime quarantine does not preserve the measured 42/48 crash fact")
    required_corrections = {"FORCED_RECORDING_STUB_NOT_ARGO_PROTOTYPE", "MUST_NOT_EXECUTE", "ORPHANED_NO_VERDICT"}
    if not required_corrections <= {x["status"] for x in correction.get("implementation_corrections", [])}:
        failures.append("B2/removal/clean-clone correction coverage mismatch")

    sampling = json.loads((HERE / "04-task-sampling-manifest.json").read_text(encoding="utf-8"))
    if sampling["status"] != "BLOCKED_PENDING_RECERTIFICATION" or sampling["eligibility"]["minimum_total_certified"] != 16:
        failures.append("task sampling does not remain blocked at the 4+12 distinct-task gate")
    if sampling["eligibility"].get("selected_domain_count") != 4 or "exactly one" not in sampling["split"]["development"]:
        failures.append("development split is not exactly four domain-stratified tasks")
    if len(sampling.get("stage0_additional_checks", [])) < 6:
        failures.append("Stage 0 loader/provenance/stale-run/floor-ceiling checks are incomplete")
    if "no best-of-k" not in sampling.get("estimand_guard", ""):
        failures.append("task-level estimand does not prohibit best-of-k")

    stage_r = (HERE / "stage-r-retrieval-screening.md").read_text(encoding="utf-8")
    normalized_stage_r = " ".join(stage_r.split())
    if not all(term in normalized_stage_r for term in ("NONE", "SEMANTIC_VECTOR", "CITATION_ENTITY_GRAPH", "DEVELOPMENT-ONLY", "before any outcome is visible")):
        failures.append("Stage R arms or pre-outcome freeze are incomplete")

    prereg = (HERE / "05-preregistration-draft.md").read_text(encoding="utf-8")
    if not all(term in prereg for term in ("RA[t,c] = S[t,c] * P[t,c]^3", "Hypothesis-to-test mapping", "13 superiority tests", "non-oracle")):
        failures.append("preregistration lacks H6 statistic, test mapping, or non-oracle F signal")
    if "only when the endpoint is binary and tasks are equally weighted" not in prereg:
        failures.append("0.10 practical-effect interpretation is not scoped to binary equal-weight tasks")
    if "NOT SEALED, NOT APPROVED, NOT EXECUTABLE" not in prereg:
        failures.append("preregistration draft lacks explicit non-executable status")

    recovery = (HERE / "06-recovery-fault-injection.md").read_text(encoding="utf-8")
    if not all(term in recovery for term in ("2×2 L×P factorial", "L1P1 - L0P1", "currently BLOCKED", "capsule-cluster bootstrap", "content equivalence")):
        failures.append("recovery L×P identification or pending fields are incomplete")

    graph = json.loads((HERE / "context-graph-validation-receipt.json").read_text(encoding="utf-8"))
    gresult = graph["result"]
    if not gresult["passed"] or gresult.get("scope") != "COMBINED_BASE_PLUS_OVERLAY_ACTIVE_VIEW":
        failures.append("combined context graph validation did not pass")
    if gresult.get("active_scientific_efficacy_result_count") != 0 or not gresult["checks"].get("exact_authority_chain"):
        failures.append("context graph admits an active scientific result or lacks exact authority chain")
    if not graph["failing_first_mutations"]["passed"] or len(graph["failing_first_mutations"]["fixtures"]) < 11:
        failures.append("context failing-first mutation set is incomplete")
    script = HERE / "validate_context_overlay.py"
    if graph.get("validator_script_sha256") != sha(script) or graph.get("exit_code") != 0 or graph.get("runtime_seconds", 0) <= 0 or not graph.get("command"):
        failures.append("context validation receipt lacks script/command/runtime/exit binding")
    if graph["canonical_graph_modified"] is not False:
        failures.append("context receipt falsely claims canonical graph modification")

    resource = json.loads((HERE / "resource-anchor-manifest.json").read_text(encoding="utf-8"))
    if resource.get("receipt_count") != 53:
        failures.append("resource anchor manifest does not contain 53 receipts")
    for row in resource.get("receipts", []):
        path = HERE.parents[2] / row["path"]
        if not path.is_file() or sha(path) != row["sha256"]:
            failures.append(f"resource anchor identity mismatch: {row['path']}")
    costs = json.loads((HERE / "08-cost-projection.json").read_text(encoding="utf-8"))
    if costs["cost_anchor"].get("manifest_sha256") != sha(HERE / "resource-anchor-manifest.json"):
        failures.append("cost projection resource manifest hash mismatch")
    for row in costs["rows"]:
        if row["episodes"] != row["tasks"] * row["cells"] * row["seeds_per_task_cell"]:
            failures.append(f"episode arithmetic mismatch: {row['design']} {row['phase']}")
    stages = {x["stage"] for x in costs.get("stage_envelope", [])}
    if not {"Stage 0 measurement certification", "Stage R retrieval screening", "Stage 2 L×P recovery factorial", "contingency", "TOTAL HUMAN APPROVAL ENVELOPE"} <= stages:
        failures.append("cost envelope omits Stage 0/R/2 or contingency")
    if costs["status"] != "PROJECTION_NOT_APPROVAL" or "UNMEASURED" not in costs["workload_multipliers"]["pricing_status"]:
        failures.append("cost projection incorrectly authorizes or prices unmeasured C1/F1 workload")

    popper = json.loads((HERE / "popper-full-read-receipt.json").read_text(encoding="utf-8"))
    popper_locs = json.loads((HERE / "popper-locators.json").read_text(encoding="utf-8"))
    source_archive = HERE.parents[2] / popper["source_archive_path"]
    if popper.get("read_level") != "FULL_PAPER_READ" or not source_archive.is_file() or sha(source_archive) != popper["source_archive_sha256"]:
        failures.append("POPPER full-read source archive identity mismatch")
    if popper.get("locator_file_sha256") != sha(HERE / "popper-locators.json") or len(popper_locs.get("locators", [])) != 9:
        failures.append("POPPER locator manifest identity or count mismatch")
    for locator in popper_locs.get("locators", []):
        path = HERE.parents[2] / locator["source_path"]
        lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        excerpt = "\n".join(lines[locator["line_start"]-1:locator["line_end"]])
        if not path.is_file() or sha(path) != locator["source_sha256"] or hashlib.sha256(excerpt.encode()).hexdigest() != locator["excerpt_sha256"]:
            failures.append(f"POPPER locator path/hash/span mismatch: {locator['locator_id']}")
    popper_note = " ".join((HERE / "popper-method-note.md").read_text(encoding="utf-8").split())
    if "does **not** provide a Type-I guarantee for F" not in popper_note:
        failures.append("POPPER-to-F non-transfer boundary is missing")

    researchagent = json.loads((HERE / "researchagent-full-read-receipt.json").read_text(encoding="utf-8"))
    researchagent_locs = json.loads((HERE / "researchagent-locators.json").read_text(encoding="utf-8"))
    ra_archive = HERE.parents[2] / researchagent["source_archive_path"]
    if researchagent.get("read_level") != "FULL_PAPER_READ" or not ra_archive.is_file() or sha(ra_archive) != researchagent["source_archive_sha256"]:
        failures.append("ResearchAgent full-read source archive identity mismatch")
    if researchagent.get("locator_file_sha256") != sha(HERE / "researchagent-locators.json") or len(researchagent_locs.get("locators", [])) != 10:
        failures.append("ResearchAgent locator manifest identity or count mismatch")
    for locator in researchagent_locs.get("locators", []):
        path = HERE.parents[2] / locator["source_path"]
        lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        excerpt = "\n".join(lines[locator["line_start"]-1:locator["line_end"]])
        if not path.is_file() or sha(path) != locator["source_sha256"] or hashlib.sha256(excerpt.encode()).hexdigest() != locator["excerpt_sha256"]:
            failures.append(f"ResearchAgent locator path/hash/span mismatch: {locator['locator_id']}")
    ra_note = " ".join((HERE / "researchagent-method-note.md").read_text(encoding="utf-8").split())
    if "does **not** independently generate two candidates" not in ra_note or "cannot establish efficacy of ARGO factor C" not in ra_note:
        failures.append("ResearchAgent-to-C non-transfer boundary is missing")

    paperqa2 = json.loads((HERE / "paperqa2-full-read-receipt.json").read_text(encoding="utf-8"))
    paperqa2_locs = json.loads((HERE / "paperqa2-locators.json").read_text(encoding="utf-8"))
    pqa_archive = HERE.parents[2] / paperqa2["source_archive_path"]
    if paperqa2.get("read_level") != "FULL_PAPER_READ" or not pqa_archive.is_file() or sha(pqa_archive) != paperqa2["source_archive_sha256"]:
        failures.append("PaperQA2 full-read source archive identity mismatch")
    if paperqa2.get("locator_file_sha256") != sha(HERE / "paperqa2-locators.json") or len(paperqa2_locs.get("locators", [])) != 12:
        failures.append("PaperQA2 locator manifest identity or count mismatch")
    for locator in paperqa2_locs.get("locators", []):
        path = HERE.parents[2] / locator["source_path"]
        lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        excerpt = "\n".join(lines[locator["line_start"]-1:locator["line_end"]])
        if not path.is_file() or sha(path) != locator["source_sha256"] or hashlib.sha256(excerpt.encode()).hexdigest() != locator["excerpt_sha256"]:
            failures.append(f"PaperQA2 locator path/hash/span mismatch: {locator['locator_id']}")
    pqa_note = " ".join((HERE / "paperqa2-method-note.md").read_text(encoding="utf-8").split())
    if "must not maximize recall alone" not in pqa_note or "not evidence that a local adapter improves science" not in pqa_note:
        failures.append("PaperQA2 Stage R non-transfer boundary is missing")

    openscholar = json.loads((HERE / "openscholar-full-read-receipt.json").read_text(encoding="utf-8"))
    openscholar_locs = json.loads((HERE / "openscholar-locators.json").read_text(encoding="utf-8"))
    os_archive = HERE.parents[2] / openscholar["source_archive_path"]
    if openscholar.get("read_level") != "FULL_PAPER_READ" or not os_archive.is_file() or sha(os_archive) != openscholar["source_archive_sha256"]:
        failures.append("OpenScholar full-read source archive identity mismatch")
    if openscholar.get("locator_file_sha256") != sha(HERE / "openscholar-locators.json") or len(openscholar_locs.get("locators", [])) != 11:
        failures.append("OpenScholar locator manifest identity or count mismatch")
    for locator in openscholar_locs.get("locators", []):
        path = HERE.parents[2] / locator["source_path"]
        lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        excerpt = "\n".join(lines[locator["line_start"]-1:locator["line_end"]])
        if not path.is_file() or sha(path) != locator["source_sha256"] or hashlib.sha256(excerpt.encode()).hexdigest() != locator["excerpt_sha256"]:
            failures.append(f"OpenScholar locator path/hash/span mismatch: {locator['locator_id']}")
    os_note = " ".join((HERE / "openscholar-method-note.md").read_text(encoding="utf-8").split())
    if "Stage R varies retrieval policy only" not in os_note or "not evidence that" in os_note:
        pass
    if "cannot identify an isolated local retrieval effect" not in os_note or "LLM judge" not in os_note:
        failures.append("OpenScholar Stage R non-transfer/evaluator boundary is missing")

    provenance = json.loads((HERE / "provenance-standards-read-receipt.json").read_text(encoding="utf-8"))
    provenance_locs = json.loads((HERE / "provenance-standards-locators.json").read_text(encoding="utf-8"))
    if len(provenance.get("sources", [])) != 3 or len(provenance_locs.get("locators", [])) != 13 or provenance.get("locator_file_sha256") != sha(HERE / "provenance-standards-locators.json"):
        failures.append("provenance standards source/locator inventory mismatch")
    for source in provenance.get("sources", []):
        path_key = "archived_html" if "archived_html" in source else "archived_pdf"
        hash_key = "html_sha256" if path_key == "archived_html" else "pdf_sha256"
        path = HERE.parents[2] / source[path_key]
        if not path.is_file() or sha(path) != source[hash_key]:
            failures.append(f"provenance source identity mismatch: {source['source_id']}")
    for locator in provenance_locs.get("locators", []):
        path = HERE.parents[2] / locator["source_path"]
        lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        excerpt = "\n".join(lines[locator["line_start"]-1:locator["line_end"]])
        if not path.is_file() or sha(path) != locator["source_sha256"] or hashlib.sha256(excerpt.encode()).hexdigest() != locator["excerpt_sha256"]:
            failures.append(f"provenance locator path/hash/span mismatch: {locator['locator_id']}")
    provenance_note = " ".join((HERE / "provenance-standards-method-note.md").read_text(encoding="utf-8").split())
    if "do not determine whether a claim is scientifically supported" not in provenance_note or "valid crate is not proof" not in provenance_note:
        failures.append("provenance standards non-efficacy boundary is missing")

    rebench = json.loads((HERE / "rebench-full-read-receipt.json").read_text(encoding="utf-8"))
    rebench_locs = json.loads((HERE / "rebench-locators.json").read_text(encoding="utf-8"))
    reb_archive = HERE.parents[2] / rebench["source_archive_path"]
    if rebench.get("read_level") != "FULL_PAPER_READ" or rebench.get("canonical_text") != "report.tex" or not reb_archive.is_file() or sha(reb_archive) != rebench["source_archive_sha256"]:
        failures.append("RE-Bench canonical full-read source identity mismatch")
    if rebench.get("locator_file_sha256") != sha(HERE / "rebench-locators.json") or len(rebench_locs.get("locators", [])) != 14:
        failures.append("RE-Bench locator manifest identity or count mismatch")
    for locator in rebench_locs.get("locators", []):
        path = HERE.parents[2] / locator["source_path"]
        lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        excerpt = "\n".join(lines[locator["line_start"]-1:locator["line_end"]])
        if not path.is_file() or sha(path) != locator["source_sha256"] or hashlib.sha256(excerpt.encode()).hexdigest() != locator["excerpt_sha256"]:
            failures.append(f"RE-Bench locator path/hash/span mismatch: {locator['locator_id']}")
    reb_note = " ".join((HERE / "rebench-method-note.md").read_text(encoding="utf-8").split())
    if "Best-of-k is not a confirmatory outcome" not in reb_note or "not as evidence that G/C/F improve performance" not in reb_note:
        failures.append("RE-Bench Stage 1 estimand/transfer boundary is missing")

    literature = (HERE / "literature-anchor-map.md").read_text(encoding="utf-8")
    if "ungrounded at this scope" not in literature or "researchclaw_report_scoring_limit" not in literature:
        failures.append("broad literature weakness claim is not downgraded or locator-bound")
    if "NOT_LOCALLY_FULL_READ" in literature:
        failures.append("minimum literature anchor list remains incomplete")

    readme = (HERE / "README.md").read_text(encoding="utf-8")
    if "Until then the automatic decision is **C — HOLD**" not in readme:
        failures.append("human approval gate does not default to HOLD")

    exit_code = 0 if not failures else 1
    script_path = Path(__file__).resolve()
    receipt = {
        "schema_version": "argo-review-packet-validation/v2",
        "checked_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "origin": "deterministic_zero_cost_validator",
        "command": f"{sys.executable} {script_path.name}",
        "validator_script_sha256": sha(script_path),
        "runtime_seconds": time.perf_counter() - started,
        "exit_code": exit_code,
        "packet_manifest_sha256": sha(HERE / "packet-manifest.json"),
        "checks": {
            "required_deliverables": not missing,
            "stage0_spec_only": not any("Stage 0 acceptance" in x or "Stage 0 spec" in x or "Stage 0 validation" in x for x in failures),
            "evaluator_failure_semantics_local": not any("evaluator semantics" in x or "repository npm" in x for x in failures),
            "identity_component_and_legacy_audit": not any("identity component" in x or "identity audit" in x for x in failures),
            "treatment_loader_component": not any("treatment loader" in x for x in failures),
            "run_state_component": not any("run-state" in x or "orphan run" in x for x in failures),
            "provenance_component": not any("provenance validator" in x or "provenance component" in x or "legacy provenance" in x for x in failures),
            "environment_component": not any("environment validator" in x or "dependency inventory" in x for x in failures),
            "resource_ceiling_component": not any("resource-ceiling" in x for x in failures),
            "scorer_boundary_component": not any("scorer-boundary" in x or "oracle isolation" in x for x in failures),
            "scorer_certification_component": not any("scorer-certification" in x or "synthetic scorer" in x for x in failures),
            "fingerprint_fail_closed": not any("protocol fingerprint" in x for x in failures),
            "integrated_design_synthesis": not any("integrated design" in x for x in failures),
            "manifest_byte_identity": not any("manifest" in x for x in failures),
            "deterministic_admission": not any("admission predicate" in x for x in failures),
            "factorial_and_loader": not any("treatment manifest" in x or "runner config" in x for x in failures),
            "admissibility_preservation": not any("correction" in x or "T1 prime" in x for x in failures),
            "sampling_and_stage0": not any("task sampling" in x or "Stage 0" in x or "development split" in x for x in failures),
            "stage_r": not any("Stage R arms" in x for x in failures),
            "preregistration": not any("preregistration" in x or "practical-effect" in x for x in failures),
            "recovery_scope": not any("recovery claim" in x for x in failures),
            "combined_context_graph": not any("context" in x for x in failures),
            "complete_cost_envelope": not any("cost" in x or "resource anchor" in x or "episode arithmetic" in x for x in failures),
            "literature_scope": not any("literature weakness" in x for x in failures),
            "popper_full_read_binding": not any("POPPER" in x for x in failures),
            "researchagent_full_read_binding": not any("ResearchAgent" in x for x in failures),
            "paperqa2_full_read_binding": not any("PaperQA2" in x for x in failures),
            "openscholar_full_read_binding": not any("OpenScholar" in x for x in failures),
            "provenance_standards_binding": not any("provenance" in x.lower() for x in failures),
            "rebench_full_read_binding": not any("RE-Bench" in x for x in failures),
            "no_execution_authority": not any("authoriz" in x or "non-executable" in x for x in failures),
        },
        "failures": failures,
        "passed": not failures,
        "experiment_authorized": False,
        "spend_usd": 0.0,
    }
    (HERE / "review-packet-validation-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())
