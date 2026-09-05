#!/usr/bin/env python3
r"""Dependency-targeting policies for evidence invalidation in a research graph.

Semantics follow the edge-dominance target used for delegation revocation
(arXiv 2608.30091 v1): for removed edge set E, the affected set is
    S = reach(G) \ reach(G - E)
under disjunctive support, i.e. a node stays supported while any valid
root-to-node path survives. Over- and under-revocation use that paper's
definitions. The target is always computed on the pre-event graph, matching
the pre-reload edge walk of arXiv 2609.00243 v1.
"""
from __future__ import annotations
from collections import defaultdict, deque

POLICIES = ("P0_NONE", "P1_COARSE", "P1G_GLOBAL_RESET", "P2_CASCADE", "P3_DOMINANCE")
DERIVED_KINDS = ("claim", "decision", "action", "result")


class TargetingViolation(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise TargetingViolation(message)


def validate_instance(inst: dict) -> None:
    require(inst.get("schema_version") == "argo-dependency-targeting-instance/v1", "INSTANCE_SCHEMA")
    ids = [n["id"] for n in inst["nodes"]]
    require(len(ids) == len(set(ids)) and all(ids), "INSTANCE_NODE_IDS")
    idset = set(ids)
    seen = set()
    for e in inst["edges"]:
        require(e["source"] in idset and e["target"] in idset, "INSTANCE_DANGLING_EDGE")
        require(e["id"] not in seen, "INSTANCE_DUPLICATE_EDGE_ID")
        seen.add(e["id"])
    require(bool(inst.get("roots")), "INSTANCE_NO_ROOTS")
    require(set(inst["roots"]) <= idset, "INSTANCE_ROOT_UNKNOWN")
    require(bool(inst.get("event", {}).get("removed_edge_ids")), "INSTANCE_NO_EVENT")
    require(set(inst["event"]["removed_edge_ids"]) <= seen, "INSTANCE_EVENT_EDGE_UNKNOWN")


def _adjacency(edges) -> dict:
    adj = defaultdict(list)
    for e in edges:
        adj[e["source"]].append(e["target"])
    return adj


def _reach(roots, edges) -> set:
    adj = _adjacency(edges)
    seen, q = set(roots), deque(roots)
    while q:
        cur = q.popleft()
        for nxt in adj[cur]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return seen


def oracle_target(inst: dict) -> set:
    """Exhaustive reference target. Recomputes global reachability twice."""
    validate_instance(inst)
    removed = set(inst["event"]["removed_edge_ids"])
    before = _reach(inst["roots"], inst["edges"])
    after = _reach(inst["roots"], [e for e in inst["edges"] if e["id"] not in removed])
    return before - after


def policy_none(inst: dict) -> dict:
    validate_instance(inst)
    return {"marked": set(), "inspected": 0}


def policy_coarse(inst: dict) -> dict:
    """Invalidate every derived node in the scope the event touched."""
    validate_instance(inst)
    removed = set(inst["event"]["removed_edge_ids"])
    scopes = {e["scope"] for e in inst["edges"] if e["id"] in removed}
    marked = {n["id"] for n in inst["nodes"] if n["kind"] in DERIVED_KINDS and n.get("scope") in scopes}
    return {"marked": marked, "inspected": len(inst["nodes"])}


def policy_global_reset(inst: dict) -> dict:
    """Invalidate every derived node in the whole state.

    This is the explicit whole-domain reset baseline. `policy_coarse` degenerates
    to a no-op whenever the projected scope label does not partition derived
    nodes, so the two are kept separate rather than merged.
    """
    validate_instance(inst)
    marked = {n["id"] for n in inst["nodes"] if n["kind"] in DERIVED_KINDS}
    return {"marked": marked, "inspected": len(inst["nodes"])}


def _changed_heads(inst: dict) -> list:
    removed = set(inst["event"]["removed_edge_ids"])
    return sorted({e["target"] for e in inst["edges"] if e["id"] in removed})


def policy_cascade(inst: dict) -> dict:
    """Forward reachability from the changed heads. Ignores surviving support."""
    validate_instance(inst)
    adj = _adjacency(inst["edges"])
    heads = _changed_heads(inst)
    marked, q, inspected = set(heads), deque(heads), set(heads)
    while q:
        cur = q.popleft()
        for nxt in adj[cur]:
            inspected.add(nxt)
            if nxt not in marked:
                marked.add(nxt)
                q.append(nxt)
    return {"marked": marked, "inspected": len(inspected)}


def policy_dominance(inst: dict) -> dict:
    """Candidate-restricted edge-dominance target.

    Visits only the forward candidate set and the direct predecessors it must
    consult, instead of recomputing global reachability. Equality with
    `oracle_target` is the claim under test, not an assumption.
    """
    validate_instance(inst)
    removed = set(inst["event"]["removed_edge_ids"])
    kept = [e for e in inst["edges"] if e["id"] not in removed]
    adj_all = _adjacency(inst["edges"])
    preds = defaultdict(list)
    for e in kept:
        preds[e["target"]].append(e["source"])

    heads = _changed_heads(inst)
    candidates, q = set(heads), deque(heads)
    while q:
        cur = q.popleft()
        for nxt in adj_all[cur]:
            if nxt not in candidates:
                candidates.add(nxt)
                q.append(nxt)

    roots = set(inst["roots"])
    inspected = set(candidates)
    affected, resolved = set(), {}
    # Iterate to a fixed point: a candidate survives when some kept predecessor
    # is a root or an already-surviving node outside the affected set.
    changed = True
    while changed:
        changed = False
        for node in sorted(candidates):
            if node in resolved:
                continue
            survives = None
            pending = False
            for p in preds[node]:
                inspected.add(p)
                if p in roots:
                    survives = True
                    break
                if p not in candidates:
                    survives = True
                    break
                if resolved.get(p) is True:
                    survives = True
                    break
                if p not in resolved:
                    pending = True
            if survives:
                resolved[node] = True
                changed = True
            elif not pending:
                resolved[node] = False
                affected.add(node)
                changed = True
    for node in candidates:
        if node not in resolved:
            # Only cycles remain; without a surviving entry they lose support.
            affected.add(node)
    return {"marked": affected, "inspected": len(inspected)}


POLICY_FNS = {
    "P0_NONE": policy_none,
    "P1_COARSE": policy_coarse,
    "P1G_GLOBAL_RESET": policy_global_reset,
    "P2_CASCADE": policy_cascade,
    "P3_DOMINANCE": policy_dominance,
}


def score(inst: dict, policy: str) -> dict:
    require(policy in POLICY_FNS, f"UNKNOWN_POLICY: {policy}")
    target = oracle_target(inst)
    out = POLICY_FNS[policy](inst)
    marked = out["marked"]
    results = {n["id"] for n in inst["nodes"] if n["kind"] == "result"}
    over = sorted(marked - target)
    under = sorted(target - marked)
    return {
        "instance_id": inst["instance_id"],
        "family": inst["family"],
        "policy": policy,
        "oracle_target": sorted(target),
        "marked": sorted(marked),
        "over_revocation": len(over),
        "under_revocation": len(under),
        "over_ids": over,
        "under_ids": under,
        "exact_target_match": not over and not under,
        "valid_results_total": len(results - target),
        "valid_results_preserved": len(results - target - marked),
        "stale_results_flagged": len(results & target & marked),
        "stale_results_total": len(results & target),
        "inspected_nodes": out["inspected"],
        "node_count": len(inst["nodes"]),
        "inspection_fraction": round(out["inspected"] / len(inst["nodes"]), 6),
    }


def batch_union_target(inst: dict) -> set:
    """Per-edge targets unioned. Used only to test non-composition."""
    validate_instance(inst)
    union = set()
    for edge_id in inst["event"]["removed_edge_ids"]:
        single = dict(inst)
        single["event"] = {"removed_edge_ids": [edge_id]}
        union |= oracle_target(single)
    return union
