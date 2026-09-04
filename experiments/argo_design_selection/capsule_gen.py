#!/usr/bin/env python3
"""Deterministic generator of dependency-targeting instances.

Families are fixed in advance and include cases where the dominance target and
the forward cascade agree (`chain`, `unrelated_only`) so the generator cannot
favour one policy by construction.
"""
from __future__ import annotations
import hashlib, json, random

FAMILIES = ("chain", "diamond_independent", "shared_result", "multi_edge_batch", "unrelated_only")
KIND_CHAIN = ("claim", "decision", "action", "result")


def _node(nid, kind, scope):
    return {"id": nid, "kind": kind, "scope": scope}


def _edge(eid, src, dst, relation, scope):
    return {"id": eid, "source": src, "target": dst, "relation": relation, "scope": scope}


def _branch(prefix, scope, depth, nodes, edges, parents, start_index=0):
    """Append a claim->decision->action->result chain under given parents."""
    prev = parents
    ids = []
    for i in range(depth):
        kind = KIND_CHAIN[min(i, len(KIND_CHAIN) - 1)]
        nid = f"{prefix}:{kind}{i}"
        nodes.append(_node(nid, kind, scope))
        for p in prev:
            edges.append(_edge(f"e:{p}->{nid}", p, nid, "depends_on", scope))
        ids.append(nid)
        prev = [nid]
    return ids


def build(family: str, seed: int) -> dict:
    rng = random.Random(f"{family}|{seed}")
    depth = rng.choice([3, 4, 5])
    nodes, edges, roots = [], [], []
    scope = "S1"
    if family == "chain":
        roots = ["src:a"]
        nodes.append(_node("src:a", "source", scope))
        _branch("m", scope, depth, nodes, edges, ["src:a"])
        removed = ["e:src:a->m:claim0"]
    elif family == "diamond_independent":
        roots = ["src:a", "src:b"]
        nodes += [_node("src:a", "source", scope), _node("src:b", "source", scope)]
        _branch("m", scope, depth, nodes, edges, ["src:a", "src:b"])
        removed = ["e:src:a->m:claim0"]
    elif family == "shared_result":
        roots = ["src:a", "src:b"]
        nodes += [_node("src:a", "source", scope), _node("src:b", "source", scope)]
        left = _branch("l", scope, depth, nodes, edges, ["src:a"])
        right = _branch("r", scope, depth, nodes, edges, ["src:b"])
        nodes.append(_node("shared:result", "result", scope))
        edges.append(_edge("e:l->shared", left[-1], "shared:result", "produces", scope))
        edges.append(_edge("e:r->shared", right[-1], "shared:result", "produces", scope))
        removed = ["e:src:a->l:claim0"]
    elif family == "multi_edge_batch":
        roots = ["src:a", "src:b"]
        nodes += [_node("src:a", "source", scope), _node("src:b", "source", scope)]
        _branch("m", scope, depth, nodes, edges, ["src:a", "src:b"])
        removed = ["e:src:a->m:claim0", "e:src:b->m:claim0"]
    elif family == "unrelated_only":
        roots = ["src:a", "src:z"]
        nodes += [_node("src:a", "source", scope), _node("src:z", "source", "S2")]
        _branch("m", scope, depth, nodes, edges, ["src:a"])
        _branch("u", "S2", 2, nodes, edges, ["src:z"])
        removed = ["e:src:z->u:claim0"]
    else:
        raise ValueError(family)
    inst = {
        "schema_version": "argo-dependency-targeting-instance/v1",
        "family": family,
        "seed": seed,
        "depth": depth,
        "roots": roots,
        "nodes": nodes,
        "edges": edges,
        "event": {"removed_edge_ids": removed, "kind": "source_support_withdrawn"},
    }
    payload = json.dumps({k: inst[k] for k in ("family", "seed", "roots", "nodes", "edges", "event")},
                         sort_keys=True, separators=(",", ":"))
    inst["instance_id"] = f"{family}-{seed}-" + hashlib.sha256(payload.encode()).hexdigest()[:12]
    return inst


def build_all(seeds) -> list:
    return [build(f, s) for f in FAMILIES for s in seeds]
