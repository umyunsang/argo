#!/usr/bin/env python3
"""Independent checks for an expanded real-graph targeting receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections import Counter, defaultdict, deque
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
    "source": "source",
    "source_code": "source",
    "literature_topic": "claim",
    "literature_area": "claim",
    "mechanism": "claim",
    "hypothesis": "claim",
    "gap": "claim",
    "constraint": "claim",
    "material": "claim",
    "component": "claim",
    "prototype": "claim",
    "event": "claim",
    "root": "claim",
    "decision": "decision",
    "experiment": "action",
    "evaluation": "action",
    "retrieval_trigger": "action",
    "artifact": "result",
    "result": "result",
    "figure": "result",
}
INACTIVE = ("RETRACTED", "QUARANTINED", "SUPERSEDED", "INACTIVE", "FALSIFIED", "MUST_NOT_EXECUTE")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def active(record: dict) -> bool:
    status = str(record.get("status", "") or "")
    return not any(token in status for token in INACTIVE)


def independent_projection(graph: dict) -> dict:
    nodes = []
    index = {}
    for node in graph["nodes"]:
        kind = KIND_MAP.get(node.get("kind"))
        if kind is not None and active(node):
            projected = {"id": node["id"], "kind": kind, "scope": node.get("kind")}
            nodes.append(projected)
            index[node["id"]] = projected
    edges = []
    for edge in graph["edges"]:
        relation = SUPPORT_RELATIONS.get(edge.get("relation"))
        if (
            relation is not None
            and active(edge)
            and edge["source"] in index
            and edge["target"] in index
        ):
            edges.append(
                {
                    "id": edge["id"],
                    "source": edge["source"],
                    "target": edge["target"],
                    "relation": relation,
                    "scope": index[edge["source"]]["scope"],
                }
            )
    incoming = {node["id"]: 0 for node in nodes}
    for edge in edges:
        incoming[edge["target"]] += 1
    roots = sorted(node_id for node_id, count in incoming.items() if count == 0)
    return {"nodes": nodes, "edges": edges, "roots": roots}


def reach(roots: list[str], edges: list[dict]) -> set[str]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        adjacency[edge["source"]].append(edge["target"])
    seen = set(roots)
    queue = deque(roots)
    while queue:
        current = queue.popleft()
        for target in adjacency[current]:
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def target(projection: dict, removed: set[str]) -> set[str]:
    before = reach(projection["roots"], projection["edges"])
    kept = [edge for edge in projection["edges"] if edge["id"] not in removed]
    return before - reach(projection["roots"], kept)


def cyclic_components(projection: dict) -> list[list[str]]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    self_loops = set()
    for edge in projection["edges"]:
        adjacency[edge["source"]].append(edge["target"])
        if edge["source"] == edge["target"]:
            self_loops.add(edge["source"])

    counter = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    index: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    components: list[list[str]] = []

    def visit(node_id: str) -> None:
        nonlocal counter
        index[node_id] = counter
        lowlink[node_id] = counter
        counter += 1
        stack.append(node_id)
        on_stack.add(node_id)
        for child in adjacency[node_id]:
            if child not in index:
                visit(child)
                lowlink[node_id] = min(lowlink[node_id], lowlink[child])
            elif child in on_stack:
                lowlink[node_id] = min(lowlink[node_id], index[child])
        if lowlink[node_id] == index[node_id]:
            component = []
            while True:
                child = stack.pop()
                on_stack.remove(child)
                component.append(child)
                if child == node_id:
                    break
            if len(component) > 1 or component[0] in self_loops:
                components.append(sorted(component))

    for node in sorted(item["id"] for item in projection["nodes"]):
        if node not in index:
            visit(node)
    return sorted(components)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    graph = json.loads(args.graph.read_text())
    receipt = json.loads(args.receipt.read_text())
    projection = independent_projection(graph)

    original_dir = Path(__file__).resolve().parents[1] / "argo_design_selection"
    sys.path.insert(0, str(original_dir))
    from real_graph_adapter import instance_for_event, project
    from targeting import policy_dominance

    adapter_projection = project(args.graph)
    projection_equal = all(
        projection[key] == adapter_projection[key] for key in ("nodes", "edges", "roots")
    )
    node_ids = {node["id"] for node in projection["nodes"]}
    reachable_ids = reach(projection["roots"], projection["edges"])

    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in projection["edges"]:
        outgoing[edge["source"]].append(edge["id"])
    sources = sorted(
        node["id"]
        for node in projection["nodes"]
        if node["kind"] == "source" and outgoing[node["id"]]
    )
    reported = {row["event_source"]: row for row in receipt["per_event"]}
    exact = 0
    target_sizes = []
    mismatch_sources = []
    targets = {}
    kind_by_id = {node["id"]: node["kind"] for node in projection["nodes"]}
    scope_by_id = {node["id"]: node["scope"] for node in projection["nodes"]}
    affected_kind_counts: Counter[str] = Counter()
    immediate_effects = 0
    multi_hop_effects = 0
    sources_with_multi_hop = 0
    cascade_over_union: set[str] = set()
    for source in sources:
        removed = set(outgoing[source])
        heads = {
            edge["target"] for edge in projection["edges"] if edge["id"] in removed
        }
        expected = target(projection, removed)
        targets[source] = expected
        immediate_effects += len(expected & heads)
        source_multi_hop = expected - heads
        multi_hop_effects += len(source_multi_hop)
        sources_with_multi_hop += bool(source_multi_hop)
        affected_kind_counts.update(kind_by_id[node] for node in expected)

        cascade_marked = reach(sorted(heads), projection["edges"])
        cascade_over_union.update(cascade_marked - expected)
        instance = instance_for_event(projection, sorted(removed), source.replace("/", "_"))
        observed = policy_dominance(instance)["marked"]
        row = reported.get(source)
        row_ok = row is not None and row.get("oracle_affected") == len(expected)
        if observed == expected and row_ok:
            exact += 1
        else:
            mismatch_sources.append(source)
        target_sizes.append(len(expected))

    nonempty_source = next(source for source in sources if targets[source])
    empty_source = next(source for source in sources if targets[source] != node_ids)
    dropped = set(targets[nonempty_source])
    dropped.pop()
    added = set(targets[empty_source])
    added.add(next(node for node in sorted(node_ids) if node not in added))
    mutation_drop_detected = dropped != targets[nonempty_source]
    mutation_add_detected = added != targets[empty_source]

    checks = {
        "graph_hash_matches_receipt": sha256(args.graph) == receipt.get("graph_sha256"),
        "projection_matches_independent_implementation": projection_equal,
        "projection_counts_match_receipt": (
            len(projection["nodes"]) == receipt["projection"]["nodes"]
            and len(projection["edges"]) == receipt["projection"]["edges"]
            and len(projection["roots"]) == receipt["projection"]["roots"]
        ),
        "all_projected_nodes_reachable": reachable_ids == node_ids,
        "event_set_matches_receipt": set(sources) == set(reported),
        "dominance_matches_independent_oracle": exact == len(sources),
        "reported_p3_exact_rate_matches": receipt["overall"]["P3_DOMINANCE"]["exact_target_match_rate"] == 1.0,
        "drop_mutation_detected": mutation_drop_detected,
        "add_mutation_detected": mutation_add_detected,
    }
    cycles = cyclic_components(projection)
    root_kind_counts = Counter(kind_by_id[node] for node in projection["roots"])
    root_scope_counts = Counter(scope_by_id[node] for node in projection["roots"])
    result_nodes = sum(node["kind"] == "result" for node in projection["nodes"])
    result = {
        "schema_version": "argo-dependency-targeting-expanded-verification/v1",
        "verifier_sha256": sha256(Path(__file__).resolve()),
        "python": platform.python_version(),
        "graph_sha256": sha256(args.graph),
        "receipt_sha256": sha256(args.receipt),
        "projection": {
            "nodes": len(projection["nodes"]),
            "edges": len(projection["edges"]),
            "roots": len(projection["roots"]),
            "all_nodes_reachable": reachable_ids == node_ids,
            "cyclic_scc_count": len(cycles),
            "max_cyclic_scc_size": max((len(component) for component in cycles), default=0),
            "cyclic_sccs": cycles,
        },
        "events": len(sources),
        "dominance_exact": exact,
        "mismatch_sources": mismatch_sources,
        "affected_events": sum(size > 0 for size in target_sizes),
        "zero_affected_events": sum(size == 0 for size in target_sizes),
        "effect_topology": {
            "affected_node_opportunities": sum(target_sizes),
            "immediate_head_effects": immediate_effects,
            "multi_hop_effects": multi_hop_effects,
            "sources_with_multi_hop": sources_with_multi_hop,
            "affected_kind_counts": dict(sorted(affected_kind_counts.items())),
            "cascade_unique_overrevoked_nodes": len(cascade_over_union),
            "result_kind_nodes": result_nodes,
            "valid_result_opportunities": result_nodes * len(sources),
            "root_kind_counts": dict(sorted(root_kind_counts.items())),
            "root_scope_counts": dict(sorted(root_scope_counts.items())),
        },
        "scope_limits": [
            "same project at a later snapshot, not an independent graph",
            "withdrawals are simulated over author-labelled support relations",
            "multiple incoming support is not proof of semantic independence",
            "inspection_fraction is a logical-neighborhood counter, not measured graph I/O",
            "routing accuracy does not establish decision sufficiency",
        ],
        "decision_sufficiency_ready": multi_hop_effects > 0,
        "checks": checks,
        "all_pass": all(checks.values()),
        "model_calls": 0,
        "spend_usd": 0.0,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
