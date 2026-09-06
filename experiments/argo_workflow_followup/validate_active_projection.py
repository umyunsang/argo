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
 for pk,hk in [("design","design_sha256"),("proposal","proposal_sha256"),("manifest","manifest_sha256"),("schemas","schemas_sha256"),("adapter_v2","adapter_v2_sha256"),("state_projection","state_projection_sha256"),("lifecycle","lifecycle_sha256"),("protocol","protocol_sha256"),("runner","runner_sha256"),("episode","episode_sha256"),("approval","approval_sha256"),("launcher","launcher_sha256"),("bootstrap","bootstrap_sha256"),("environment_manifest_module","environment_manifest_module_sha256"),("environment_content_manifest","environment_content_manifest_sha256"),("graph_validation_authority","graph_validation_authority_sha256"),("graph_integrity_validator","graph_integrity_validator_sha256"),("graph_integrity_test","graph_integrity_test_sha256")]:
  p=root/cf.get(pk,"")
  if not p.is_file() or sha(p)!=cf.get(hk):errors.append("FRONTIER_BINDING:"+pk)
 try:
  parity_design=json.loads((root/cf["design"]).read_text());readiness=json.loads((root/cf["static_readiness"]).read_text())
  cells=parity_design["selected_design"]["cells"];parity_edge=edges["edge:1272"]
  if type(cells) is not int or cells!=30 or parity_edge.get("scope")!=f"{cells}-cell paired parity design":errors.append("PARITY_CELL_SCOPE")
  bindings=parity_design["candidate_binding"];test_keys=sorted(key for key in bindings if key.endswith("_test"));test_paths=[bindings.get(key) for key in test_keys]
  if len(test_paths)!=len(set(test_paths)) or any(not (root/path).is_file() or sha(root/path)!=bindings.get(key+"_sha256") for key,path in zip(test_keys,test_paths)):errors.append("CANDIDATE_TEST_BINDING")
  declared_counts={int(match.group(1)) for action in nxt.get("next_zero_cost_actions",[]) if (match:=re.search(r"validate (\d+) tests",action))}
  total=readiness.get("total_tests")
  if declared_counts!={total}:errors.append("TEST_COUNT_CONSISTENCY")
  decision=nodes.get("decision:rd_2026_09_06_discoveryworld_ui_parity",{});readiness_edge=edges.get("edge:1297",{})
  if not isinstance(total,int) or f"_{total}_TESTS_" not in decision.get("status","") or readiness_edge.get("scope")!=f"{total}-test static readiness" or str(total) not in nxt.get("status","") or str(total) not in handoff.get("status",""):errors.append("ACTIVE_TEST_STATUS")
  design_nav=nodes.get("artifact:discoveryworld_ui_parity_design",{}).get("status","");handoff_design=next((doc.get("status","") for doc in handoff.get("active_documents",[]) if doc.get("role")=="ui_parity_design"),"");nav_text=" ".join([decision.get("status",""),design_nav,handoff_design,readiness.get("status",""),readiness.get("decision",""),nxt.get("status",""),*nxt.get("next_zero_cost_actions",[])])
  nav_counts={int(value) for value in re.findall(r"(?i)(\d+)(?:-test|_tests?)",nav_text)}
  if nav_counts!={total}:errors.append("ACTIVE_NAV_COUNT")
  proposal_obj=json.loads((root/cf["proposal"]).read_text());approval_obj=json.loads((root/cf["approval"]).read_text());phase_text=" ".join([decision.get("next_action",""),handoff.get("current_allowed_next_action",""),readiness.get("decision",""),nxt.get("status",""),*nxt.get("next_zero_cost_actions",[]),proposal_obj.get("review_status",""),json.dumps(handoff.get("active_documents",[]),sort_keys=True),json.dumps(readiness.get("reviews",{}),sort_keys=True)]).lower()
  if any(term in phase_text for term in ["resolved_in_uncommitted_successor","v4 is uncommitted","v5 is uncommitted","pending_immutable_commit","requires immutable commit","commit exact v4","unreviewed_v4","cascade_pending","clean immutable v5 roots"]):errors.append("STALE_PHASE")
  required_paths=proposal_obj.get("required_preapproval_receipts",{});approval_paths={key:approval_obj.get("bindings",{}).get(key,{}).get("path") for key in ["immutable_validation","method_review","runtime_review","handoff_review"]}
  versions={match.group(1) for path in required_paths.values() if (match:=re.search(r"ui-parity-v(\d+)-",str(path)))}
  if required_paths!=approval_paths or len(versions)!=1 or len(required_paths)!=4:errors.append("RECEIPT_NAMESPACE")
  authority_path=root/cf["graph_validation_authority"]
  if readiness.get("graph_validation_authority",{}).get("sha256")!=sha(authority_path):errors.append("READINESS_GRAPH_AUTH")
 except (KeyError,TypeError,FileNotFoundError,json.JSONDecodeError):errors.append("PARITY_HANDOFF_READ")
 if not set(contract.get("required_prohibited_claims",[])).issubset(set(handoff.get("prohibited_claims",[]))):errors.append("PROHIBITED_CLAIMS")
 if handoff.get("inference_scope",{}).get("candidate_n")!=2 or nxt.get("inference_scope",{}).get("candidate_n")!=2:errors.append("INFERENCE_SCOPE")
 lineage=graph.get("projection_lineage",{})
 if lineage.get("predecessor_snapshot_sha256")!=contract.get("predecessor",{}).get("predecessor_snapshot_sha256") or "successor" not in lineage.get("semantics",""):errors.append("PREDECESSOR")
 if graph.get("evidence_cutoff")!="2026-09-06":errors.append("EVIDENCE_CUTOFF")
 return {"passed":not errors,"errors":errors,"nodes":len(nodes),"edges":len(edges),"active_chain_nodes":len(node_ids),"active_chain_edges":len(edge_ids),"used_relations":len(used)}
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument("--contract",type=Path,required=True);a=p.parse_args();r=validate(a.root,a.contract);print(json.dumps(r,indent=2,sort_keys=True));return 0 if r["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
