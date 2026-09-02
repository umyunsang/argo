#!/usr/bin/env python3
"""Report, for each declared outcome, whether its block size can be computed today.

A plan that quietly assumes an input it does not have is worse than one that names the
input. This walks each declared outcome, states whether the quantity needed to size a
block is available, and if not, names the single thing that blocks it.

    /usr/bin/python3 experiments/study_a/plan_status.py
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from block_planning import plan  # noqa: E402
from endpoint_analysis import variance_components  # noqa: E402
from reference_anchor import minimum_calibration_size  # noqa: E402

CONFIRMATION = ROOT / "paper/experiments/confirmation-block-receipt.json"
LABEL_FORM = ROOT / "paper/experiments/calibration/label-form.json"


def completion_outcome(receipt: dict) -> dict:
    """Completion is planable: it is measured by the admission path, with no judge."""
    try:
        result = plan(receipt, 0.15)
    except ValueError as exc:
        return {"outcome": "budget completion", "planable": False, "blocked_by": str(exc)}
    return {"outcome": "budget completion", "planable": True,
            "n_per_condition": result["n_per_condition"], "episodes": result["episodes"],
            "estimated_cost_usd": result["estimated_cost_usd"]}


def quality_outcome(coverage_admissible: dict, labels_collected: int,
                    labels_required: int) -> dict:
    """Quality is not planable until judged scoring is admissible AND variance estimable."""
    blockers = []
    if labels_collected < labels_required:
        blockers.append({
            "blocker": "judged scoring is inadmissible",
            "detail": f"{labels_collected} of {labels_required} human-anchored labels collected",
            "kind": "external input",
        })
    try:
        variance_components(coverage_admissible)
        variance_note = None
    except ValueError as exc:
        variance_note = str(exc)
        blockers.append({"blocker": "endpoint variance is not estimable from admissible episodes",
                         "detail": variance_note, "kind": "design"})
    return {"outcome": "design quality", "planable": not blockers, "blocked_by": blockers}


def main() -> int:
    receipt = json.loads(CONFIRMATION.read_text(encoding="utf-8"))
    form = json.loads(LABEL_FORM.read_text(encoding="utf-8"))
    items = form["items"] if isinstance(form, dict) else form
    collected = sum(1 for item in items if item.get("answer"))
    required = minimum_calibration_size(0.10)
    coverage = {}
    for episode in receipt.get("per_episode", []):
        # Only admissible episodes may inform a plan, by the same rule that decides
        # whether they may be scored at all.
        if episode.get("admissible") is False:
            continue
        gaps = episode.get("structural_gaps") or []
        coverage[episode["episode_id"]] = (5 - len(gaps)) / 5
    out = {
        "outcomes": [completion_outcome(receipt),
                     quality_outcome(coverage, collected, required)],
        "note": ("completion is planable because the admission path measures it without a "
                 "judge; quality is not, and the binding constraint is a human input"),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
