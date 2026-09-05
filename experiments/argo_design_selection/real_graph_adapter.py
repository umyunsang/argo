#!/usr/bin/env python3
"""Project a real research context graph into dependency-targeting instances.

The projection is explicit about what it keeps: only edges whose relation is a
support-bearing dependency become dependency edges, and only nodes that are
reachable evidence, claims, decisions, actions or results become graph nodes.
Everything else is reported as excluded rather than silently dropped.
"""
from __future__ import annotations
import json
from pathlib import Path

SUPPORT_RELATIONS = {
    "supports": "supports",
    "supports_prior_mechanism": "supports",
    "supports_or_counters_hypothesis": "supports",
    "narrows_or_informs": "informs",
    "informs_decision": "informs",
    "formulates": "informs",
    "instantiates": "governs_action",
    "executes": "governs_action",
    "produces": "produces",
    "measures": "produces",
    "governs": "informs",
    "establishes_lineage": "informs",
    "contains": "informs",
    "evaluated_by": "informs",
}
KIND_MAP = {
    "source": "source", "source_code": "source",
    "literature_topic": "claim", "literature_area": "claim", "mechanism": "claim",
    "hypothesis": "claim", "gap": "claim", "constraint": "claim", "material": "claim",
    "component": "claim", "prototype": "claim", "event": "claim", "root": "claim",
    "decision": "decision",
    "experiment": "action", "evaluation": "action", "retrieval_trigger": "action",
    "artifact": "result", "result": "result", "figure": "result",
}
INACTIVE_STATUS_TOKENS = ("RETRACTED", "QUARANTINED", "SUPERSEDED", "INACTIVE", "FALSIFIED", "MUST_NOT_EXECUTE")


def is_active(node_or_edge: dict) -> bool:
    status = str(node_or_edge.get("status", "") or "")
    return not any(tok in status for tok in INACTIVE_STATUS_TOKENS)


def project(graph_path: Path) -> dict:
    g = json.loads(Path(graph_path).read_text(encoding="utf-8"))
    excluded_nodes, excluded_edges = [], []
    nodes, index = [], {}
    for n in g["nodes"]:
        kind = KIND_MAP.get(n.get("kind"))
        if kind is None or not is_active(n):
            excluded_nodes.append({"id": n.get("id"), "kind": n.get("kind"), "status": n.get("status")})
            continue
        rec = {"id": n["id"], "kind": kind, "scope": n.get("kind")}
        nodes.append(rec)
        index[n["id"]] = rec
    edges = []
    for e in g["edges"]:
        rel = SUPPORT_RELATIONS.get(e.get("relation"))
        if rel is None or not is_active(e) or e["source"] not in index or e["target"] not in index:
            excluded_edges.append({"id": e.get("id"), "relation": e.get("relation"), "status": e.get("status")})
            continue
        edges.append({"id": e["id"], "source": e["source"], "target": e["target"],
                      "relation": rel, "scope": index[e["source"]]["scope"]})
    incoming = {n["id"]: 0 for n in nodes}
    for e in edges:
        incoming[e["target"]] += 1
    roots = sorted(n["id"] for n in nodes if incoming[n["id"]] == 0)
    return {"nodes": nodes, "edges": edges, "roots": roots,
            "excluded_nodes": excluded_nodes, "excluded_edges": excluded_edges}


def instance_for_event(projection: dict, removed_edge_ids: list, label: str) -> dict:
    return {
        "schema_version": "argo-dependency-targeting-instance/v1",
        "family": "real_context_graph",
        "instance_id": f"real-{label}",
        "seed": None,
        "roots": projection["roots"],
        "nodes": projection["nodes"],
        "edges": projection["edges"],
        "event": {"removed_edge_ids": removed_edge_ids, "kind": "source_support_withdrawn", "label": label},
    }


def support_multiplicity(projection: dict) -> dict:
    counts = {}
    for e in projection["edges"]:
        counts[e["target"]] = counts.get(e["target"], 0) + 1
    multi = sorted(k for k, v in counts.items() if v > 1)
    return {"nodes_with_multiple_incoming_support": len(multi), "examples": multi[:10],
            "max_incoming": max(counts.values()) if counts else 0}
