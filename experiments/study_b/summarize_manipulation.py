#!/usr/bin/env python3
"""Study B manipulation-check summary (instruction-0016a item 1).

Aggregates the per-episode manipulation_check fields stored in the 120 block
receipts (seed 0 from stage1v4, seeds 1..39 from the block dir) into an
auxiliary verifier receipt. Read-only over run receipts; arm rules mirror
episode_runner.parse_manipulation_log exactly:
  B0: violation iff tool_call_counts["ipython"] > 0
  B2: violation iff decisions_recorded < 1 or thresholds_registered < 1
"""

import json
import hashlib
import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASK = "T3"
N_SEEDS = 40


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def discover_receipts(root: Path = ROOT, task: str = TASK, n_seeds: int = N_SEEDS):
    """Return the ordered list of 120 input receipt paths (B0, B1, B2 per seed)."""
    stage1 = root / "paper/experiments/screening/stage1v4"
    block = root / "paper/experiments/screening/block"
    paths = []
    for seed in range(n_seeds):
        for arm in ("B0", "B1", "B2"):
            if seed == 0:
                p = stage1 / f"{arm}-{task}-seed0-receipt.json"
            else:
                p = block / f"{arm}_{task}" / f"seed{seed}-receipt.json"
            if not p.is_file():
                raise FileNotFoundError(f"missing input receipt: {p}")
            paths.append(p)
    return paths


def episode_rule_check(arm: str, mc: dict):
    """Mirror episode_runner.parse_manipulation_log arm rules from stored fields."""
    tools = mc.get("tool_call_counts", {}) or {}
    decisions = int(mc.get("decisions_recorded", 0) or 0)
    thresholds = int(mc.get("thresholds_registered", 0) or 0)
    if arm == "B0":
        n_ipython = int(tools.get("ipython", 0) or 0)
        ok = n_ipython == 0
        return {"rule": "B0_no_ipython_tool", "pass": ok,
                "detail": f"ipython_calls={n_ipython}"}
    if arm == "B2":
        ok = decisions >= 1 and thresholds >= 1
        return {"rule": "B2_decision_node_precedence", "pass": ok,
                "detail": f"decisions={decisions},thresholds={thresholds}"}
    return {"rule": "B1_none_defined", "pass": True, "detail": "no arm-specific rule"}


def aggregate_receipts(paths, root: Path = ROOT):
    """Aggregate per-episode manipulation results over the given receipts."""
    arms = {}
    input_paths = []
    for p in paths:
        rec = json.loads(p.read_text(encoding="utf-8"))
        rel = p.relative_to(root).as_posix() if p.is_relative_to(root) else str(p)
        input_paths.append(rel)
        for ep in rec.get("episodes", []):
            arm = ep.get("arm") or rec.get("arm")
            mc = ep.get("manipulation_check", {}) or {}
            rule = episode_rule_check(arm, mc)
            slot = arms.setdefault(arm, {
                "episode_count": 0, "manipulation_check_passed": 0,
                "rule_checks": {}, "violations": [], "excluded": []})
            slot["episode_count"] += 1
            if mc.get("manipulation_check_passed") is True:
                slot["manipulation_check_passed"] += 1
            rc = slot["rule_checks"].setdefault(rule["rule"], {"pass": 0, "violations": 0})
            if rule["pass"]:
                rc["pass"] += 1
            else:
                rc["violations"] += 1
                slot["violations"].append({"receipt": rel, "seed": ep.get("seed"),
                                           "detail": rule["detail"]})
    excluded = []
    for arm, slot in arms.items():
        for v in slot["violations"]:
            excluded.append({"arm": arm, **v})
        for v in slot.get("excluded", []):
            excluded.append({"arm": arm, **v})
    for slot in arms.values():
        slot["violations"] = slot.pop("violations")
        slot["excluded"] = []
    n_ep = sum(s["episode_count"] for s in arms.values())
    n_pass = sum(s["manipulation_check_passed"] for s in arms.values())
    n_rule_violations = sum(rc["violations"] for s in arms.values()
                            for rc in s["rule_checks"].values())
    return {
        "arm_aggregates": arms,
        "input_receipts": input_paths,
        "input_receipt_count": len(input_paths),
        "episodes_total": n_ep,
        "manipulation_check_passed_total": n_pass,
        "rule_violations_total": n_rule_violations,
        "excluded_episodes": excluded,
        "excluded_episode_count": len(excluded),
        "all_passed": bool(n_ep) and n_pass == n_ep and n_rule_violations == 0,
    }


def assemble_output(summary, script_path: Path):
    """Assemble the auxiliary receipt.

    executed is False by design: this receipt runs zero model calls and its
    single-run provenance fields cannot bind 120 distinct orx runs. Execution
    lineage is carried by the per-run input receipts, each of which is
    individually provenance-bound; this receipt records their paths.
    """
    return {
        "schema_version": "study-b-manipulation-summary/v1",
        "origin": "verifier",
        "evidence_level": "AGGREGATE_VERIFIER",
        "executed": False,
        "task": TASK,
        "n_seeds": N_SEEDS,
        **summary,
        "summarizer": {
            "script": "experiments/study_b/summarize_manipulation.py",
            "script_sha256": sha256_file(script_path.resolve()),
            "generated_at": datetime.datetime.now(datetime.timezone.utc)
                .astimezone().isoformat(timespec="seconds"),
        },
    }


def main() -> int:
    paths = discover_receipts()
    summary = aggregate_receipts(paths)
    out = assemble_output(summary, Path(__file__))
    out_path = ROOT / "paper/experiments/screening/block/manipulation-check-summary.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({
        "written": out_path.relative_to(ROOT).as_posix(),
        "input_receipt_count": out["input_receipt_count"],
        "episodes_total": out["episodes_total"],
        "manipulation_check_passed_total": out["manipulation_check_passed_total"],
        "rule_violations_total": out["rule_violations_total"],
        "excluded_episode_count": out["excluded_episode_count"],
        "all_passed": out["all_passed"],
    }, ensure_ascii=False))
    return 0 if out["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
