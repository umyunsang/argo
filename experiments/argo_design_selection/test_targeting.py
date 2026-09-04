#!/usr/bin/env python3
"""Failing-first checks for dependency-targeting semantics."""
from __future__ import annotations
import copy
from capsule_gen import build, build_all
from targeting import (TargetingViolation, batch_union_target, oracle_target,
                       policy_cascade, policy_dominance, score)
import policy as legacy

F = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" :: " + detail if detail and not ok else ""))
    if not ok:
        F.append(name)


def main():
    # Oracle is defined independently of any policy implementation.
    chain = build("chain", 1)
    check("chain oracle marks the whole dependent path",
          oracle_target(chain) == {n["id"] for n in chain["nodes"] if n["kind"] != "source"})
    check("chain: cascade equals dominance (non-discriminating control)",
          policy_cascade(chain)["marked"] == policy_dominance(chain)["marked"])

    dia = build("diamond_independent", 1)
    check("independent support survives withdrawal", oracle_target(dia) == set())
    check("dominance marks nothing when support survives", policy_dominance(dia)["marked"] == set())
    check("cascade over-revokes on independent support", len(policy_cascade(dia)["marked"]) > 0)

    shared = build("shared_result", 1)
    tgt = oracle_target(shared)
    check("shared result survives via the other branch", "shared:result" not in tgt)
    check("dominance preserves the shared result", "shared:result" not in policy_dominance(shared)["marked"])
    check("cascade discards the shared result", "shared:result" in policy_cascade(shared)["marked"])

    batch = build("multi_edge_batch", 1)
    check("batch target is not the union of per-edge targets",
          oracle_target(batch) != batch_union_target(batch) and batch_union_target(batch) == set())
    check("dominance matches the joint batch target",
          policy_dominance(batch)["marked"] == oracle_target(batch))

    unrelated = build("unrelated_only", 1)
    s = score(unrelated, "P3_DOMINANCE")
    check("unrelated event leaves the main scope untouched",
          all(not x.startswith("m:") for x in s["marked"]))
    check("coarse harm appears when scope is wider than the dependency boundary",
          score(shared, "P1_COARSE")["over_revocation"] > 0)
    check("coarse is harmless when scope coincides with the affected component",
          score(unrelated, "P1_COARSE")["over_revocation"] == 0)
    check("no-op policy under-revokes on chain", score(chain, "P0_NONE")["under_revocation"] > 0)

    rows = [score(i, p) for i in build_all(range(5)) for p in ("P0_NONE", "P1_COARSE", "P2_CASCADE", "P3_DOMINANCE")]
    dom = [r for r in rows if r["policy"] == "P3_DOMINANCE"]
    check("dominance matches the oracle on every generated instance",
          all(r["exact_target_match"] for r in dom),
          str([r["instance_id"] for r in dom if not r["exact_target_match"]]))
    check("dominance inspects less than the full graph on shared_result",
          all(r["inspection_fraction"] < 1.0 for r in dom if r["family"] == "shared_result"))

    # The earlier manipulation module uses plain forward reachability, which the
    # revocation-semantics literature predicts will over-revoke here.
    legacy_capsule = {
        "schema_version": "argo-scientific-choice-capsule/v1",
        "nodes": [{"id": "source:s1", "kind": "source", "status": "VALID"},
                  {"id": "source:s2", "kind": "source", "status": "VALID"},
                  {"id": "claim:c1", "kind": "claim", "status": "SUPPORTED"},
                  {"id": "decision:d1", "kind": "decision", "status": "ADMITTED"},
                  {"id": "action:a1", "kind": "action", "status": "ALLOWED"},
                  {"id": "result:r1", "kind": "result", "status": "VALID"}],
        "dependency_edges": [{"source": "source:s1", "target": "claim:c1", "relation": "supports"},
                             {"source": "source:s2", "target": "claim:c1", "relation": "supports"},
                             {"source": "claim:c1", "target": "decision:d1", "relation": "informs_decision"},
                             {"source": "decision:d1", "target": "action:a1", "relation": "governs_action"},
                             {"source": "action:a1", "target": "result:r1", "relation": "produces"}],
        "experiment_tree": {"active_next_action": "action:a1", "leaves": []},
        "events": [{"id": "event:legacy", "kind": "source_invalidation", "source_id": "source:s1"}],
        "expected": {}, "fixed_opportunities": {"model_calls": 0},
    }
    legacy_out = legacy.typed_policy(legacy_capsule, {"source_id": "source:s1"})
    check("recorded defect: forward-reachability policy over-revokes independent support",
          legacy_out["requires_recheck"] != [])

    broken = copy.deepcopy(chain)
    broken["edges"].append({"id": "e:bad", "source": "missing", "target": "m:claim0",
                            "relation": "depends_on", "scope": "S1"})
    try:
        oracle_target(broken)
        caught = False
    except TargetingViolation:
        caught = True
    check("dangling edge fails closed", caught)

    a = [score(i, "P3_DOMINANCE") for i in build_all(range(3))]
    b = [score(i, "P3_DOMINANCE") for i in build_all(range(3))]
    check("scoring is deterministic across replays", a == b)

    print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.")
    return 1 if F else 0


if __name__ == "__main__":
    raise SystemExit(main())
