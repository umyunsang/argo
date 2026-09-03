#!/usr/bin/env python3
"""Failing-first tests for the Study B run contract."""
import json, os, subprocess, sys, tempfile
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

def run(args, env=None, out=None):
    e = dict(os.environ); e.pop("ORX_RUN_ID", None)
    e["STUDY_B_EXECUTOR"] = "study_b.fixture_executor:record"  # never a model call
    e["ORX_LOCAL_RUNS"] = str(RUNS)
    if env: e.update(env)
    p = subprocess.run([sys.executable, "experiments/study_b/run_block.py", *args,
                        "--out", str(out or TMP / "_rb.json")],
                       cwd=ROOT, capture_output=True, text=True, env=e)
    objs, dec, s = [], json.JSONDecoder(), p.stdout
    i = 0
    while True:
        j = s.find("{", i)
        if j < 0: break
        try:
            o, k = dec.raw_decode(s, j); objs.append(o); i = k
        except json.JSONDecodeError:
            i = j + 1
    return p.returncode, objs[-1] if objs else {"raw": p.stdout + p.stderr}


TMP = Path(tempfile.mkdtemp(prefix="rb_test_"))
RUNS = TMP / "runs"; (RUNS / "real-run").mkdir(parents=True)
SUB = {"ORX_RUN_ID": "real-run"}


def main():
    # Refusal tests run WITHOUT an approval record. The substrate check runs first,
    # so each refusal scenario sets the field that must already be satisfied.
    with_no_approval()
    try:
        rc, o = run(["--arm", "B2", "--task", "T3", "--seeds", "40"], SUB)
        check("real spend without approval is refused even inside the substrate",
              rc == 2 and o.get("status") == "REFUSED", str(o)[:140])
        check("the refusal names the missing approval", "not approved" in o.get("reason", ""), str(o)[:180])

        rc, o = run(["--arm", "B2", "--task", "T3", "--seeds", "1", "--dry-run"])
        check("a dry run outside the substrate is refused", rc == 2 and o.get("status") == "REFUSED")
        check("the refusal names the missing run id", "ORX_RUN_ID" in o.get("reason", ""), str(o)[:180])
    finally:
        restore_approval()

    rc, o = run(["--arm", "B2", "--task", "T3", "--seeds", "1", "--dry-run"], {"ORX_RUN_ID": "probe"})
    check("a run id that is only a string is refused", rc == 2 and o.get("status") == "REFUSED", str(o)[:160])
    check("the refusal says the id resolves to no run directory",
          "does not resolve" in o.get("reason", ""), str(o)[:200])

    rc, o = run(["--arm", "B2", "--task", "T3", "--seeds", "5", "--dry-run"], SUB)
    check("a dry run over the episode cap is refused", rc == 2 and "capped" in o.get("reason", ""), str(o)[:160])

    rc, o = run(["--arm", "B2", "--task", "T1", "--seeds", "1", "--dry-run"], SUB)
    check("a task whose data is absent does not start", rc == 3 and o.get("status") == "TASK_NOT_READY")
    check("the block reports which task is not ready", o.get("task") == "T1", str(o)[:160])

    out = TMP / "ok" / "receipt.json"
    rc, o = run(["--arm", "B2", "--task", "T3", "--seeds", "3"], SUB, out)
    check("a ready task inside the substrate runs to completion",
          rc == 0 and o.get("status") == "BLOCK_COMPLETE", str(o)[:200])
    check("every requested episode was executed", o.get("episodes") == 3, str(o)[:160])
    rcpt = json.loads(out.read_text())
    check("the receipt is written to --out", rcpt.get("episodes_completed") == 3, str(rcpt)[:120])
    check("a recorded executor cannot pass as a model call",
          rcpt.get("origin") == "recorded_executor" and rcpt.get("evidence_level") == "FIXTURE_NOT_A_MODEL_CALL",
          str({k: rcpt.get(k) for k in ("origin", "evidence_level", "executor")}))
    check("the executor is named in the receipt", rcpt.get("executor") == "study_b.fixture_executor:record")
    check("the receipt carries the substrate run id", rcpt.get("orx_run_id") == "real-run")
    check("cost is summed from the episodes that ran", abs(rcpt.get("total_cost_usd", 0) - 0.03) < 1e-9, str(rcpt.get("total_cost_usd")))
    check("the arm and task are echoed without being overwritten", rcpt.get("arm") == "B2" and rcpt.get("task") == "T3")
    check("the usage log sits beside the receipt", (out.parent / "usage_B2_T3.json").is_file())

    out2 = TMP / "crash" / "receipt.json"
    rc, o = run(["--arm", "B0", "--task", "T3", "--seeds", "3"], {**SUB, "FIXTURE_CRASH_AT_SEED": "1"}, out2)
    check("a crash after spend is reported, not swallowed", rc == 4 and o.get("status") == "BLOCK_INTERRUPTED", str(o)[:200])
    rcpt2 = json.loads(out2.read_text())
    check("episodes completed before the crash survive in the receipt",
          rcpt2.get("episodes_completed") == 1 and rcpt2.get("interrupted", {}).get("seed") == 1, str(rcpt2.get("interrupted")))
    check("an interrupted block is never marked as a passed manipulation check for missing episodes",
          rcpt2.get("seeds") == 3 and rcpt2.get("episodes_completed") == 1)

    out3 = TMP / "kill" / "receipt.json"
    rc, o = run(["--arm", "B1", "--task", "T3", "--seeds", "3"], {**SUB, "FIXTURE_KILL_AT_SEED": "2"}, out3)
    check("a hard kill leaves no completion status", rc == 137 and o.get("status") != "BLOCK_COMPLETE", str(o)[:120])
    rcpt3 = json.loads(out3.read_text()) if out3.is_file() else {}
    check("episodes spent before a hard kill are already on disk",
          rcpt3.get("episodes_completed") == 2 and abs(rcpt3.get("total_cost_usd", 0) - 0.02) < 1e-9,
          str({k: rcpt3.get(k) for k in ("episodes_completed", "total_cost_usd")}))

    rc, o = run(["--arm", "B9", "--task", "T3", "--seeds", "1", "--dry-run"], SUB)
    check("an unknown arm is rejected by the argument contract", rc == 2 and "raw" in o)

    print(f"\n{len(F)} failing" if F else "\nall checks passed")
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
