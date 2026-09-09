#!/usr/bin/env python3
"""Generate the T1-prime restart gate from live checks, never assertions."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import verify_seals

REQUIRED_T1_CHECKS = [
    "PASS TASK.md contains task_inst",
    "PASS TASK.md contains output_fname",
    "PASS TASK.md contains domain_knowledge",
    "PASS TASK.md contains dataset_folder_tree",
    "PASS TASK.md contains dataset_preview",
    "PASS workspace has no gold_results",
    "PASS workspace has no gold files",
    "PASS verify_output does not write into workspace",
    "PASS verify_output did not leak gold into workspace",
    "PASS verify_output subprocess cwd is outside workspace",
    "PASS verify_output invokes eval script outside workspace",
]


def run_t1_checks(root: Path) -> dict:
    script = root / "experiments/study_b/tasks/test_t1.py"
    result = subprocess.run(
        [sys.executable, str(script)], cwd=root, capture_output=True, text=True, timeout=180)
    output = result.stdout + result.stderr
    passed = [name for name in REQUIRED_T1_CHECKS if name in output]
    return {
        "command": f"{sys.executable} experiments/study_b/tasks/test_t1.py",
        "exit_code": result.returncode,
        "passed_checks": passed,
        "required_checks": REQUIRED_T1_CHECKS,
        "stdout_sha256": hashlib.sha256(output.encode()).hexdigest(),
    }


def inspect_pilots(root: Path) -> dict:
    pilot_dir = root / "experiments/study_b/pilot_receipts"
    receipts = {}
    b0_scores = []
    manipulation = 0
    gold_leaks = 0
    for path in sorted(pilot_dir.glob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        receipts[path.name] = {
            "path": str(path.relative_to(root)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "arm": obj.get("arm"),
            "instance_id": obj.get("instance_id"),
            "cost_usd": obj.get("cost_usd"),
            "ordinal_score": obj.get("ordinal_score"),
        }
        if obj.get("arm") == "B0":
            b0_scores.append(obj.get("ordinal_score"))
        manipulation += obj.get("manipulation_check_passed") is True
        gold_leaks += obj.get("gold_leak") is True
    return {
        "passed": len(receipts) == 5 and manipulation == 5 and gold_leaks == 0,
        "pilot_count": len(receipts),
        "b0_scores": b0_scores,
        "manipulation_passed": manipulation,
        "gold_leaks": gold_leaks,
        "receipt_digests": receipts,
    }


def blocked_budget() -> dict:
    return {
        "passed": False,
        "reason": "cost ledger, header, and receipt totals have not been reconciled live",
    }


def restart_conditions(root: Path) -> dict:
    cert_path = root / "paper/experiments/screening/t1prime/verifier-certification-receipt.json"
    certified = 0
    parity = False
    if cert_path.is_file():
        cert = json.loads(cert_path.read_text(encoding="utf-8"))
        certified = int(cert.get("certified_count", 0))
        parity = bool(cert.get("environment_parity_verified", False))
    addendum = (root / "paper/research/study-b-t1t2-addendum.md").read_text(encoding="utf-8")
    distributed = "(task, seed)" in addendum and "과제 전체" in addendum
    return {
        "task_recertification": {
            "satisfied": certified >= 10 and parity,
            "certified_count": certified,
            "minimum": 10,
            "environment_parity_verified": parity,
        },
        "block_design": {
            "satisfied": distributed,
            "task_seed_distribution_declared": distributed,
        },
    }


def gate(satisfied: bool, evidence: str, **extra: object) -> dict:
    return {"satisfied": bool(satisfied), "evidence": evidence, **extra}


def build_receipt(root: Path, protocol_path: Path, checked_at: str,
                  t1_checks: dict, pilot_checks: dict, budget: dict,
                  restart: dict | None = None) -> dict:
    seals = verify_seals.verify(root, protocol_path)
    present = set(t1_checks["passed_checks"])
    field_checks = set(REQUIRED_T1_CHECKS[:5])
    gold_checks = set(REQUIRED_T1_CHECKS[5:7])
    isolation_checks = set(REQUIRED_T1_CHECKS[7:])
    seal_failures = [x["reason"] for x in seals["checks"] if not x["matched"]]
    b0_scores = [x for x in pilot_checks["b0_scores"] if isinstance(x, (int, float))]
    b0_mean = sum(b0_scores) / len(b0_scores) if b0_scores else None
    restart = restart or {
        "task_recertification": {"satisfied": False, "reason": "not checked"},
        "block_design": {"satisfied": False, "reason": "not checked"},
    }
    gates = {
        "gate_1_task_md_5_fields": gate(
            t1_checks["exit_code"] == 0 and field_checks <= present,
            f"live test exit={t1_checks['exit_code']} stdout_sha256={t1_checks['stdout_sha256']}",
            checks=sorted(field_checks),
        ),
        "gate_2_workspace_no_gold": gate(
            t1_checks["exit_code"] == 0 and gold_checks <= present,
            f"live test exit={t1_checks['exit_code']} stdout_sha256={t1_checks['stdout_sha256']}",
            checks=sorted(gold_checks),
        ),
        "gate_3_eval_outside_workspace": gate(
            t1_checks["exit_code"] == 0 and isolation_checks <= present,
            f"live test exit={t1_checks['exit_code']} stdout_sha256={t1_checks['stdout_sha256']}",
            checks=sorted(isolation_checks),
        ),
        "gate_4_pilot_receipts_exist": gate(
            pilot_checks["pilot_count"] == 5,
            f"live file scan found {pilot_checks['pilot_count']} pilot receipts",
            receipts=pilot_checks["receipt_digests"],
        ),
        "gate_5_pilot_b0_headroom": gate(
            b0_mean is not None and 0.4 <= b0_mean <= 1.4,
            f"live B0 scores={b0_scores} mean={b0_mean}",
        ),
        "gate_6_budget_reconciled": gate(
            budget.get("passed") is True,
            budget.get("reason", "live cost reconciliation supplied"),
            calculation=budget,
        ),
        "gate_7_seals_verified": gate(
            seals["passed"],
            "all live digests matched" if seals["passed"] else "; ".join(seal_failures),
            verification=seals,
        ),
        "gate_8_manipulation_rules_verified": gate(
            pilot_checks["passed"] is True,
            f"live receipts: manipulation={pilot_checks['manipulation_passed']}/"
            f"{pilot_checks['pilot_count']} gold_leaks={pilot_checks['gold_leaks']}",
        ),
        "gate_9_task_recertification_and_environment_parity": gate(
            restart["task_recertification"].get("satisfied") is True,
            json.dumps(restart["task_recertification"], ensure_ascii=False),
        ),
        "gate_10_task_seed_block_design": gate(
            restart["block_design"].get("satisfied") is True,
            json.dumps(restart["block_design"], ensure_ascii=False),
        ),
    }
    all_passed = all(x["satisfied"] for x in gates.values())
    return {
        "schema_version": "study-b-t1prime-gate/v2",
        "generated_at": checked_at,
        "evaluation_contract": "instruction-0025 section 6",
        "gates": gates,
        "all_passed": all_passed,
        "verdict": "AUTHORIZED_FOR_SPEND" if all_passed else "SPEND_BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", default="paper/experiments/screening/t1prime/gate-receipt.json")
    args = parser.parse_args()
    root = args.root.resolve()
    checked_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    receipt = build_receipt(
        root, root / ".orx/paper_protocol.json", checked_at,
        run_t1_checks(root), inspect_pilots(root), blocked_budget(), restart_conditions(root))
    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
