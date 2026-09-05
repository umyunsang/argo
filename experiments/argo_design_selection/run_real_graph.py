#!/usr/bin/env python3
"""Stage A-real: dependency targeting on the project's own research graph."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, platform, statistics, subprocess, sys, time
from collections import defaultdict
from pathlib import Path
from real_graph_adapter import instance_for_event, project, support_multiplicity
from targeting import POLICIES, oracle_target, score


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    start = time.monotonic()
    proj = project(a.graph)
    out_edges = defaultdict(list)
    for e in proj["edges"]:
        out_edges[e["source"]].append(e["id"])
    sources = sorted(n["id"] for n in proj["nodes"] if n["kind"] == "source" and out_edges[n["id"]])

    rows, per_event = [], []
    for sid in sources:
        inst = instance_for_event(proj, sorted(out_edges[sid]), sid.replace("/", "_"))
        target = oracle_target(inst)
        scored = {pol: score(inst, pol) for pol in POLICIES}
        per_event.append({
            "event_source": sid,
            "removed_edges": len(out_edges[sid]),
            "oracle_affected": len(target),
            **{pol: {k: scored[pol][k] for k in
                     ("over_revocation", "under_revocation", "exact_target_match",
                      "valid_results_preserved", "valid_results_total", "inspection_fraction")}
               for pol in POLICIES},
        })
        rows.extend(scored.values())

    def agg(pol):
        sel = [r for r in rows if r["policy"] == pol]
        return {
            "events": len(sel),
            "exact_target_match_rate": round(sum(r["exact_target_match"] for r in sel) / len(sel), 6),
            "total_over_revocation": sum(r["over_revocation"] for r in sel),
            "total_under_revocation": sum(r["under_revocation"] for r in sel),
            "max_over_revocation": max(r["over_revocation"] for r in sel),
            "mean_over_revocation": round(statistics.mean(r["over_revocation"] for r in sel), 6),
            "valid_results_preserved": sum(r["valid_results_preserved"] for r in sel),
            "valid_results_total": sum(r["valid_results_total"] for r in sel),
            "mean_inspection_fraction": round(statistics.mean(r["inspection_fraction"] for r in sel), 6),
        }

    overall = {pol: agg(pol) for pol in POLICIES}
    affected_sizes = [e["oracle_affected"] for e in per_event]
    here = Path(__file__).resolve().parent
    root = here.parents[1]
    receipt = {
        "schema_version": "argo-dependency-targeting-real-graph/v1",
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "graph_path": str(a.graph),
        "graph_sha256": sha(a.graph),
        "harness_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "code": {n: sha(here / n) for n in ("targeting.py", "real_graph_adapter.py", "run_real_graph.py")},
        "python": platform.python_version(),
        "python_executable_sha256": sha(Path(sys.executable)),
        "projection": {
            "nodes": len(proj["nodes"]), "edges": len(proj["edges"]), "roots": len(proj["roots"]),
            "excluded_nodes": len(proj["excluded_nodes"]), "excluded_edges": len(proj["excluded_edges"]),
            "support_multiplicity": support_multiplicity(proj),
            "exclusion_rule": "inactive status tokens and non-support relations are dropped and counted",
        },
        "events": len(per_event),
        "affected_set_size": {
            "min": min(affected_sizes), "max": max(affected_sizes),
            "mean": round(statistics.mean(affected_sizes), 6),
            "median": statistics.median(affected_sizes),
            "zero_affected_events": sum(1 for x in affected_sizes if x == 0),
        },
        "overall": overall,
        "per_event": per_event,
        "scope": "real project research graph, source-withdrawal events, protocol targeting only",
        "not_claimed": ["model compliance", "decision quality", "efficacy", "external generalization"],
        "duration_seconds": round(time.monotonic() - start, 6),
        "model_calls": 0,
        "spend_usd": 0.0,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"events": len(per_event), "projection": receipt["projection"]["nodes"],
                      "affected_set_size": receipt["affected_set_size"], "overall": overall,
                      "model_calls": 0, "spend_usd": 0.0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
