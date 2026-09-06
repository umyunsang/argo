#!/usr/bin/env python3
from __future__ import annotations
import copy,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(HERE))
from validate_graph_relations import validate
GRAPH=json.loads((ROOT/"paper/context-graph.json").read_text())
class Tests(unittest.TestCase):
 def test_current(self):
  r=validate(GRAPH);self.assertTrue(r["passed"],r["errors"])
 def test_missing_used_relation(self):
  x=copy.deepcopy(GRAPH);x["edge_vocabulary"].remove("validates");self.assertFalse(validate(x)["passed"])
 def test_unknown_edge_relation(self):
  x=copy.deepcopy(GRAPH);x["edges"][0]["relation"]="invented";self.assertFalse(validate(x)["passed"])
 def test_duplicate_vocabulary(self):
  x=copy.deepcopy(GRAPH);x["edge_vocabulary"].append(x["edge_vocabulary"][0]);self.assertFalse(validate(x)["passed"])
 def test_predecessor_identity_required(self):
  x=copy.deepcopy(GRAPH);x["projection_lineage"]["predecessor_snapshot_sha256"]="0";self.assertFalse(validate(x)["passed"])
if __name__=="__main__":unittest.main(verbosity=2)
