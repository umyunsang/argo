#!/usr/bin/env python3
"""T2 adapter: budget-completion task reusing the Study A release sandbox.

T2 measures whether an episode reaches a verifiable answer inside its budget ceiling.
Budget exhaustion is a COMPETING EVENT, not a missing value: an episode that runs out
of budget is recorded as not-completed, never dropped.

Dependency: the released/withheld task bundles are evaluator-owned bytes that are not
committed to this repository. This module refuses to fabricate them; if they are absent
it reports the precondition as unmet so the caller stops rather than inventing a task.

origin: verifier
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments"))

BUNDLE_DIGESTS = {
    "T1-context-artifact": "4e0ea5fe451094f7c6199578eb60f7307ed663913c9781278b3e47d95e0200d7",
    "T2-orchestration-cost": "9aa1cfc0b4406286cc1f989bfff88aab266ff44445866a7b963ff89eab21be90",
    "T3-scaffold-elicitation": "1a072dcbff9a27d34c789c9dceabc0178110d15329ccee3855e66ae37764c562",
    "T4-retrieval-scale": "e83b78ac1ea48393fdc4d5b0bca41f3380764b8e36b2a375b0a898153d9dc34a",
}


class PreconditionUnmet(RuntimeError):
    pass


def bundle_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    return ROOT / "paper/experiments/task-bundles"


def check_preconditions(bundles: Path) -> dict:
    """Report, without inventing anything, whether T2 can actually run."""
    missing = []
    if not bundles.is_dir():
        return {"ready": False, "reason": f"bundle directory absent: {bundles}",
                "expected_tasks": sorted(BUNDLE_DIGESTS)}
    for task in sorted(BUNDLE_DIGESTS):
        if not (bundles / task).is_dir():
            missing.append(task)
    if missing:
        return {"ready": False, "reason": "bundle directories missing", "missing": missing}
    return {"ready": True, "tasks": sorted(BUNDLE_DIGESTS)}


def score_completion(episode: dict, ceiling_usd: float) -> dict:
    """Budget completion as a competing event."""
    spent = float(episode.get("cost_usd", 0.0))
    answered = bool(episode.get("answer_path")) and episode.get("exit_code") == 0
    if spent >= ceiling_usd and not answered:
        outcome = "budget_exhausted"
    elif answered:
        outcome = "completed"
    else:
        outcome = "failed_within_budget"
    return {"outcome": outcome, "completed": outcome == "completed",
            "competing_event": outcome == "budget_exhausted",
            "spent_usd": spent, "ceiling_usd": ceiling_usd}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundles", default=None)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    state = check_preconditions(bundle_root(a.bundles))
    print(json.dumps(state, indent=2))
    if not state["ready"] and not a.check_only:
        raise PreconditionUnmet(state["reason"])
