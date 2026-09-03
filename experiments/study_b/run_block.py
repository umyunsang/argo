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
sys.path.insert(0, str(ROOT / "experiments/study_b/tasks"))
import run_t1, run_t2, run_t3  # noqa: E402
from study_b import episode_runner  # noqa: E402

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


SEALED_ARM_FILES = (
    "experiments/study_b/run_block.py",
    "experiments/study_b/episode_runner.py",
    "experiments/study_b/harness/arms.py",
    "experiments/study_b/harness/components.py",
    "experiments/study_b/harness/extensions/b0_tools.js",
    "experiments/study_b/harness/extensions/b2_harness.js",
    "experiments/study_b/harness/prompts/b0_system_prompt.txt",
    "experiments/study_b/harness/prompts/b1_system_prompt.txt",
    "experiments/study_b/harness/prompts/b2_system_prompt.txt",
    "experiments/study_b/tasks/run_t3.py",
    "experiments/study_b/tasks/oracle_t3.py",
)


def blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def code_identity() -> dict:
    """Identity of the code that ran, derived from bytes.

    The substrate executes a source snapshot without a .git directory, so on
    2026-09-03 the first executed dry run recorded harness_commit="" and the
    receipt named no code at all. Blob ids from bytes match `git ls-tree` in the
    repository and verify in any copy.
    """
    blobs = {}
    for rel in SEALED_ARM_FILES:
        p = ROOT / rel
        blobs[rel] = blob_sha1(p.read_bytes()) if p.is_file() else None
    digest = hashlib.sha256(json.dumps(blobs, sort_keys=True).encode()).hexdigest()
    return {"arm_blob_ids": blobs, "arm_code_digest": digest, "git_head_if_present": git_commit()}



LOCAL_RUNS = Path(os.environ.get("ORX_LOCAL_RUNS",
                                 Path.home() / ".local/share/openresearch/local-runs"))


def substrate_run_dir(run_id) -> Path:
    """Resolve the run id to the substrate's own run directory.

    A bare string is not evidence of a run: on 2026-09-03 a test fixture set
    ORX_RUN_ID=probe and a real model episode executed outside any run. The id
    must name a directory the substrate created, or the block does not start.
    """
    if not run_id:
        raise SpendRefused(
            "refusing to run outside the experiment substrate: ORX_RUN_ID is unset. "
            "Episodes executed outside a run are not admissible as results.")
    run_dir = LOCAL_RUNS / run_id
    if not run_dir.is_dir():
        raise SpendRefused(
            "refusing to run: ORX_RUN_ID=%s does not resolve to a run directory under %s. "
            "Episodes executed outside a run are not admissible as results." % (run_id, LOCAL_RUNS))
    return run_dir

def build_receipt(arm, task, seeds, dry_run, episodes, usage_log, transcripts) -> dict:
    return {
        "schema_version": "study-b-block/v1",
        "origin": "model_call",
        "evidence_level": "PIPELINE_DRY_RUN" if dry_run else "REPRODUCED_EXPERIMENT",
        "executed": True,
        "arm": arm, "task": task, "seeds": seeds,
        "model_id": episode_runner.MODEL,
        "harness_commit": git_commit() or "snapshot:" + code_identity()["arm_code_digest"][:16],
        "code_identity": code_identity(),
        "protocol_fingerprint": hashlib.sha256(
            (Path(__file__).read_bytes() + (ROOT / "experiments/study_b/harness/arms.py").read_bytes())
        ).hexdigest(),
        "provider_usage_log": usage_log,
        "episode_transcripts_dir": transcripts,
        "orx_project_id": os.environ.get("ORX_PROJECT_ID", ""),
        "orx_experiment_id": os.environ.get("ORX_EXPERIMENT_ID", ""),
        "orx_run_id": os.environ.get("ORX_RUN_ID", ""),
        "node_commit": os.environ.get("ORX_NODE_COMMIT", "") or git_commit() or "snapshot:" + code_identity()["arm_code_digest"][:16],
        "episodes": episodes,
    }


def task_preconditions(task: str) -> dict:
    """Ask the task adapter itself whether it can run. No adapter is assumed ready."""
    if task == "T1":
        env = os.environ.get("RESEARCHCLAWBENCH_CHECKOUT")
        return run_t1.check_preconditions(Path(env) if env else None)
    if task == "T2":
        return run_t2.check_preconditions(run_t2.bundle_root(os.environ.get("STUDY_B_BUNDLES")))
    if task == "T3":
        # T3 is self-contained: its verifier generates its own ground truth.
        probe = run_t3.oracle_t3.build(0)
        return {"ready": bool(probe.get("oracle_digest")), "task": "T3",
                "verifier": "tasks/oracle_t3.py", "self_contained": True}
    return {"ready": False, "reason": f"unknown task {task}"}


def resolve_executor():
    """The model executor is chosen by name so tests can substitute a recorder.

    STUDY_B_EXECUTOR=episode selects the real runner (the default). Any other
    value must name a module:function importable from the repository root, and
    the receipt records which one ran so a recorded episode can never pass as a
    model call.
    """
    name = os.environ.get("STUDY_B_EXECUTOR", "episode")
    if name == "episode":
        return episode_runner.run_episode, "study_b.episode_runner:run_episode"
    mod_name, fn_name = name.split(":")
    import importlib
    return getattr(importlib.import_module(mod_name), fn_name), name



def write_receipt(a, state, episodes, executor_name, out_path, work_root, interrupted, rel) -> dict:
    total_cost = round(sum(float(e.get("cost_usd") or 0.0) for e in episodes), 6)
    total_tokens = sum(int(e.get("total_tokens") or 0) for e in episodes)
    usage_path = out_path.parent / f"usage_{a.arm}_{a.task}.json"
    usage_path.write_text(json.dumps({"records": [
        {"episode": i, "arm": e["arm"], "task": e["task"], "seed": e["seed"],
         "total_tokens": e.get("total_tokens", 0), "cost_usd": e.get("cost_usd", 0.0)}
        for i, e in enumerate(episodes)],
        "total_tokens": total_tokens, "total_cost_usd": total_cost}, indent=2) + "\n",
        encoding="utf-8")
    receipt = build_receipt(a.arm, a.task, a.seeds, a.dry_run, episodes,
                            rel(usage_path), rel(work_root))
    receipt["executor"] = executor_name
    if executor_name != "study_b.episode_runner:run_episode":
        receipt["origin"] = "recorded_executor"
        receipt["evidence_level"] = "FIXTURE_NOT_A_MODEL_CALL"
    receipt["episodes_completed"] = len(episodes)
    receipt["total_tokens"] = total_tokens
    receipt["total_cost_usd"] = total_cost
    receipt["interrupted"] = interrupted
    receipt["manipulation_check_passed"] = bool(episodes) and all(
        e.get("manipulation_check", {}).get("manipulation_check_passed") for e in episodes)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt

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

    substrate_run_dir(os.environ.get("ORX_RUN_ID"))

    global EXECUTOR
    EXECUTOR, executor_name = resolve_executor()
    task_state = task_preconditions(a.task)
    if not task_state.get("ready"):
        print(json.dumps({"status": "TASK_NOT_READY", "arm": a.arm, "task": a.task,
                          "detail": task_state}, indent=2))
        return 3

    print(json.dumps({"status": "PRECONDITIONS_OK", "arm": a.arm, "task": a.task,
                      "dry_run": a.dry_run, "approval": state,
                      "task_preconditions": task_state}))

    # Execution. Until this block existed the sealed command stopped above and
    # returned 0 without ever calling a model, so a screening run would have
    # reported success while producing nothing. The receipt is written only from
    # episodes that actually ran, and a refusal is recorded rather than swallowed.
    out_path = Path(a.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    work_root = out_path.parent / f"{a.arm}_{a.task}"
    oracle_root = out_path.parent / f"oracle_{a.task}"
    work_root.mkdir(parents=True, exist_ok=True)
    oracle_root.mkdir(parents=True, exist_ok=True)

    def rel(p: Path) -> str:
        try:
            return str(p.relative_to(ROOT))
        except ValueError:
            return str(p)

    episodes = []
    interrupted = None
    for seed in range(a.seeds):
        try:
            ep = EXECUTOR(a.arm, a.task, seed, work_root / f"seed{seed}", oracle_root, a.dry_run)
        except BaseException as exc:  # a spent episode must never vanish with the crash
            interrupted = {"seed": seed, "error": repr(exc)}
            break
        episodes.append(ep)
        print(json.dumps({"episode": seed, "answered": ep.get("answered"),
                          "cost_usd": ep.get("cost_usd")}))
        write_receipt(a, state, episodes, executor_name, out_path, work_root, None, rel)
    if interrupted is not None:
        write_receipt(a, state, episodes, executor_name, out_path, work_root, interrupted, rel)
        print(json.dumps({"status": "BLOCK_INTERRUPTED", "arm": a.arm, "task": a.task,
                          "completed_episodes": len(episodes), "interrupted": interrupted,
                          "receipt": rel(out_path)}))
        return 4

    receipt = write_receipt(a, state, episodes, executor_name, out_path, work_root, None, rel)
    cap = DRY_RUN_USD_CAP if a.dry_run else (state.get("usd_cap") or 0.0)
    if receipt["total_cost_usd"] > cap:
        print(json.dumps({"status": "REFUSED", "reason": "cumulative cost %.6f exceeds cap %.2f"
                          % (receipt["total_cost_usd"], cap), "receipt": rel(out_path)}))
        return 2
    print(json.dumps({"status": "BLOCK_COMPLETE", "arm": a.arm, "task": a.task,
                      "episodes": len(episodes), "total_cost_usd": receipt["total_cost_usd"],
                      "manipulation_check_passed": receipt["manipulation_check_passed"],
                      "receipt": rel(out_path)}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SpendRefused as exc:
        print(json.dumps({"status": "REFUSED", "reason": str(exc)}, indent=2))
        sys.exit(2)
