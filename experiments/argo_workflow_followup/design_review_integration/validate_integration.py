"""Validate review integration bytes and active research navigation, not efficacy."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate(root, contract_path):
    root = Path(root).resolve()
    errors = []
    def path(relative):
        value = (root / relative).resolve()
        if value != root and root not in value.parents:
            raise ValueError("OUTSIDE_ROOT")
        return value
    def load(relative):
        return json.loads(path(relative).read_text())
    def bound(item, label):
        p = path(item["path"])
        if not p.is_file() or sha(p) != item["sha256"]:
            errors.append("BINDING:" + label)
    try:
        contract = json.loads(Path(contract_path).read_text())
        bindings = contract["bindings"]
        for key, item in bindings.items(): bound(item, key)
        packet_sha = sha(path(bindings["packet"]["path"]))
        intake = load(bindings["intake"]["path"])
        if intake["packet_sha256"] != packet_sha: errors.append("INTAKE_PACKET")
        reports = intake["reports"]
        if len(reports) != 5 or len({r["json_path"] for r in reports}) != 5:
            errors.append("FIVE_ROLES_REQUIRED")
        findings = []
        for report in reports:
            p = path(report["json_path"])
            if sha(p) != report["json_sha256"]: errors.append("REVIEW_BYTES")
            obj = load(report["json_path"])
            if obj["packet_sha256"] != packet_sha: errors.append("REVIEW_PACKET")
            findings.extend(f["id"] for f in obj["findings"])
        responses = load(bindings["responses"]["path"])["findings"]
        response_ids = [r["finding_id"] for r in responses]
        if sorted(findings) != sorted(response_ids) or len(response_ids) != len(set(response_ids)):
            errors.append("FINDING_COVERAGE")
        study = load(bindings["study"]["path"])
        execution = study["execution"]
        if execution.get("authorized") is not False or execution.get("native_runtime_changes") is not False or type(execution.get("new_model_calls")) is not int or execution["new_model_calls"] != 0:
            errors.append("EXECUTION_AUTHORITY")
        if study["primary"].get("no_archive_or_best_seed") is not True:
            errors.append("SELECTION_POLICY")
        completion = load(bindings["completion"]["path"])
        if completion.get("research_status") != "NOT_COMPLETE" or any(completion.get(k) is not False for k in ["writing_allowed", "publication_allowed", "prototype_build_authorized"]):
            errors.append("COMPLETION_AUTHORITY")
        nav = contract["navigation"]
        nxt, handoff, graph = (load(nav[k]) for k in ["next", "handoff", "graph"])
        integration = nxt["research_review_integration"]
        if integration["path"] != bindings["study"]["path"] or integration["sha256"] != sha(path(integration["path"])):
            errors.append("NEXT_INTEGRATION")
        bound(handoff["entrypoint"], "ENTRYPOINT")
        for item in handoff["active_documents"]: bound(item, "ACTIVE_DOCUMENT:" + item["path"])
        if handoff["acyclic_binding"]["next_sha256"] != sha(path(nav["next"])):
            errors.append("NEXT_HANDOFF")
        nodes = graph["nodes"]
        edges = graph["edges"]
        by_id = {n["id"]: n for n in nodes}
        edge_ids = {e["id"] for e in edges}
        if len(by_id) != len(nodes) or len(edge_ids) != len(edges): errors.append("DUPLICATE_IDS")
        if any(e["source"] not in by_id or e["target"] not in by_id for e in edges): errors.append("DANGLING_EDGE")
        chain = handoff["active_chain"]
        if not set(contract["required_nodes"]) <= set(chain["current_node_ids"]): errors.append("REQUIRED_ROUTE")
        if not set(chain["current_edge_ids"]) <= edge_ids: errors.append("CHAIN_EDGES")
        for node_id in chain["current_node_ids"]:
            node = by_id.get(node_id)
            if node is None:
                errors.append("CHAIN_NODE"); continue
            relative = node.get("evidence", node.get("path"))
            if relative is None or "sha256" not in node: errors.append("NODE_IDENTITY:" + node_id)
            else: bound({"path":relative, "sha256":node["sha256"]}, "NODE:" + node_id)
        root_node = by_id.get("root:research_direction")
        if root_node:
            if root_node.get("active_design_sha256") != sha(path(bindings["design"]["path"])) or root_node.get("active_handoff_sha256") != sha(path(nav["handoff"])):
                errors.append("ROOT_NAVIGATION")
        if "current_nodes" in chain:
            expected = [{"id": n, "kind": by_id[n]["kind"]} for n in chain["current_node_ids"] if n in by_id]
            if chain["current_nodes"] != expected: errors.append("CHAIN_NODE_REFS")
        if "current_edges" in chain:
            edge_map = {e["id"]:e for e in edges}
            expected_edges = [edge_map[e] for e in chain["current_edge_ids"] if e in edge_map]
            if chain["current_edges"] != expected_edges: errors.append("CHAIN_EDGE_REFS")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append("SCHEMA_OR_READ:" + type(exc).__name__)
    return {"passed": not errors, "errors": errors, "scope": "review count/identity, finding coverage, active-node byte bindings and declared closed authority only"}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True)
    a = p.parse_args()
    result = validate(a.root, a.contract)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
