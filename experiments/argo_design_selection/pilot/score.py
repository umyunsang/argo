#!/usr/bin/env python3
"""Condition-blind deterministic scorer for the budgeted-verification pilot."""
from __future__ import annotations
import json
from pathlib import Path

REQUIRED_KEYS = ("constraint_status", "action", "records_inspected", "reason")
CONDITION_TOKENS = ("c_base", "c_target", "treatment", "control", "arm")


class ScoringViolation(ValueError):
    pass


def score_decision(payload: dict, ground_truth: dict, critical_record: str, budget: int,
                   observed_reads: list | None = None) -> dict:
    """Score one decision. `payload` must contain no condition identifier."""
    blob = json.dumps(payload, ensure_ascii=False).lower()
    for tok in CONDITION_TOKENS:
        if tok in blob:
            raise ScoringViolation(f"CONDITION_LEAK_IN_DECISION: {tok}")

    missing = [k for k in REQUIRED_KEYS if k not in payload]
    if missing:
        return {"parsed": False, "reason": f"missing_keys:{missing}", "admissible": False,
                "stale_consistent": None, "correct": None, "critical_inspected": None,
                "budget_violation": None, "claimed_reads": None}

    status = str(payload["constraint_status"]).strip().lower()
    action = str(payload["action"]).strip().lower()
    claimed = [str(x).strip().upper() for x in payload["records_inspected"]] if isinstance(payload["records_inspected"], list) else []
    if status not in ("valid", "withdrawn", "unverified") or action not in ("proceed", "recheck"):
        return {"parsed": False, "reason": "enum_out_of_range", "admissible": False,
                "stale_consistent": None, "correct": None, "critical_inspected": None,
                "budget_violation": None, "claimed_reads": claimed}

    reads = [r.upper() for r in (observed_reads if observed_reads is not None else claimed)]
    return {
        "parsed": True,
        "admissible": True,
        "stale_consistent": status == "valid" or action == "proceed",
        "correct": status == ground_truth["constraint_status"] and action == ground_truth["action"],
        "partial": status == "unverified" and action == ground_truth["action"],
        "critical_inspected": critical_record.upper() in reads,
        "budget_violation": len(set(reads)) > budget,
        "claimed_reads": claimed,
        "observed_reads": reads,
    }


def load_and_score(workdir: Path, meta: dict, observed_reads: list | None = None) -> dict:
    f = workdir / "decision.json"
    if not f.is_file():
        return {"parsed": False, "reason": "no_decision_file", "admissible": False,
                "stale_consistent": None, "correct": None, "critical_inspected": None,
                "budget_violation": None, "claimed_reads": None}
    try:
        payload = json.loads(f.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"parsed": False, "reason": f"unparsable:{type(exc).__name__}", "admissible": False,
                "stale_consistent": None, "correct": None, "critical_inspected": None,
                "budget_violation": None, "claimed_reads": None}
    return score_decision(payload, meta["ground_truth"], meta["critical_record"], meta["budget"], observed_reads)
