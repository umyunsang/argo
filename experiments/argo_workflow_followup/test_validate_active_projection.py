#!/usr/bin/env python3
from __future__ import annotations
import copy,json,re,subprocess,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(HERE))
from validate_active_projection import validate
C=ROOT/"paper/research/context-graph-projection-contract-v1.json"
def workspace_copy():
 import shutil
 td=Path(tempfile.mkdtemp());paths={"paper/context-graph.json","paper/research/ROOT-research-direction.md","paper/research/integrated-research-design-active.md","paper/research/next-experiment-manifest.json","paper/research/active-graph-handoff-manifest.json",str(C.relative_to(ROOT))}
 handoff=json.loads((ROOT/"paper/research/active-graph-handoff-manifest.json").read_text());paths.update(doc["path"] for doc in handoff.get("active_documents",[]))
 nxt=json.loads((ROOT/"paper/research/next-experiment-manifest.json").read_text());paths.update(value for value in nxt.get("current_frontier",{}).values() if isinstance(value,str) and (ROOT/value).is_file())
 design=json.loads((ROOT/nxt["current_frontier"]["design"]).read_text());paths.update(value for key,value in design.get("candidate_binding",{}).items() if key.endswith("_test") and isinstance(value,str) and (ROOT/value).is_file())
 for rel in paths:
  source=ROOT/rel
  if source.is_file():target=td/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
 return td
def workspace_mutate(rel,fn):
 td=workspace_copy();target=td/rel;o=json.loads(target.read_text());fn(o);target.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n");return td
class Tests(unittest.TestCase):
 def test_current(self):
  r=validate(ROOT,C);self.assertTrue(r["passed"],r["errors"])
 def test_cli_default_root(self):
  done=subprocess.run([sys.executable,str(HERE/"validate_active_projection.py"),"--contract",str(C)],text=True,capture_output=True,check=False);self.assertEqual(done.returncode,0,done.stdout+done.stderr)
 def test_noncanonical_chain_node(self):
  td=workspace_mutate("paper/research/active-graph-handoff-manifest.json",lambda o:o["active_chain"]["current_node_ids"].append("missing"));self.assertFalse(validate(td,td/C.relative_to(ROOT))["passed"])
 def test_missing_relation_vocabulary(self):
  td=workspace_mutate("paper/context-graph.json",lambda o:o["edge_vocabulary"].remove("validates"));self.assertFalse(validate(td,td/C.relative_to(ROOT))["passed"])
 def test_stale_next_hash(self):
  td=workspace_mutate("paper/research/active-graph-handoff-manifest.json",lambda o:o["acyclic_binding"].update({"next_sha256":"0"*64}));self.assertFalse(validate(td,td/C.relative_to(ROOT))["passed"])
 def test_historical_edge_cannot_be_active(self):
  td=workspace_mutate("paper/context-graph.json",lambda o:next(e for e in o["edges"] if e["id"]=="edge:889").update({"active":True}));self.assertFalse(validate(td,td/C.relative_to(ROOT))["passed"])
 def test_root_handoff_hash(self):
  td=workspace_mutate("paper/context-graph.json",lambda o:next(n for n in o["nodes"] if n["id"]=="root:research_direction").update({"active_handoff_sha256":"0"*64}));self.assertFalse(validate(td,td/C.relative_to(ROOT))["passed"])
 def test_v4_environment_frontier_hash(self):
  td=workspace_mutate("paper/research/next-experiment-manifest.json",lambda value:value["current_frontier"].update({"environment_content_manifest_sha256":"0"*64}));self.assertIn("FRONTIER_BINDING:environment_content_manifest",validate(td,td/C.relative_to(ROOT))["errors"])
 def test_active_design_hash(self):
  td=workspace_mutate("paper/context-graph.json",lambda o:next(n for n in o["nodes"] if n["id"]=="artifact:active_integrated_research_design").update({"sha256":"0"*64}));self.assertFalse(validate(td,td/C.relative_to(ROOT))["passed"])
 def test_prohibited_claim_projection(self):
  td=workspace_mutate("paper/research/active-graph-handoff-manifest.json",lambda o:o["prohibited_claims"].pop());self.assertFalse(validate(td,td/C.relative_to(ROOT))["passed"])
 def test_mutation_workspace_baseline(self):
  td=workspace_copy();r=validate(td,td/C.relative_to(ROOT));self.assertTrue(r["passed"],r["errors"])
 def test_parity_cell_scope_contradiction(self):
  td=workspace_copy();graph_path=td/"paper/context-graph.json";handoff_path=td/"paper/research/active-graph-handoff-manifest.json";graph=json.loads(graph_path.read_text());handoff=json.loads(handoff_path.read_text());next(e for e in graph["edges"] if e["id"]=="edge:1272")["scope"]="40-cell paired parity design";next(e for e in handoff["active_chain"]["current_edges"] if e["id"]=="edge:1272")["scope"]="40-cell paired parity design";graph_path.write_text(json.dumps(graph,ensure_ascii=False,indent=2)+"\n");handoff_path.write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+"\n");self.assertIn("PARITY_CELL_SCOPE",validate(td,td/C.relative_to(ROOT))["errors"])
 def test_duplicate_or_stale_sentinel_binding(self):
  td=workspace_copy();path=td/"paper/research/discoveryworld-ui-adapter-parity-design.json";design=json.loads(path.read_text());design["candidate_binding"].update({"official_sentinel_test":design["candidate_binding"]["sentinel_test"],"official_sentinel_test_sha256":"0"*64});path.write_text(json.dumps(design,ensure_ascii=False,indent=2)+"\n");self.assertIn("CANDIDATE_TEST_BINDING",validate(td,td/C.relative_to(ROOT))["errors"])
 def test_active_navigation_count_contradiction(self):
  td=workspace_copy();path=td/"paper/context-graph.json";graph=json.loads(path.read_text());next(node for node in graph["nodes"] if node["id"]=="artifact:discoveryworld_ui_parity_design")["status"]="V4_114_TESTS_PASS";path.write_text(json.dumps(graph,ensure_ascii=False,indent=2)+"\n");self.assertIn("ACTIVE_NAV_COUNT",validate(td,td/C.relative_to(ROOT))["errors"])
 def test_receipt_namespace_matches_approval(self):
  td=workspace_copy();path=td/"paper/research/discoveryworld-ui-adapter-parity-proposal.json";proposal=json.loads(path.read_text());proposal["required_preapproval_receipts"]["runtime_review"]="paper/research/reviews/x-v4-runtime-pass.json";path.write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+"\n");self.assertIn("RECEIPT_NAMESPACE",validate(td,td/C.relative_to(ROOT))["errors"])
 def test_readiness_graph_authority_hash(self):
  td=workspace_copy();path=td/"paper/research/receipts/discoveryworld-ui-parity-static-readiness-v1.json";value=json.loads(path.read_text());value["graph_validation_authority"]["sha256"]="0"*64;path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n");self.assertIn("READINESS_GRAPH_AUTH",validate(td,td/C.relative_to(ROOT))["errors"])
 def test_stale_phase_language(self):
  td=workspace_copy();path=td/"paper/research/discoveryworld-ui-adapter-parity-proposal.json";proposal=json.loads(path.read_text());proposal["review_status"]="CASCADE_PENDING";path.write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+"\n");self.assertIn("STALE_PHASE",validate(td,td/C.relative_to(ROOT))["errors"])
 def test_active_decision_test_status_contradiction(self):
  td=workspace_copy();path=td/"paper/context-graph.json";graph=json.loads(path.read_text());next(node for node in graph["nodes"] if node["id"]=="decision:rd_2026_09_06_discoveryworld_ui_parity")["status"]="CONTROLLER_48_TESTS_PASS";path.write_text(json.dumps(graph,ensure_ascii=False,indent=2)+"\n");self.assertIn("ACTIVE_TEST_STATUS",validate(td,td/C.relative_to(ROOT))["errors"])
 def test_next_action_test_count_contradiction(self):
  td=workspace_copy();path=td/"paper/research/next-experiment-manifest.json";nxt=json.loads(path.read_text());nxt["next_zero_cost_actions"]=[re.sub(r"validate \d+ tests","validate 79 tests",action) for action in nxt["next_zero_cost_actions"]];path.write_text(json.dumps(nxt,ensure_ascii=False,indent=2)+"\n");self.assertIn("TEST_COUNT_CONSISTENCY",validate(td,td/C.relative_to(ROOT))["errors"])
if __name__=="__main__":unittest.main(verbosity=2)
