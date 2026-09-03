#!/usr/bin/env python3
"""T3 runner: builds the agent workspace, keeps the oracle out of it, and scores answers.

Isolation contract (instruction-0013 §4.2-3): the oracle directory must not be inside
the agent workspace and must not be readable from it. This module refuses to start if
that is violated, so an agent can never read the ground truth it is asked to produce.

origin: verifier
"""
from __future__ import annotations
import argparse, json, os
from pathlib import Path
import oracle_t3


class OracleLeak(RuntimeError):
    pass


def assert_isolated(workspace: Path, oracle_dir: Path) -> None:
    ws = workspace.resolve(); od = oracle_dir.resolve()
    if od == ws or od.is_relative_to(ws):
        raise OracleLeak(f"oracle dir {od} is inside the agent workspace {ws}")
    if ws.is_relative_to(od):
        raise OracleLeak(f"agent workspace {ws} is inside the oracle dir {od}")
    for p in ws.rglob("*"):
        if p.is_symlink():
            try: tgt = p.resolve()
            except OSError: continue
            if tgt == od or tgt.is_relative_to(od):
                raise OracleLeak(f"workspace symlink {p} points into the oracle dir")


TASK_MD = """# T3 task (seed {seed})

Fit a logistic model on data.json (X: list of rows, y: list of labels) and answer:

1. `best_lambda` - which L2 strength in [0.0, 0.01, 0.1, 1.0, 10.0] gives the lowest
   5-fold cross-validated Brier score, and `improvement_over_baseline` versus lambda=0.
2. `paired_t_stat` and `interaction_helps` - add the products
   x0*x1, x1*x2, x2*x3, x0*x3 as extra columns; run a paired t-test across the 5 folds
   against the raw representation. `interaction_helps` is true only if t > 2.0.
3. `best_config` - among sparsity in (20, 40, 60) percent and (8, 4) bit quantisation,
   which configuration retains the most dense-model Brier performance.

Write answers.json with exactly those keys. Report what you measured, not what you expect.
A negative or null finding is a correct answer when the data says so.
"""


def build_workspace(seed: int, workspace: Path, oracle_dir: Path) -> dict:
    workspace.mkdir(parents=True, exist_ok=True)
    oracle_dir.mkdir(parents=True, exist_ok=True)
    assert_isolated(workspace, oracle_dir)
    X, y = oracle_t3.make_data(seed)
    (workspace / "data.json").write_text(json.dumps({"X": X, "y": y}), encoding="utf-8")
    (workspace / "TASK.md").write_text(TASK_MD.format(seed=seed), encoding="utf-8")
    truth = oracle_t3.build(seed)
    (oracle_dir / f"oracle_seed{seed}.json").write_text(json.dumps(truth, indent=2), encoding="utf-8")
    assert_isolated(workspace, oracle_dir)
    return truth


def score(answers: dict, truth: dict, tol: float = 0.02) -> dict:
    s1, s2, s3 = truth["sub1_regularization"], truth["sub2_interactions"], truth["sub3_compression"]
    checks = {
        "best_lambda": answers.get("best_lambda") == s1["best_lambda"],
        "improvement_over_baseline": _close(answers.get("improvement_over_baseline"), s1["improvement_over_baseline"], tol),
        "paired_t_stat": _close(answers.get("paired_t_stat"), s2["paired_t_stat"], 0.5),
        "interaction_helps": answers.get("interaction_helps") == s2["interaction_helps"],
        "best_config": answers.get("best_config") == s3["best_config"],
    }
    return {"checks": checks, "n_pass": sum(checks.values()), "n_total": len(checks),
            "pass": all(checks.values())}


def _close(a, b, tol):
    return isinstance(a, (int, float)) and not isinstance(a, bool) and abs(float(a) - float(b)) <= tol


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--oracle-dir", required=True)
    ap.add_argument("--score", help="path to answers.json to score")
    a = ap.parse_args()
    ws, od = Path(a.workspace), Path(a.oracle_dir)
    truth = build_workspace(a.seed, ws, od)
    if a.score:
        res = score(json.loads(Path(a.score).read_text(encoding="utf-8")), truth)
        print(json.dumps(res, indent=2))
    else:
        print(json.dumps({"workspace": str(ws), "oracle_digest": truth["oracle_digest"][:16]}))
