#!/usr/bin/env python3
"""Validate the combined base+overlay causal graph without modifying the canonical graph."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import sys
import time
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def canonical_hash(node: dict) -> str:
    payload = {k: v for k, v in node.items() if k != "content_hash"}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def active_view(overlay: dict, base: dict) -> tuple[dict, list]:
    nodes = {n["id"]: copy.deepcopy(n) for n in base.get("nodes", [])}
    for patch in overlay.get("base_status_changes", []):
        if patch["node_id"] in nodes:
            nodes[patch["node_id"]]["status"] = patch["new_status"]
    for node in overlay["nodes"]:
        nodes[node["id"]] = copy.deepcopy(node)
    edges = {e["id"]: copy.deepcopy(e) for e in base.get("edges", [])}
    for patch in overlay.get("base_edge_changes", []):
        if patch["edge_id"] in edges:
            edges[patch["edge_id"]]["status"] = patch["new_status"]
    for edge in overlay["edges"]:
        edges[edge["id"]] = copy.deepcopy(edge)
    return nodes, list(edges.values())


def validate(overlay: dict, base: dict) -> dict:
    failures: list[str] = []
    nodes, edges = active_view(overlay, base)
    overlay_nodes = {n["id"]: n for n in overlay["nodes"]}
    active_statuses = set(overlay["active_statuses"])
    active = {nid for nid, n in nodes.items() if n.get("status") in active_statuses}
    root = overlay["root_node_id"]

    bad_hashes = [nid for nid, n in overlay_nodes.items()
                  if n.get("content_hash") != canonical_hash(n)]
    if bad_hashes:
        failures.append("content hash mismatch: " + ", ".join(sorted(bad_hashes)))

    kinds = {n["kind"] for n in overlay_nodes.values()}
    missing_kinds = set(overlay["declared_node_kinds"]) - kinds
    if missing_kinds:
        failures.append("missing required node kinds: " + ", ".join(sorted(missing_kinds)))

    absent_endpoints = [e["id"] for e in edges if e.get("source") not in nodes or e.get("target") not in nodes]
    if absent_endpoints:
        failures.append("combined edge endpoint absent: " + ", ".join(sorted(absent_endpoints)))
    active_edges = [e for e in edges if e.get("status", "ACTIVE") == "ACTIVE" and
                    e.get("source") in active and e.get("target") in active]
    used_relations = {e["relation"] for e in active_edges}
    undeclared = used_relations - set(overlay["declared_relations"])
    if undeclared:
        failures.append("undeclared relations: " + ", ".join(sorted(undeclared)))

    adjacency = {nid: [] for nid in active}
    for edge in active_edges:
        adjacency[edge["source"]].append(edge["target"])
    reached = set()
    queue = deque([root])
    while queue:
        current = queue.popleft()
        if current in reached:
            continue
        reached.add(current)
        queue.extend(adjacency.get(current, []))
    unreachable = active - reached
    if root not in active:
        failures.append("root is not active")
    if unreachable:
        failures.append("combined active nodes unreachable from root: " + ", ".join(sorted(unreachable)))

    edge_pairs = {(e["source"], e["target"]) for e in active_edges}
    chain = overlay["authority_chain"]
    for source, target in zip(chain, chain[1:]):
        if source not in active or target not in active or (source, target) not in edge_pairs:
            failures.append(f"authority chain broken: {source} -> {target}")

    for node in overlay_nodes.values():
        if node["id"] not in active:
            continue
        target = node.get("next_action_target")
        if target and target not in active:
            failures.append(f"stale next_action target: {node['id']} -> {target}")
        if node["kind"] == "source_span":
            required = ("source_path", "source_sha256", "line_start", "line_end",
                        "excerpt_sha256", "locator_id")
            missing = [key for key in required if not node.get(key)]
            if missing:
                failures.append(f"source span missing binding: {node['id']} -> {missing}")
            else:
                path = REPO / node["source_path"]
                actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
                lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
                excerpt = "\n".join(lines[node["line_start"]-1:node["line_end"]])
                excerpt_hash = hashlib.sha256(excerpt.encode()).hexdigest()
                if actual != node["source_sha256"] or excerpt_hash != node["excerpt_sha256"]:
                    failures.append(f"source path/hash/span mismatch: {node['id']}")
        if node["kind"] == "result":
            required = set(overlay["active_result_requirements"])
            missing = [key for key in required if not node.get(key)]
            if missing:
                failures.append(f"active result missing identities: {node['id']} -> {missing}")
            protocol = nodes.get(node.get("protocol_id"), {})
            if node.get("result_type") == "SCIENTIFIC_EFFICACY":
                if protocol.get("protocol_status") != "SEALED" or not protocol.get("protocol_identity"):
                    failures.append(f"scientific result lacks sealed protocol identity: {node['id']}")
            elif node.get("result_type") != "AUDIT_FINDING" or node.get("efficacy_claim") is not False:
                failures.append(f"non-efficacy result is not explicitly an audit finding: {node['id']}")
        if node["kind"] == "claim":
            grounded = any(e["target"] == node["id"] and e["relation"] in {"grounds", "supports"}
                           for e in active_edges)
            if not grounded:
                failures.append(f"active claim lacks source/result grounding: {node['id']}")
        if node["kind"] == "decision":
            required = ("alternatives", "falsifier", "uncertainty", "stopping_guardrails",
                        "admission_rule")
            missing = [key for key in required if not node.get(key)]
            if missing:
                failures.append(f"active decision missing admission fields: {node['id']} -> {missing}")

    for edge in active_edges:
        target_kind = nodes[edge["target"]]["kind"]
        if edge["relation"] == "refines_research" and target_kind != "research_state":
            failures.append(f"research refinement crosses lineage: {edge['id']}")
        if edge["relation"] == "refines_engine" and target_kind != "engine_version":
            failures.append(f"engine refinement crosses lineage: {edge['id']}")

    ablations = [e for e in active_edges if e["relation"] == "ablation_of"]
    expected_removals = {"arm:g0c1f1", "arm:g1c0f1", "arm:g1c1f0"}
    if {e["source"] for e in ablations} != expected_removals or any(
            e["target"] != "arm:g1c1f1" for e in ablations):
        failures.append("ablation edges must be only -G/-C/-F pointing to FULL")

    required_scope = {"Study A", "T3 Study B", "T1 prime pilot and block", "B2 current harness",
                      "B2-G/B2-P/B2-R", "signed legacy four-removal model",
                      "latest clean-clone attempt"}
    observed_scope = {x["scope"] for x in overlay.get("scope_status_changes", [])}
    if observed_scope != required_scope:
        failures.append("status overlay coverage mismatch")

    base_edges = {e["id"]: e for e in base.get("edges", [])}
    base_nodes = {n["id"]: n for n in base.get("nodes", [])}
    changed_edges = {e["edge_id"]: e for e in overlay.get("base_edge_changes", [])}
    changed_nodes = {n["node_id"]: n for n in overlay.get("base_status_changes", [])}
    for nid, node in base_nodes.items():
        is_retracted = node.get("status") == "RETRACTED" or "RETRACTED" in changed_nodes.get(nid, {}).get("new_status", "")
        if not is_retracted:
            continue
        for edge in base_edges.values():
            if edge.get("source") == nid and edge.get("relation") == "supports":
                change = changed_edges.get(edge["id"])
                if not change or not change.get("new_status", "").startswith("INACTIVE"):
                    failures.append(f"retracted result retains active supports path: {edge['id']}")

    h6 = overlay_nodes.get("hypothesis:h6-full", {}).get("summary", "")
    h7 = overlay_nodes.get("hypothesis:h7-recovery", {}).get("summary", "")
    if "every comparator" not in h6 or "reliability-adjusted" not in h6:
        failures.append("H6 summary is not faithful to the directive")
    if "Separated graph-backed research/engine lineage" not in h7 or "noninferiority" not in h7:
        failures.append("H7 summary is not faithful to the directive")
    for hypothesis_id in ("hypothesis:h6-full", "hypothesis:h7-recovery"):
        hypothesis = overlay_nodes[hypothesis_id]
        path = REPO / hypothesis.get("source_path", "")
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        excerpt = "\n".join(lines[hypothesis.get("line_start", 0)-1:hypothesis.get("line_end", 0)])
        excerpt_hash = hashlib.sha256(excerpt.encode()).hexdigest()
        if actual != hypothesis.get("source_sha256") or excerpt_hash != hypothesis.get("excerpt_sha256"):
            failures.append(f"hypothesis authority path/hash/span mismatch: {hypothesis_id}")

    checks = {
        "combined_root_reachability": not any(x.startswith("combined active nodes unreachable") or x == "root is not active" for x in failures),
        "combined_endpoint_integrity": not any(x.startswith("combined edge endpoint absent") for x in failures),
        "exact_authority_chain": not any(x.startswith("authority chain broken") for x in failures),
        "vocabulary_closure": not any(x.startswith("missing required node kinds") or x.startswith("undeclared relations") for x in failures),
        "content_identity": not any(x.startswith("content hash mismatch") for x in failures),
        "source_path_hash_span_binding": not any(x.startswith("source span") or x.startswith("source path") for x in failures),
        "scientific_result_protocol_gate": not any(x.startswith("scientific result") or x.startswith("non-efficacy result") for x in failures),
        "decision_admission_rule": not any(x.startswith("active decision") for x in failures),
        "lineage_closure": not any("crosses lineage" in x for x in failures),
        "retraction_propagation": not any(x.startswith("retracted result retains") for x in failures),
        "stale_action_checks": not any(x.startswith("stale next_action") for x in failures),
        "ablation_semantics": not any(x.startswith("ablation edges") for x in failures),
        "status_overlay_coverage": not any(x.startswith("status overlay") for x in failures),
        "hypothesis_fidelity": not any(x.startswith("H6") or x.startswith("H7") or x.startswith("hypothesis authority") for x in failures),
    }
    active_scientific = sum(1 for nid in active if nodes[nid].get("result_type") == "SCIENTIFIC_EFFICACY")
    return {"passed": not failures, "scope":"COMBINED_BASE_PLUS_OVERLAY_ACTIVE_VIEW",
            "checks": checks, "failures": failures, "base_node_count":len(base.get("nodes",[])),
            "overlay_node_count":len(overlay_nodes), "combined_node_count":len(nodes),
            "active_node_count":len(active), "reachable_active_node_count":len(active & reached),
            "active_scientific_efficacy_result_count":active_scientific,
            "node_kind_count":len(kinds), "used_active_relation_count":len(used_relations)}


def rehash(node: dict) -> None:
    node["content_hash"] = canonical_hash(node)


def self_test(overlay: dict, base: dict) -> dict:
    fixtures = []
    def run(name: str, mutate, expected: str) -> None:
        candidate = copy.deepcopy(overlay); mutate(candidate)
        result = validate(candidate, base)
        caught = any(expected in reason for reason in result["failures"])
        fixtures.append({"name":name,"expected_reason":expected,"caught":caught,
                         "observed_failures":result["failures"]})
    def orphan(x):
        n=dict(x["nodes"][0]); n.update(id="objective:orphan",summary="orphan",next_action_target=None); rehash(n); x["nodes"].append(n)
    run("unreachable active node",orphan,"combined active nodes unreachable from root")
    run("undeclared relation",lambda x:x["edges"].append({"id":"mut-rel","source":x["root_node_id"],"target":"requirement:causal_realignment","relation":"invented","status":"ACTIVE"}),"undeclared relations")
    run("content mutation",lambda x:x["nodes"][0].update(summary="mutated"),"content hash mismatch")
    run("broken authority chain",lambda x:x.update(edges=[e for e in x["edges"] if e["id"]!="e119"]),"authority chain broken")
    def stale(x):
        n=next(n for n in x["nodes"] if n["id"]=="decision:causal_realignment"); n["next_action_target"]="result:missing"; rehash(n)
    run("stale next action",stale,"stale next_action target")
    run("retracted supports edge",lambda x:x.update(base_edge_changes=[]),"retracted result retains active supports path")
    def cross(x):
        engine = next(n for n in x["nodes"] if n["id"] == "engine_version:fixed_inherited_substrate")
        engine["status"] = "ACTIVE"
        rehash(engine)
        x["edges"].append({"id":"mut-cross","source":"protocol:gcf_prereg_draft","target":"engine_version:fixed_inherited_substrate","relation":"refines_research","status":"ACTIVE"})
    run("cross-lineage refinement",cross,"research refinement crosses lineage")
    def missing_result(x):
        n=next(n for n in x["nodes"] if n["id"]=="result:current_efficacy_inadmissible"); n.pop("protocol_id"); rehash(n)
    run("result without protocol identity",missing_result,"active result missing identities")
    def scientific_on_draft(x):
        n=next(n for n in x["nodes"] if n["id"]=="result:current_efficacy_inadmissible"); n["result_type"]="SCIENTIFIC_EFFICACY"; n["efficacy_claim"]=True; rehash(n)
    run("scientific result on draft protocol",scientific_on_draft,"scientific result lacks sealed protocol identity")
    def no_admission(x):
        n=next(n for n in x["nodes"] if n["id"]=="decision:causal_realignment"); n.pop("admission_rule"); rehash(n)
    run("decision without admission rule",no_admission,"active decision missing admission fields")
    def bad_span(x):
        n=next(n for n in x["nodes"] if n["kind"]=="source_span"); n["excerpt_sha256"]="0"*64; rehash(n)
    run("source span hash mismatch",bad_span,"source path/hash/span mismatch")
    run("absent edge endpoint",lambda x:x["edges"].append({"id":"mut-endpoint","source":x["root_node_id"],"target":"node:absent","relation":"supports","status":"ACTIVE"}),"combined edge endpoint absent")
    def bad_h6_span(x):
        n=next(n for n in x["nodes"] if n["id"]=="hypothesis:h6-full"); n["excerpt_sha256"]="0"*64; rehash(n)
    run("H6 authority span mismatch",bad_h6_span,"hypothesis authority path/hash/span mismatch")
    return {"passed":all(x["caught"] for x in fixtures),"fixtures":fixtures}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--overlay",default="07-context-graph-repair-overlay.json"); parser.add_argument("--base",default="../../../paper/context-graph.json"); parser.add_argument("--out",default="context-graph-validation-receipt.json"); args=parser.parse_args()
    start=time.perf_counter(); overlay_path=(HERE/args.overlay).resolve(); base_path=(HERE/args.base).resolve()
    overlay=json.loads(overlay_path.read_text(encoding="utf-8")); base=json.loads(base_path.read_text(encoding="utf-8"))
    result=validate(overlay,base); mutations=self_test(overlay,base); exit_code=0 if result["passed"] and mutations["passed"] else 1
    script=Path(__file__).resolve(); runtime=time.perf_counter()-start
    receipt={"schema_version":"argo-context-graph-overlay-validation/v2","checked_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"deterministic_zero_cost_validator","command":f"{sys.executable} {script.name}","validator_script_path":str(script),"validator_script_sha256":hashlib.sha256(script.read_bytes()).hexdigest(),"runtime_seconds":runtime,"exit_code":exit_code,"overlay_path":str(overlay_path),"overlay_sha256":hashlib.sha256(overlay_path.read_bytes()).hexdigest(),"base_path":str(base_path),"base_sha256":hashlib.sha256(base_path.read_bytes()).hexdigest(),"result":result,"failing_first_mutations":mutations,"canonical_graph_modified":False}
    (HERE/args.out).resolve().write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False,indent=2)); return exit_code

if __name__=="__main__": raise SystemExit(main())
