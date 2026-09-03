#!/usr/bin/env python3
"""Runnable 5-minute demo: one task carried end to end by an arm.

    /usr/bin/python3 -m study_b.demo T3 --seed 42 [--arm B2]

Makes NO model call. Every number printed comes from the deterministic verifier in
tasks/oracle_t3.py, so the demo is honest about its own provenance: it demonstrates
the governance components, not model skill.

The point of the demo is the contrast at step 8: run it with --arm B2-P and the same
draft report passes with no checking at all.
"""
from __future__ import annotations
import argparse, json, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent / "tasks"))

from study_b.harness.arms import ARMS  # noqa: E402
import oracle_t3, run_t3  # noqa: E402

CORPUS = {
    "loop-engineering": "iteration budget stopping rule falsification trigger control loop policy",
    "graph-engineering": "schema node immutability edge semantics update retrieval policy",
    "claim-locking": "report numbers matched against execution receipt provenance origin",
    "regularisation": "ridge penalty lambda overfitting cross validation brier generalisation",
}


def banner(step, title):
    print(f"\n[{step}] {title}\n" + "-" * (len(title) + 6))


def solve(workspace: Path, seed: int) -> dict:
    """The 'agent' work, done honestly by running the same computation the task asks for."""
    data = json.loads((workspace / "data.json").read_text())
    X, y = data["X"], data["y"]
    grid = [0.0, 0.01, 0.1, 1.0, 10.0]
    means = {}
    for lam in grid:
        means[lam] = sum(oracle_t3.kfold(X, y, lam)) / 5
    best = min(means, key=means.get)
    Xi = [r + [r[0]*r[1], r[1]*r[2], r[2]*r[3], r[0]*r[3]] for r in X]
    a = oracle_t3.kfold(X, y, 0.1); b = oracle_t3.kfold(Xi, y, 0.1)
    d = [p - q for p, q in zip(a, b)]
    md = sum(d) / len(d)
    var = sum((x - md) ** 2 for x in d) / (len(d) - 1)
    sd = var ** 0.5
    t = md / (sd / len(d) ** 0.5) if sd > 0 else 0.0
    s3 = oracle_t3.sub3(seed)
    return {"best_lambda": best,
            "improvement_over_baseline": means[0.0] - means[best],
            "paired_t_stat": t, "interaction_helps": bool(t > 2.0),
            "best_config": s3["best_config"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task", choices=["T3"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--arm", default="B2", choices=sorted(ARMS))
    a = ap.parse_args()
    cfg = ARMS[a.arm]
    parts = cfg.build(corpus=CORPUS)
    state, protocol, search, loop = parts["state"], parts["protocol"], parts["search"], parts["loop"]

    with tempfile.TemporaryDirectory() as td:
        root = Path(td); ws = root / "ws"; od = root / "oracle"

        banner(1, f"Task presented (arm {a.arm}, seed {a.seed})")
        truth = run_t3.build_workspace(a.seed, ws, od)
        print("workspace contains:", sorted(p.name for p in ws.iterdir()))
        print("oracle is outside the workspace and a symlink into it would be refused")

        banner(2, "Typed state: gap -> hypothesis")
        state.add("gap:reg", "gap", statement="is L2 useful on this sample?")
        state.add("hyp:reg", "hypothesis", statement="some lambda beats lambda=0")
        state.link("gap:reg", "motivates", "hyp:reg")
        print(state.render()[:220] + ("..." if len(state.render()) > 220 else ""))

        banner(3, "Decision record: six fields or nothing")
        try:
            protocol.record(question="which lambda?", alternatives=["grid", "single"],
                            rationale="grid is cheap", decision="grid",
                            expected_effect_and_risk="risk: grid too coarse")
            print("five-field record ACCEPTED  <-- governance absent")
        except ValueError as exc:
            print("five-field record REFUSED:", exc)
        protocol.record(question="which lambda?", alternatives=["grid", "single"],
                        rationale="grid is cheap", decision="grid",
                        expected_effect_and_risk="risk: grid too coarse",
                        falsifier="if no lambda beats baseline, the hypothesis is refuted")
        print("six-field record accepted")

        banner(4, "Preregister thresholds, then run")
        thr = loop.preregister(improvement_over_baseline=0.005)
        print("thresholds:", thr or "(loop ablated: none)")
        answers = solve(ws, a.seed)
        print("measured:", json.dumps(answers, indent=2)[:300])

        banner(5, "Falsification check")
        cont, why = loop.judge(answers)
        print(f"continue={cont} :: {why}")

        banner(6, "Result-driven search")
        hits = search.query("lambda regularisation did not beat baseline brier")
        print("re-query hits:", hits or "(search ablated: none)")

        banner(7, "Immutability")
        state.add("exp:1", "experiment", seed=a.seed); state.seal("exp:1")
        try:
            state.add("exp:1", "experiment", seed=999); print("rewrite ACCEPTED  <-- no immutability")
        except RuntimeError as exc:
            print("rewrite REFUSED:", exc)

        banner(8, "Claim locking  <-- the contrast")
        receipt = {"answers": answers}
        honest = f"best_lambda = {answers['best_lambda']}, improvement_over_baseline = {answers['improvement_over_baseline']:.5f}"
        inflated = "improvement_over_baseline = 0.02650, f1 = 0.95"
        for label, report in (("honest draft", honest), ("inflated draft", inflated)):
            r = protocol.lock_claims(report, receipt)
            if not r["checked"]:
                print(f"{label}: NOT CHECKED (protocol ablated) -> ships as written")
            else:
                print(f"{label}: {len(r['unsupported'])} unsupported ->",
                      [u["claim"] for u in r["unsupported"]] or "clean")

        banner(9, "Scored against the oracle it never saw")
        print(json.dumps(run_t3.score(answers, truth), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
