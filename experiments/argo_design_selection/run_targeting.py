#!/usr/bin/env python3
"""Stage A: deterministic dependency-targeting experiment. Zero model calls."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, platform, statistics, subprocess, sys, time
from pathlib import Path
from capsule_gen import FAMILIES, build_all
from targeting import POLICIES, batch_union_target, oracle_target, score


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=40)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    start = time.monotonic()
    instances = build_all(range(a.seeds))
    rows = [score(inst, pol) for inst in instances for pol in POLICIES]

    agg = {}
    for pol in POLICIES:
        for fam in FAMILIES:
            sel = [r for r in rows if r["policy"] == pol and r["family"] == fam]
            agg[f"{pol}|{fam}"] = {
                "instances": len(sel),
                "exact_target_match_rate": round(sum(r["exact_target_match"] for r in sel) / len(sel), 6),
                "mean_over_revocation": round(statistics.mean(r["over_revocation"] for r in sel), 6),
                "mean_under_revocation": round(statistics.mean(r["under_revocation"] for r in sel), 6),
                "valid_results_preserved": sum(r["valid_results_preserved"] for r in sel),
                "valid_results_total": sum(r["valid_results_total"] for r in sel),
                "stale_results_flagged": sum(r["stale_results_flagged"] for r in sel),
                "stale_results_total": sum(r["stale_results_total"] for r in sel),
                "mean_inspection_fraction": round(statistics.mean(r["inspection_fraction"] for r in sel), 6),
            }
    overall = {pol: {
        "instances": sum(1 for r in rows if r["policy"] == pol),
        "exact_target_match_rate": round(sum(r["exact_target_match"] for r in rows if r["policy"] == pol) / len(instances), 6),
        "total_over_revocation": sum(r["over_revocation"] for r in rows if r["policy"] == pol),
        "total_under_revocation": sum(r["under_revocation"] for r in rows if r["policy"] == pol),
        "mean_inspection_fraction": round(statistics.mean(r["inspection_fraction"] for r in rows if r["policy"] == pol), 6),
    } for pol in POLICIES}

    batch = [i for i in instances if i["family"] == "multi_edge_batch"]
    non_composition = sum(1 for i in batch if oracle_target(i) != batch_union_target(i))

    hypotheses = {
        "H1_dominance_exact": overall["P3_DOMINANCE"]["exact_target_match_rate"] == 1.0,
        "H2_cascade_over_revokes": overall["P2_CASCADE"]["total_over_revocation"] > 0,
        "H3_coarse_discards_valid_work": agg["P1_COARSE|shared_result"]["mean_over_revocation"] > 0,
        "H4_none_under_revokes": overall["P0_NONE"]["total_under_revocation"] > 0,
        "H5_batch_non_composition": non_composition == len(batch) and len(batch) > 0,
    }

    here = Path(__file__).resolve().parent
    root = here.parents[1]
    receipt = {
        "schema_version": "argo-dependency-targeting-stageA/v1",
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "design_path": "paper/research/experiment-design-dependency-targeting.md",
        "harness_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "code": {name: sha(here / name) for name in ("targeting.py", "capsule_gen.py", "run_targeting.py", "test_targeting.py")},
        "python": platform.python_version(),
        "python_executable_sha256": sha(Path(sys.executable)),
        "platform": platform.platform(),
        "families": list(FAMILIES),
        "policies": list(POLICIES),
        "seeds": a.seeds,
        "instances": len(instances),
        "scored_rows": len(rows),
        "overall": overall,
        "by_policy_family": agg,
        "batch_non_composition_instances": non_composition,
        "hypotheses": hypotheses,
        "rows": rows,
        "scope": "synthetic generated graphs; protocol-level targeting fidelity only",
        "not_claimed": ["population efficacy", "model compliance", "SOTA", "real-corpus generalization"],
        "duration_seconds": round(time.monotonic() - start, 6),
        "model_calls": 0,
        "spend_usd": 0.0,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"instances": len(instances), "overall": overall, "hypotheses": hypotheses,
                      "model_calls": 0, "spend_usd": 0.0}, indent=2))
    return 0 if all(hypotheses.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
