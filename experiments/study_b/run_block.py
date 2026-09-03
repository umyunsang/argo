#!/usr/bin/env python3
"""Fixed run contract for one Study B block (one arm x one task).

This is the string sealed in the preregistration. Arms, tasks and seeds change only
through arguments; the command itself never changes.

    /usr/bin/python3 experiments/study_b/run_block.py --arm <ARM> --task <TASK> \
        --seeds <N> --out <RECEIPT> [--dry-run]

Spend policy (instruction-0013 §4.4): without --dry-run this refuses to run until the
revised Q-0009 is approved, and it refuses on its own rather than relying on a caller.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))
from study_b.harness.arms import ARMS  # noqa: E402

APPROVAL_FLAG = ROOT / "paper/research/q0009-approval.json"
DRY_RUN_EPISODE_CAP = 1
DRY_RUN_USD_CAP = 2.00


class SpendRefused(RuntimeError):
    pass


def approval_state() -> dict:
    if not APPROVAL_FLAG.is_file():
        return {"approved": False, "reason": "no approval record on disk"}
    try:
        obj = json.loads(APPROVAL_FLAG.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"approved": False, "reason": f"approval record unreadable: {exc}"}
    if obj.get("q0009_scenario") not in ("a", "b", "c"):
        return {"approved": False, "reason": "approval record names no scenario"}
    if obj.get("q0009_scenario") == "b":
        return {"approved": False, "reason": "scenario (b) is do-not-run"}
    return {"approved": True, "scenario": obj["q0009_scenario"], "usd_cap": obj.get("usd_cap")}


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return ""


def build_receipt(arm, task, seeds, dry_run, episodes, usage_log, transcripts) -> dict:
    return {
        "schema_version": "study-b-block/v1",
        "origin": "model_call",
        "evidence_level": "PIPELINE_DRY_RUN" if dry_run else "REPRODUCED_EXPERIMENT",
        "executed": True,
        "arm": arm, "task": task, "seeds": seeds,
        "model_id": os.environ.get("STUDY_B_MODEL", ""),
        "harness_commit": git_commit(),
        "protocol_fingerprint": hashlib.sha256(
            (Path(__file__).read_bytes() + (ROOT / "experiments/study_b/harness/arms.py").read_bytes())
        ).hexdigest(),
        "provider_usage_log": usage_log,
        "episode_transcripts_dir": transcripts,
        "orx_project_id": os.environ.get("ORX_PROJECT_ID", ""),
        "orx_experiment_id": os.environ.get("ORX_EXPERIMENT_ID", ""),
        "orx_run_id": os.environ.get("ORX_RUN_ID", ""),
        "node_commit": os.environ.get("ORX_NODE_COMMIT", "") or git_commit(),
        "episodes": episodes,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--task", required=True, choices=["T1", "T2", "T3"])
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    state = approval_state()
    if not a.dry_run and not state["approved"]:
        raise SpendRefused(
            "refusing to spend: revised Q-0009 is not approved (%s). "
            "Re-run with --dry-run for the pipeline check." % state["reason"])
    if a.dry_run and a.seeds > DRY_RUN_EPISODE_CAP:
        raise SpendRefused(
            "dry run is capped at %d episode per arm; asked for %d"
            % (DRY_RUN_EPISODE_CAP, a.seeds))

    if not os.environ.get("ORX_RUN_ID"):
        raise SpendRefused(
            "refusing to run outside the experiment substrate: ORX_RUN_ID is unset. "
            "Episodes executed outside a run are not admissible as results.")

    print(json.dumps({"status": "PRECONDITIONS_OK", "arm": a.arm, "task": a.task,
                      "dry_run": a.dry_run, "approval": state}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SpendRefused as exc:
        print(json.dumps({"status": "REFUSED", "reason": str(exc)}, indent=2))
        sys.exit(2)
