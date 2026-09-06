#!/usr/bin/env python3
"""Validate the acyclic canonical research projection and fresh-agent handoff."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def validate(root,contract_path):
 root=Path(root);contract=json.loads(Path(contract_path).read_text());errors=[]
 try:
  graph=json.loads((root/contract["objects"]["graph"]).read_text());handoff=json.loads((root/contract["objects"]["handoff"]).read_text());nxt=json.loads((root/contract["objects"]["next"]).read_text());root_path=root/contract["objects"]["root"];design_path=root/contract["objects"]["active_design"]
 except Exception as exc:return {"passed":False,"errors":["READ:"+type(exc).__name__]}
 nodes={n["id"]:n for n in graph.get("nodes",[])};edges={e["id"]:e for e in graph.get("edges",[])};used={e.get("relation") for e in edges.values()};vocab=graph.get("edge_vocabulary",[])
 if len(vocab)!=len(set(vocab)) or used-set(vocab) or set(vocab)-used:errors.append("RELATION_VOCABULARY")
 chain=handoff.get("active_chain",{});node_ids=chain.get("current_node_ids",[]);edge_ids=chain.get("current_edge_ids",[])
 if any(x not in nodes for x in node_ids) or any(x not in edges for x in edge_ids):errors.append("CHAIN_IDS")
 expected_node_refs=[{"id":x,"kind":nodes[x]["kind"]} for x in node_ids if x in nodes]
 if chain.get("current_nodes")!=expected_node_refs:errors.append("CHAIN_NODE_REFS")
 if chain.get("current_edges")!=[edges[x] for x in edge_ids if x in edges]:errors.append("CHAIN_EDGE_REFS")
 if not set(contract.get("required_route",[])).issubset(set(node_ids)) or not set(contract.get("required_edge_ids",[])).issubset(set(edge_ids)):errors.append("REQUIRED_ROUTE")
 old=edges.get(contract.get("historical_edge"),{})
 if old.get("active") is not False or old.get("historical") is not True or old.get("superseded_by") not in edges:errors.append("HISTORICAL_EDGE")
 for doc in handoff.get("active_documents",[]):
  p=root/doc.get("path","")
  if not p.is_file() or sha(p)!=doc.get("sha256"):errors.append("ACTIVE_DOCUMENT:"+str(doc.get("role")))
 if handoff.get("acyclic_binding",{}).get("next_sha256")!=sha(root/contract["objects"]["next"]):errors.append("NEXT_HANDOFF_BINDING")
 if handoff.get("acyclic_binding",{}).get("order")!=contract.get("binding_order"):errors.append("BINDING_ORDER")
 root_node=nodes.get("root:research_direction",{});handoff_node=nodes.get("artifact:active_graph_handoff",{});design_node=nodes.get("artifact:active_integrated_research_design",{});next_node=nodes.get("artifact:next_information_experiment",{})
 if root_node.get("sha256")!=sha(root_path) or root_node.get("active_handoff_sha256")!=sha(root/contract["objects"]["handoff"]):errors.append("ROOT_BINDING")
 if handoff_node.get("sha256")!=sha(root/contract["objects"]["handoff"]):errors.append("HANDOFF_NODE")
 if design_node.get("sha256")!=sha(design_path) or root_node.get("active_design_sha256")!=sha(design_path):errors.append("DESIGN_BINDING")
 if next_node.get("sha256")!=sha(root/contract["objects"]["next"]):errors.append("NEXT_NODE")
 cf=nxt.get("current_frontier",{})
 for pk,hk in [("design","design_sha256"),("proposal","proposal_sha256"),("manifest","manifest_sha256"),("schemas","schemas_sha256"),("adapter_v2","adapter_v2_sha256"),("state_projection","state_projection_sha256"),("lifecycle","lifecycle_sha256"),("protocol","protocol_sha256"),("runner","runner_sha256"),("episode","episode_sha256"),("approval","approval_sha256")]:
  p=root/cf.get(pk,"")
  if not p.is_file() or sha(p)!=cf.get(hk):errors.append("FRONTIER_BINDING:"+pk)
 if not set(contract.get("required_prohibited_claims",[])).issubset(set(handoff.get("prohibited_claims",[]))):errors.append("PROHIBITED_CLAIMS")
 if handoff.get("inference_scope",{}).get("candidate_n")!=2 or nxt.get("inference_scope",{}).get("candidate_n")!=2:errors.append("INFERENCE_SCOPE")
 lineage=graph.get("projection_lineage",{})
 if lineage.get("predecessor_snapshot_sha256")!=contract.get("predecessor",{}).get("predecessor_snapshot_sha256") or "successor" not in lineage.get("semantics",""):errors.append("PREDECESSOR")
 if graph.get("evidence_cutoff")!="2026-09-06":errors.append("EVIDENCE_CUTOFF")
 return {"passed":not errors,"errors":errors,"nodes":len(nodes),"edges":len(edges),"active_chain_nodes":len(node_ids),"active_chain_edges":len(edge_ids),"used_relations":len(used)}
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument("--contract",type=Path,required=True);a=p.parse_args();r=validate(a.root,a.contract);print(json.dumps(r,indent=2,sort_keys=True));return 0 if r["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
