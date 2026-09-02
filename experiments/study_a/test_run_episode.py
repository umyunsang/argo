#!/usr/bin/env python3
"""Failing-first fixtures for the fixed Study A runner."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_episode import run, validate_config  # noqa: E402
from test_release_sandbox import make_bundle  # noqa: E402

R = []


def check(name, cond, detail=""):
    R.append({"check": name, "passed": bool(cond), "detail": detail})


def base_cfg(bundle_root: Path, cond="C10"):
    return {"episode_id": "ep-001", "task_bundle": str(bundle_root), "condition": cond,
            "structured_state": cond in ("C10", "C11"), "dynamic_retrieval": cond in ("C01", "C11"),
            "model_selector": "pinned-revision", "token_ceiling": 32000, "call_ceiling": 12,
            "wallclock_seconds": 2700, "output_schema": "design-v1",
            "required_state_field": "state_field", "environment": {}, "scoring_paths": []}


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        bundle = make_bundle(td / "bundle")
        cfg_path = td / "ep.json"

        cfg = base_cfg(bundle.root)
        cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
        r1 = run(cfg_path, td / "ws")
        check("no_backend_is_not_executed", r1["status"] == "NOT_EXECUTED" and "model backend" in r1["reasons"][0],
              json.dumps(r1["reasons"]))
        check("workspace_digest_recorded", bool(r1.get("workspace_digest")))

        r2 = run(cfg_path, td / "ws2")
        check("runner_is_deterministic", r1["workspace_digest"] == r2["workspace_digest"])

        bad = dict(cfg); bad.pop("token_ceiling")
        cfg_path.write_text(json.dumps(bad), encoding="utf-8")
        r3 = run(cfg_path, td / "ws3")
        check("incomplete_config_refused", r3["status"] == "NOT_EXECUTED" and "configuration incomplete" in r3["reasons"][0],
              json.dumps(r3["reasons"]))

        mism = dict(cfg); mism["condition"] = "C01"
        check("condition_factor_mismatch_detected", any("expected" in p for p in validate_config(mism)),
              str(validate_config(mism)))

        leak = dict(cfg); leak["environment"] = {"TASK_TARGET": str(bundle.withheld / "target.json")}
        cfg_path.write_text(json.dumps(leak), encoding="utf-8")
        r4 = run(cfg_path, td / "ws4")
        check("probe_blocks_launch", r4["status"] == "NOT_EXECUTED" and "probe fired" in r4["reasons"][0],
              json.dumps(r4["reasons"]))

        good = dict(cfg); good["model_backend"] = {"kind": "declared-for-fixture-only"}
        cfg_path.write_text(json.dumps(good), encoding="utf-8")
        r5 = run(cfg_path, td / "ws5")
        check("declared_backend_reaches_executed", r5["status"] == "EXECUTED", json.dumps(r5["reasons"]))

    passed = sum(1 for r in R if r["passed"])
    print(json.dumps({"suite": "study_a_runner", "checks": len(R), "passed": passed, "results": R},
                     indent=2, sort_keys=True))
    return 0 if passed == len(R) else 1


if __name__ == "__main__":
    sys.exit(main())
