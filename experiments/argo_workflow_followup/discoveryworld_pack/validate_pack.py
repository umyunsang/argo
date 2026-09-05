#!/usr/bin/env python3
"""Fail-closed validator for the source-only DiscoveryWorld pack design."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

EXPECTED_COMMIT = "fd591323920be0d3786ef350955de1945aa571e5"
EXPECTED_TASKS = {
    ("chemistry", "Combinatorial Chemistry", "Normal", seed, f"dw-chemistry-normal-s{seed}")
    for seed in range(5)
} | {
    ("archaeology", "Archaeology Dating", "Normal", seed, f"dw-archaeology-normal-s{seed}")
    for seed in range(5)
}
FORBIDDEN_TASK_KEYS = {
    "expected_choice", "gold_answer", "solution", "scoringInfo",
    "criticalQuestions", "criticalHypotheses",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record(checks: dict[str, bool], name: str, condition: bool) -> None:
    checks[name] = bool(condition)


def _keys(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.add(str(key))
            found.update(_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_keys(child))
    return found


def validate(pack: dict, repo_root: Path) -> dict:
    checks: dict[str, bool] = {}
    _record(
        checks,
        "SCHEMA",
        pack.get("schema_version") == "argo-discoveryworld-derived-pack-design/v1"
        and pack.get("status") == "DESIGNED_NOT_GENERATED_NOT_ADMITTED_NOT_AUTHORIZED",
    )

    source = pack.get("source", {})
    audit_path = repo_root / str(source.get("audit_path", ""))
    _record(
        checks,
        "SOURCE_PIN",
        source.get("commit") == EXPECTED_COMMIT
        and audit_path.is_file()
        and _sha256(audit_path) == source.get("audit_sha256"),
    )

    observation = pack.get("observation_contract", {})
    _record(
        checks,
        "TEXT_ONLY",
        observation.get("text_only") is True
        and observation.get("vision_enabled") is False,
    )
    _record(
        checks,
        "NO_LLM_JUDGE",
        observation.get("explanatory_knowledge_judge_enabled") is False,
    )
    _record(
        checks,
        "AGENT_BOUNDARY",
        observation.get("agent_surface") == ["observe", "act", "submit"]
        and observation.get("arbitrary_filesystem") is False
        and observation.get("network") is False
        and observation.get("scorecard_before_terminal") is False,
    )

    tasks = pack.get("tasks")
    tasks_valid = isinstance(tasks, list)
    observed_tasks = set()
    ids = []
    if tasks_valid:
        for task in tasks:
            if not isinstance(task, dict):
                tasks_valid = False
                continue
            ids.append(task.get("task_id"))
            observed_tasks.add(
                (
                    task.get("family"), task.get("scenario"), task.get("difficulty"),
                    task.get("literal_api_seed"), task.get("task_id"),
                )
            )
            tasks_valid &= task.get("horizon_steps") == 1000
            tasks_valid &= task.get("paired_conditions") == ["TREE", "TYPED"]
            tasks_valid &= task.get("fresh_context_handoff") is True
            tasks_valid &= task.get("requires_unaffected_preservation") is True
    _record(
        checks,
        "TASK_MATRIX",
        tasks_valid
        and observed_tasks == EXPECTED_TASKS
        and len(ids) == len(set(ids)) == 10
        and pack.get("sampling", {}).get("task_rows") == 10,
    )
    _record(
        checks,
        "GOLD_LEAK",
        isinstance(tasks, list)
        and not any(FORBIDDEN_TASK_KEYS & _keys(task) for task in tasks),
    )

    sampling = pack.get("sampling", {})
    _record(
        checks,
        "PSEUDOREPLICATION",
        sampling.get("families") == 2
        and sampling.get("seeds_per_family") == 5
        and sampling.get("inference_unit") == "task_family"
        and sampling.get("seeds_are_nested_rollouts") is True
        and sampling.get("confirmatory_n") is None
        and sampling.get("power") is None,
    )

    versions_ok = isinstance(tasks, list) and all(
        task.get("correction_event", {}).get("old_version") == "v1"
        and task.get("correction_event", {}).get("new_version") == "v2"
        and task.get("correction_event", {}).get("retains_revoked_old_version") is True
        for task in tasks
    )
    _record(checks, "VERSION_HISTORY", versions_ok)

    event = pack.get("event_contract", {})
    _record(
        checks,
        "ARM_IDENTITY",
        all(
            event.get(key) is True
            for key in (
                "same_raw_records_across_conditions", "same_first_record",
                "same_correction_bytes", "same_action_opportunities",
                "old_version_retained", "fresh_context_after_correction",
                "requires_affected_revision", "requires_unaffected_preservation",
            )
        )
        and pack.get("conditions", {}).get("only_intended_difference") == "typed policy",
    )

    gold_path = repo_root / str(pack.get("gold_generation_contract", ""))
    gold_valid = False
    if gold_path.is_file():
        try:
            gold = json.loads(gold_path.read_text())
            gold_valid = (
                _sha256(gold_path) == pack.get("gold_generation_contract_sha256")
                and gold.get("schema_version")
                == "argo-discoveryworld-gold-generation-contract/v1"
                and gold.get("status") == "DESIGN_ONLY_NOT_EXECUTED"
                and "expected_choice" not in json.dumps(gold, sort_keys=True)
            )
        except (OSError, json.JSONDecodeError):
            gold_valid = False
    _record(checks, "GOLD_CONTRACT", gold_valid)

    endpoints = pack.get("endpoints", {})
    _record(
        checks,
        "ENDPOINT",
        endpoints.get("primary")
        == "official rule-derived completedSuccessfully after correction/handoff"
        and "official scoreNormalized after per-task failed-action audit"
        in endpoints.get("secondary", [])
        and "LLM explanatory-knowledge judge" in endpoints.get("excluded", []),
    )

    execution = pack.get("execution", {})
    _record(
        checks,
        "EXECUTION_GATE",
        execution.get("runner") is None
        and execution.get("environment") is None
        and execution.get("isolation_receipt") is None
        and execution.get("cost_envelope") is None
        and execution.get("approval") is None
        and execution.get("model_calls_authorized") is False,
    )
    _record(
        checks,
        "NO_EXECUTION_CLAIM",
        bool(pack.get("admission_blockers"))
        and pack.get("model_calls") == 0
        and pack.get("spend_usd") == 0.0,
    )
    errors = [name for name, passed in checks.items() if not passed]
    return {"passed": not errors, "checks": checks, "errors": errors}
