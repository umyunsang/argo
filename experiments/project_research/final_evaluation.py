
"""Evaluator-only execution of frozen candidate against held-out splits.

Workers must never access final or future holdout partitions. Staging and
execution occur strictly under evaluator custody with explicit single-use
ledger reservations in the central evaluation registry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

from .contracts import canonical, digest, make_contract, utc_now, write_new
from .dispatch import ROOT, SOURCE
from .review import ReviewError, reserve_final_evaluation, verify_freeze
from .runner import execute as runner_execute
from .state import AdmissionError, Store


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_split_receipt(
    evaluator_wine_dir: Path,
    worker_wine_dir: Path,
    phase: str = "final",
) -> dict[str, object]:
    """Construct an immutable custody receipt for a held-out evaluation partition."""
    if phase not in ("final", "future"):
        raise ReviewError("evaluation phase must be 'final' or 'future'")
    evaluator_wine_dir = evaluator_wine_dir.resolve()
    worker_wine_dir = worker_wine_dir.resolve()

    evaluator_manifest = json.loads((evaluator_wine_dir / "manifest.json").read_text())
    worker_manifest = json.loads((worker_wine_dir / "manifest.json").read_text())

    split_file = evaluator_wine_dir / f"{phase}.csv"
    if not split_file.is_file():
        raise ReviewError(f"evaluator split file absent: {split_file}")
    split_bytes = split_file.read_bytes()
    split_sha = _sha(split_bytes)

    expected_hash = evaluator_manifest.get("all_files", {}).get(f"{phase}.csv", {}).get("sha256")
    if split_sha != expected_hash:
        raise ReviewError("evaluator split file hash does not match evaluator manifest")

    train_hash = worker_manifest.get("files", {}).get("train.csv", {}).get("sha256")
    dev_hash = worker_manifest.get("files", {}).get("dev.csv", {}).get("sha256")
    if not train_hash or not dev_hash:
        raise ReviewError("worker manifest is missing train.csv or dev.csv hashes")

    receipt = {
        "schema_version": "project-research-split-receipt/v1",
        "split_id": f"wine-{phase}",
        "split_sha256": split_sha,
        "evaluator_id": f"evaluator-wine-{phase}",
        "purpose": "final_evaluation",
        "worker_access": False,
        "independent_from_development": True,
        "development_split_sha256": [train_hash, dev_hash],
        "custody_evidence": [
            f"Evaluator-only custody at {split_file}",
            "Held-out partition generated at initialization and stored outside worker tree",
        ],
        "independence_evidence": [
            "Independent holdout partition not mounted to development sessions",
            "Group-isolated from train and dev splits with zero group overlap",
        ],
        "evidence_scope": "development_research",
    }
    return receipt


def locate_candidate_source(
    freeze_dir: Path,
    dispatches_dir: Path,
) -> tuple[str, str, bytes]:
    """Find the exact ORX-executed candidate bytes that match the freeze reproduction receipt."""
    repro_path = freeze_dir / "artifacts" / "reproduction-receipt.json"
    if not repro_path.is_file():
        raise ReviewError("freeze artifacts missing reproduction-receipt.json")
    repro = json.loads(repro_path.read_text())
    execution_id = repro.get("execution_id")
    if not execution_id:
        raise ReviewError("reproduction receipt missing execution_id")

    for launch_path in dispatches_dir.glob("*/launch.json"):
        try:
            launch = json.loads(launch_path.read_text())
            if launch.get("run_id") == execution_id:
                frozen_path = launch_path.with_name("frozen.json")
                if frozen_path.is_file():
                    frozen = json.loads(frozen_path.read_text())
                    cand_path = Path(frozen["worktree"]) / "candidate.py"
                    if cand_path.is_file():
                        data = cand_path.read_bytes()
                        return execution_id, _sha(data), data
        except (OSError, ValueError):
            continue

    raise ReviewError(f"unable to locate candidate source for execution_id {execution_id}")


def stage_evaluator_root(
    freeze_dir: Path,
    evaluator_wine_dir: Path,
    worker_wine_dir: Path,
    staging_base: Path,
    phase: str = "final",
    *,
    dispatches_dir: Path | None = None,
) -> tuple[Path, str, str, bytes]:
    """Stage a sterile workspace where dev.csv holds the held-out split bytes."""
    freeze = verify_freeze(freeze_dir)
    freeze_id = str(freeze["freeze_id"])
    staged_workspace = staging_base / f"{freeze_id}-{phase}"
    staged_wine = staged_workspace / "wine"
    staged_wine.mkdir(parents=True, exist_ok=True, mode=0o700)

    train_src = worker_wine_dir / "train.csv"
    split_src = evaluator_wine_dir / f"{phase}.csv"
    if not train_src.is_file() or not split_src.is_file():
        raise ReviewError("source data files for staging are missing")

    train_dest = staged_wine / "train.csv"
    dev_dest = staged_wine / "dev.csv"

    shutil.copyfile(train_src, train_dest)
    train_dest.chmod(0o600)
    shutil.copyfile(split_src, dev_dest)
    dev_dest.chmod(0o600)

    other_phase = "future" if phase == "final" else "final"
    if (staged_wine / f"{other_phase}.csv").exists():
        raise ReviewError(f"forbidden holdout file {other_phase}.csv present in staging")

    staged_manifest = {
        "schema_version": "project-research-evaluator-staged/v1",
        "phase": phase,
        "freeze_id": freeze_id,
        "files": {
            "train.csv": _sha(train_dest.read_bytes()),
            "dev.csv": _sha(dev_dest.read_bytes()),
        },
    }
    (staged_wine / "manifest.json").write_text(json.dumps(staged_manifest, indent=2) + "\n")
    (staged_wine / "manifest.json").chmod(0o600)

    disp_dir = dispatches_dir or (freeze_dir.parents[2] / "dispatches")
    exec_id, cand_sha, cand_bytes = locate_candidate_source(freeze_dir, disp_dir)
    return staged_workspace, exec_id, cand_sha, cand_bytes


def ensure_evaluator_contract(domain: str, root: Path = ROOT) -> str:
    """Ensure a dedicated evaluator project contract exists for held-out evaluation."""
    project_id = f"evaluator-{domain}"
    contract_path = root / "control" / "contracts" / f"{project_id}.json"
    store = Store(root / "control" / "state.sqlite")
    if not contract_path.is_file():
        pool = json.loads((root / "control" / "model-pool.json").read_text())
        pool_digest = digest(pool)
        contract = make_contract(project_id, domain, "B", False, pool_digest)
        contract["constraints"].append("held-out evaluator measurement, not a worker development session")
        write_new(contract_path, contract)
        store.append(contract)
    return project_id


def run_final_evaluation(
    freeze_dir: Path,
    registry_dir: Path,
    phase: str = "final",
    *,
    root: Path = ROOT,
    runner_fn: Callable[[Path], dict[str, Any]] | None = None,
    dispatches_dir: Path | None = None,
) -> dict[str, object]:
    """Atomically reserve and execute held-out evaluation for a frozen candidate."""
    freeze = verify_freeze(freeze_dir)
    evaluator_wine = root / "evaluator" / "wine"
    worker_wine = root / "worker" / "wine"
    split_receipt = build_split_receipt(evaluator_wine, worker_wine, phase=phase)

    registry_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    db_path = registry_dir / "final-evaluations.sqlite3"
    conn = sqlite3.connect(db_path, timeout=10, isolation_level=None)
    conn.execute("CREATE TABLE IF NOT EXISTS reservations (reservation_id TEXT PRIMARY KEY, freeze_sha256 TEXT UNIQUE NOT NULL, split_id TEXT UNIQUE NOT NULL, split_sha256 TEXT UNIQUE NOT NULL, receipt_json TEXT NOT NULL)")

    row = conn.execute(
        "SELECT reservation_id, receipt_json FROM reservations WHERE freeze_sha256=? AND split_id=?",
        (freeze["freeze_sha256"], split_receipt["split_id"]),
    ).fetchone()

    if row is None:
        reservation = reserve_final_evaluation(freeze_dir, split_receipt, registry_dir)
        reservation_id = str(reservation["reservation_id"])
    else:
        reservation_id, receipt_text = row[0], row[1]
        receipt_doc = json.loads(receipt_text)
        reservation = receipt_doc.get("reservation", receipt_doc)

    results_dir = root / "evaluator" / "results"
    receipt_path = results_dir / f"{reservation_id}.json"
    if receipt_path.is_file():
        raise ReviewError("reservation already executed; repeated evaluation is prohibited")

    reservation["execution_started"] = True
    conn.execute("BEGIN IMMEDIATE")
    try:
        receipt_wrapper = {"reservation": reservation, "split_custody_receipt": split_receipt}
        conn.execute(
            "UPDATE reservations SET receipt_json=? WHERE reservation_id=?",
            (canonical(receipt_wrapper), reservation_id),
        )
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        conn.close()
        raise
    conn.close()

    staging_base = root / "evaluator" / "staging"
    staged_ws, exec_id, cand_sha, cand_bytes = stage_evaluator_root(
        freeze_dir,
        evaluator_wine,
        worker_wine,
        staging_base,
        phase=phase,
        dispatches_dir=dispatches_dir,
    )

    eval_snapshot = root / "control" / "evaluations" / reservation_id
    eval_snapshot.mkdir(parents=True, exist_ok=True, mode=0o700)
    (eval_snapshot / "candidate.py").write_bytes(cand_bytes)
    (eval_snapshot / "runner.py").write_bytes(
        b"from experiments.project_research.runner import main\nraise SystemExit(main())\n"
    )
    (eval_snapshot / "experiments").mkdir(exist_ok=True, mode=0o700)
    (eval_snapshot / "experiments" / "__init__.py").write_bytes(b"")
    for name in ("__init__.py", "contracts.py", "state.py", "runner.py", "container_task.py"):
        (eval_snapshot / "experiments" / "project_research" / name).parent.mkdir(parents=True, exist_ok=True)
        (eval_snapshot / "experiments" / "project_research" / name).write_bytes((SOURCE / name).read_bytes())

    env_info = json.loads((root / "control" / "environment.json").read_text())
    campaign_id = freeze_dir.parent.name
    eval_project_id = ensure_evaluator_contract("wine", root=root)
    spec = {
        "mode": "candidate",
        "project_id": eval_project_id,
        "domain": "wine",
        "worker_root": str(staged_ws),
        "image": env_info["image"],
        "timeout_seconds": 600,
        "arguments": ["wine"],
        "evaluator_execution": True,
    }
    (eval_snapshot / "node-spec.json").write_text(json.dumps(spec, indent=2) + "\n")

    execute_impl = runner_fn or runner_execute
    run_receipt = execute_impl(eval_snapshot)

    result_doc = run_receipt.get("result")
    result_sha = run_receipt.get("result_sha256")

    results_dir = root / "evaluator" / "results"
    results_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    eval_receipt = {
        "schema_version": "project-research-final-evaluation-receipt/v1",
        "reservation_id": reservation_id,
        "freeze_id": freeze["freeze_id"],
        "freeze_sha256": freeze["freeze_sha256"],
        "candidate_id": freeze["candidate_id"],
        "phase": phase,
        "split_id": split_receipt["split_id"],
        "split_sha256": split_receipt["split_sha256"],
        "candidate_source_sha256": cand_sha,
        "reproduction_run_id": exec_id,
        "image": env_info["image"],
        "exit_code": run_receipt.get("exit_code"),
        "cpu_seconds": (run_receipt.get("resources") or {}).get("cpu_seconds"),
        "result_sha256": result_sha,
        "final_result": result_doc,
        "evaluated_at": utc_now(),
        "custody": "Evaluator custody only; do not expose to development workers",
    }

    receipt_path = results_dir / f"{reservation_id}.json"
    write_new(receipt_path, eval_receipt)
    receipt_path.chmod(0o600)

    store = Store(root / "control" / "state.sqlite")
    store.event({
        "event": "final_evaluation_executed",
        "project_id": campaign_id,
        "evaluator_project_id": eval_project_id,
        "freeze_sha256": freeze["freeze_sha256"],
        "reservation_id": reservation_id,
        "phase": phase,
        "result_sha256": result_sha,
        "disclosed": False,
    })

    return eval_receipt


def disclose(
    reservation_id: str,
    results_dir: Path,
    freeze_dir: Path,
) -> dict[str, object]:
    """Assemble an authoritative PI disclosure packet comparing development vs final metrics."""
    receipt_file = results_dir / f"{reservation_id}.json"
    if not receipt_file.is_file():
        raise ReviewError(f"evaluation receipt absent: {receipt_file}")
    eval_receipt = json.loads(receipt_file.read_text())

    final_res = eval_receipt.get("final_result") or {}
    final_metrics = {
        "baseline_model": final_res.get("baseline_model"),
        "interaction_model": final_res.get("interaction_model"),
        "mean_predictor": final_res.get("mean_predictor"),
        "reproduction_checks": final_res.get("reproduction_checks"),
        "reproduction_overall_pass": final_res.get("reproduction_overall_pass"),
    }

    dev_res_file = freeze_dir / "artifacts" / f"result-{eval_receipt['reproduction_run_id'][:8]}.json"
    dev_metrics: dict[str, Any] = {}
    if dev_res_file.is_file():
        dev_res = json.loads(dev_res_file.read_text())
        dev_metrics = {
            "baseline_model": dev_res.get("baseline_model"),
            "interaction_model": dev_res.get("interaction_model"),
            "mean_predictor": dev_res.get("mean_predictor"),
            "reproduction_checks": dev_res.get("reproduction_checks"),
            "reproduction_overall_pass": dev_res.get("reproduction_overall_pass"),
        }

    packet = {
        "schema_version": "project-research-final-disclosure/v1",
        "reservation_id": reservation_id,
        "freeze_id": eval_receipt["freeze_id"],
        "candidate_id": eval_receipt["candidate_id"],
        "phase": eval_receipt["phase"],
        "split_id": eval_receipt["split_id"],
        "development_metrics": dev_metrics,
        "held_out_final_metrics": final_metrics,
        "superiority": "NOT_ASSESSED",
        "pi_acceptance": "PENDING",
        "disclosed_at": utc_now(),
        "note": "Superiority and PI acceptance are separate judgments requiring PI determination.",
    }
    return packet


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    res = sub.add_parser("reserve")
    res.add_argument("freeze_dir", type=Path)
    res.add_argument("--registry-dir", type=Path, default=ROOT / "control" / "evaluation-registry")
    res.add_argument("--phase", default="final", choices=["final", "future"])

    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("freeze_dir", type=Path)
    run_cmd.add_argument("--registry-dir", type=Path, default=ROOT / "control" / "evaluation-registry")
    run_cmd.add_argument("--phase", default="final", choices=["final", "future"])

    disc = sub.add_parser("disclose")
    disc.add_argument("reservation_id")
    disc.add_argument("freeze_dir", type=Path)
    disc.add_argument("--results-dir", type=Path, default=ROOT / "evaluator" / "results")

    args = parser.parse_args(argv)
    try:
        if args.command == "reserve":
            eval_wine = ROOT / "evaluator" / "wine"
            work_wine = ROOT / "worker" / "wine"
            split_receipt = build_split_receipt(eval_wine, work_wine, phase=args.phase)
            result = reserve_final_evaluation(args.freeze_dir, split_receipt, args.registry_dir)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "run":
            result = run_final_evaluation(args.freeze_dir, args.registry_dir, phase=args.phase)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "disclose":
            result = disclose(args.reservation_id, args.results_dir, args.freeze_dir)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ReviewError, AdmissionError, OSError, ValueError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
