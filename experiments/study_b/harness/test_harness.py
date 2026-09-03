#!/usr/bin/env python3
"""Failing-first tests for the seven arms and the five components."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from study_b.harness.arms import ABLATION_OF, ARM_IDS, ARMS, single_component_difference
from study_b.harness.components import DecisionProtocol, FalsificationLoop, TypedContextGraph

F = []
def check(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (f" :: {d}" if not ok else ""))
    if not ok: F.append(n)

def main():
    check("seven arms are declared", tuple(ARMS) == ARM_IDS)
    for ab, comp in ABLATION_OF.items():
        diff = single_component_difference("B2", ab)
        check(f"{ab} differs from B2 by exactly one component", diff == [comp], f"got {diff}")
    check("B0 has no persistent interpreter", ARMS["B0"].persistent_repl is False)
    check("B1 adds persistence but no governance",
          ARMS["B1"].persistent_repl and not ARMS["B1"].typed_graph and not ARMS["B1"].decision_protocol)

    # graph immutability is real
    g = TypedContextGraph(); g.add("e1", "experiment", status="done"); g.seal("e1")
    try:
        g.add("e1", "experiment", status="rewritten")
        check("sealed node rejects rewrite", False, "no error")
    except RuntimeError as e:
        check("sealed node rejects rewrite for being immutable", "immutable" in str(e), str(e))
    try:
        g.link("e1", "produces", "missing")
        check("edge to a missing node is rejected", False, "no error")
    except RuntimeError as e:
        check("edge to a missing node is rejected for a missing endpoint", "endpoint" in str(e), str(e))

    # decision protocol enforces all six fields, naming what is missing
    p = DecisionProtocol()
    try:
        p.record(question="q", alternatives=["a"], rationale="r", decision="d",
                 expected_effect_and_risk="e")
        check("a five-field record is rejected", False, "no error")
    except ValueError as e:
        check("a record missing the falsifier is rejected and names it", "falsifier" in str(e), str(e))
    ok = p.record(question="q", alternatives=["a"], rationale="r", decision="d",
                  expected_effect_and_risk="e", falsifier="f")
    check("a complete six-field record is accepted", ok == 0)

    # claim locking catches an unsupported number
    receipt = {"metrics": {"brier": 0.1425}}
    r = p.lock_claims("we measured brier = 0.1425", receipt)
    check("a supported claim is not flagged", r["unsupported"] == [], str(r))
    r = p.lock_claims("we measured brier = 0.9100", receipt)
    check("an unsupported claim is flagged", len(r["unsupported"]) == 1, str(r))
    r = p.lock_claims("we measured f1 = 0.95", receipt)
    check("a fabricated metric name is flagged", len(r["unsupported"]) == 1, str(r))
    off = DecisionProtocol(enabled=False)
    check("an ablated protocol reports that it did not check",
          off.lock_claims("brier = 0.91", receipt)["checked"] is False)

    # falsification loop
    L = FalsificationLoop(); L.preregister(pass_rate=0.8)
    cont, why = L.judge({"pass_rate": 0.4})
    check("loop continues when a threshold is missed", cont and "pivot" in why, why)
    cont, why = L.judge({"pass_rate": 0.9})
    check("loop stops when thresholds are met", (not cont) and "met" in why, why)
    L2 = FalsificationLoop(); L2.preregister(pass_rate=0.8)
    for _ in range(3): cont, why = L2.judge({"pass_rate": 0.1})
    check("loop stops at its iteration budget and says so",
          (not cont) and "budget exhausted" in why, why)
    L3 = FalsificationLoop(enabled=False)
    cont, why = L3.judge({"pass_rate": 0.1})
    check("ablated loop makes a single pass with no threshold",
          (not cont) and L3.history[0]["verdict"] == "single_pass_no_threshold")

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
