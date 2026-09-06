#!/usr/bin/env python3
from __future__ import annotations
import copy,json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(HERE))
from validate_active_projection import validate
C=ROOT/"paper/research/context-graph-projection-contract-v1.json"
def workspace_mutate(rel,fn):
 import shutil
 td=Path(tempfile.mkdtemp());
 for p in ["paper/context-graph.json","paper/research/ROOT-research-direction.md","paper/research/integrated-research-design-active.md","paper/research/next-experiment-manifest.json","paper/research/active-graph-handoff-manifest.json"]:
  d=td/p;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,d)
 shutil.copy2(C,td/C.relative_to(ROOT));target=td/rel;o=json.loads(target.read_text());fn(o);target.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n");return td
class Tests(unittest.TestCase):
 def test_current(self):
  r=validate(ROOT,C);self.assertTrue(r["passed"],r["errors"])
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
 def test_active_design_hash(self):
  td=workspace_mutate("paper/context-graph.json",lambda o:next(n for n in o["nodes"] if n["id"]=="artifact:active_integrated_research_design").update({"sha256":"0"*64}));self.assertFalse(validate(td,td/C.relative_to(ROOT))["passed"])
 def test_prohibited_claim_projection(self):
  td=workspace_mutate("paper/research/active-graph-handoff-manifest.json",lambda o:o["prohibited_claims"].pop());self.assertFalse(validate(td,td/C.relative_to(ROOT))["passed"])
if __name__=="__main__":unittest.main(verbosity=2)
