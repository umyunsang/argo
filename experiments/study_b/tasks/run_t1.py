#!/usr/bin/env python3
"""T1 adapter: ResearchClawBench execution subset.

Verifies that the benchmark is present, licensed for this use, and structurally intact
BEFORE any episode runs. Downloads nothing on its own: acquisition is a deliberate,
logged act, not a side effect of a precondition check.

Licence recorded 2026-09-03 from the repository page: MIT.
Sources: repo github.com/InternScience/ResearchClawBench, paper arXiv 2606.07591.

origin: verifier
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

BENCH = {
    "name": "ResearchClawBench",
    "repo": "https://github.com/InternScience/ResearchClawBench",
    "dataset": "https://huggingface.co/datasets/InternScience/ResearchClawBench",
    "paper_arxiv_id": "2606.07591",
    "licence": "MIT",
    "licence_verified_at": "2026-09-03",
    "stated_task_count": 40,
    "clone": "git clone https://github.com/InternScience/ResearchClawBench.git",
}
REQUIRED_DIRS = ("tasks", "evaluation", "eval_configs")
PERMISSIVE_LICENCES = ("MIT", "Apache-2.0", "BSD-3-Clause")


class PreconditionUnmet(RuntimeError):
    pass


def licence_ok() -> tuple[bool, str]:
    lic = BENCH["licence"]
    if lic not in PERMISSIVE_LICENCES:
        return False, f"licence {lic!r} is not in the permissive set {PERMISSIVE_LICENCES}"
    return True, f"licence {lic} permits benchmark use and redistribution of results"


def check_preconditions(checkout: Path | None) -> dict:
    ok_lic, lic_msg = licence_ok()
    state = {"benchmark": BENCH["name"], "licence_ok": ok_lic, "licence_note": lic_msg,
             "acquisition": "not attempted by this module"}
    if checkout is None or not checkout.is_dir():
        state.update(ready=False,
                     reason=f"benchmark checkout absent: {checkout}",
                     next_step=BENCH["clone"])
        return state
    missing = [d for d in REQUIRED_DIRS if not (checkout / d).is_dir()]
    if missing:
        state.update(ready=False, reason="checkout is incomplete", missing=missing)
        return state
    tasks = sorted(p.name for p in (checkout / "tasks").iterdir() if p.is_dir())
    state.update(ready=ok_lic, discovered_task_count=len(tasks), tasks_sample=tasks[:5])
    if not ok_lic:
        state["reason"] = lic_msg
    return state


def select_subset(tasks: list[str], k: int, seed: int) -> list[str]:
    """Deterministic subset selection, sealed before any arm runs.

    Uses a digest of (seed, task) so the choice does not depend on directory order
    and can be re-derived by anyone holding the preregistration.
    """
    if k > len(tasks):
        raise PreconditionUnmet(f"asked for {k} tasks but only {len(tasks)} are available")
    ranked = sorted(tasks, key=lambda t: hashlib.sha256(f"{seed}:{t}".encode()).hexdigest())
    return ranked[:k]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkout", default=None)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    st = check_preconditions(Path(a.checkout) if a.checkout else None)
    print(json.dumps(st, indent=2))
    if not st.get("ready") and not a.check_only:
        raise PreconditionUnmet(st.get("reason", "preconditions unmet"))
