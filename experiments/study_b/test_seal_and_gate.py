#!/usr/bin/env python3
"""Failing-first tests for live seal and T1-prime gate verification."""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import generate_t1prime_gate_receipt as gate
import verify_seals

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + (f" :: {detail}" if not ok else ""))
    if not ok:
        FAILURES.append(name)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def fixture(root: Path) -> Path:
    (root / ".orx").mkdir()
    (root / "paper/research").mkdir(parents=True)
    (root / "experiments/study_b/harness").mkdir(parents=True)
    prereg = root / "paper/research/prereg.md"
    spec = root / "paper/research/spec.md"
    script = root / "experiments/study_b/analyze.py"
    addendum = root / "paper/research/addendum.md"
    arm = root / "experiments/study_b/harness/arm.py"
    for path, text in ((prereg, "prereg"), (spec, "spec"), (script, "analysis"),
                       (addendum, "addendum"), (arm, "arm")):
        path.write_text(text, encoding="utf-8")
    cfg = {
        "study_b": {
            "preregistration_path": "paper/research/prereg.md",
            "preregistration_sha256": sha256(prereg),
            "analysis_spec_path": "paper/research/spec.md",
            "analysis_spec_sha256": sha256(spec),
            "analysis_script_path": "experiments/study_b/analyze.py",
            "analysis_script_sha256": sha256(script),
            "t1prime_addendum_path": "paper/research/addendum.md",
            "t1prime_addendum_sha256": sha256(addendum),
            "arm_blob_hashes": {"harness/arm.py": blob_sha1(arm)},
        }
    }
    protocol = root / ".orx/paper_protocol.json"
    protocol.write_text(json.dumps(cfg), encoding="utf-8")
    return protocol


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        protocol = fixture(root)
        good = verify_seals.verify(root, protocol)
        check("all five seal classes pass from current bytes", good["passed"] is True)
        check("five checks are emitted", len(good["checks"]) == 5,
              str(len(good["checks"])))

        addendum = root / "paper/research/addendum.md"
        addendum.write_text("changed after registration", encoding="utf-8")
        bad = verify_seals.verify(root, protocol)
        failed = [x for x in bad["checks"] if not x["matched"]]
        check("changed addendum fails", bad["passed"] is False)
        check("only the changed addendum fails", len(failed) == 1, str(failed))
        reason = failed[0].get("reason", "") if failed else ""
        check("failure names the addendum path", "paper/research/addendum.md" in reason, reason)
        check("failure explains registered and actual digests",
              "registered=" in reason and "actual=" in reason, reason)

        receipt = gate.build_receipt(
            root=root,
            protocol_path=protocol,
            checked_at="2026-09-04T14:30:12+09:00",
            t1_checks={"exit_code": 0, "passed_checks": gate.REQUIRED_T1_CHECKS,
                       "stdout_sha256": "a" * 64},
            pilot_checks={"passed": True, "pilot_count": 5, "b0_scores": [1, 1, 1],
                          "manipulation_passed": 5, "gold_leaks": 0,
                          "receipt_digests": {}},
            budget={"passed": True, "measured_triple_cost_usd": 0.236,
                    "projected_cost_usd": 9.44, "buffer_usd": 20.47},
        )
        check("gate 7 reflects the live seal failure",
              receipt["gates"]["gate_7_seals_verified"]["satisfied"] is False)
        evidence = receipt["gates"]["gate_7_seals_verified"]["evidence"]
        check("gate 7 preserves the mismatch reason",
              "paper/research/addendum.md" in evidence and "registered=" in evidence,
              evidence)
        check("overall gate fails when gate 7 fails", receipt["all_passed"] is False)
        check("actual supplied clock is preserved", receipt["generated_at"] ==
              "2026-09-04T14:30:12+09:00")

    print(f"\n{len(FAILURES)} failing checks" if FAILURES else "\nAll checks passed.")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
