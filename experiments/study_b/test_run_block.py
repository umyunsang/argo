#!/usr/bin/env python3
"""Failing-first tests for the Study B run contract."""
import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
F = []
def check(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (f" :: {d}" if not ok else ""))
    if not ok: F.append(n)

APPROVAL = ROOT / "paper/research/q0009-approval.json"
HIDDEN = ROOT / "paper/research/q0009-approval.json.hidden_by_test"

def with_no_approval():
    if APPROVAL.exists():
        APPROVAL.rename(HIDDEN)

def restore_approval():
    if HIDDEN.exists():
        HIDDEN.rename(APPROVAL)

def run(args, env=None):
    e = dict(os.environ); e.pop("ORX_RUN_ID", None)
    if env: e.update(env)
    p = subprocess.run([sys.executable, "experiments/study_b/run_block.py", *args, "--out", "/tmp/_rb.json"],
                       cwd=ROOT, capture_output=True, text=True, env=e)
    try: return p.returncode, json.loads(p.stdout)
    except Exception: return p.returncode, {"raw": p.stdout + p.stderr}

def main():
    # Refusal tests run WITHOUT an approval record. The substrate check runs first,
    # so each refusal scenario sets the field that must already be satisfied.
    with_no_approval()
    try:
        rc, o = run(["--arm", "B2", "--task", "T3", "--seeds", "40"], {"ORX_RUN_ID": "probe"})
        check("real spend without approval is refused even inside the substrate",
              rc == 2 and o.get("status") == "REFUSED", str(o)[:140])
        check("the refusal names the missing approval", "not approved" in o.get("reason", ""), str(o)[:180])

        rc, o = run(["--arm", "B2", "--task", "T3", "--seeds", "1", "--dry-run"])
        check("a dry run outside the substrate is refused", rc == 2 and o.get("status") == "REFUSED")
        check("the refusal names the missing run id", "ORX_RUN_ID" in o.get("reason", ""), str(o)[:180])
    finally:
        restore_approval()

    rc, o = run(["--arm", "B2", "--task", "T3", "--seeds", "5", "--dry-run"], {"ORX_RUN_ID": "probe"})
    check("a dry run over the episode cap is refused", rc == 2 and "capped" in o.get("reason", ""), str(o)[:160])

    rc, o = run(["--arm", "B2", "--task", "T1", "--seeds", "1", "--dry-run"], {"ORX_RUN_ID": "probe"})
    check("a task whose data is absent does not start", rc == 3 and o.get("status") == "TASK_NOT_READY")
    check("the block reports which task is not ready", o.get("task") == "T1", str(o)[:160])

    rc, o = run(["--arm", "B2", "--task", "T3", "--seeds", "1", "--dry-run"], {"ORX_RUN_ID": "probe"})
    check("a self-contained task inside the substrate passes preconditions",
          rc == 0 and o.get("status") == "PRECONDITIONS_OK", str(o)[:160])
    check("the arm and task are echoed without being overwritten",
          o.get("arm") == "B2" and o.get("task") == "T3", str(o)[:200])

    rc, o = run(["--arm", "B9", "--task", "T3", "--seeds", "1", "--dry-run"], {"ORX_RUN_ID": "probe"})
    check("an unknown arm is rejected by the argument contract", rc not in (0, 3))

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
