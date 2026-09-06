#!/usr/bin/env python3
from __future__ import annotations
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];AUTH=ROOT/"paper/research/context-graph-validation-authority-v2.json"
class Tests(unittest.TestCase):
 def test_supersession_is_graph_only(self):
  value=json.loads(AUTH.read_text());self.assertEqual(value["decision"],"SUPERSEDE_LEGACY_EXACT_SNAPSHOT_GATE_FOR_ACTIVE_CONTEXT_GRAPH_ONLY");self.assertIn("does not waive",value["authority_limit"]);self.assertEqual((value["legacy_gate"]["frozen_expected_nodes"],value["legacy_gate"]["frozen_expected_edges"]),(705,1260))
 def test_three_current_gates_exist(self):
  value=json.loads(AUTH.read_text());self.assertEqual(len(value["current_active_graph_gates"]),3)
  for gate in value["current_active_graph_gates"]:self.assertTrue((ROOT/gate["path"]).is_file());self.assertTrue((ROOT/gate["test"]).is_file())
if __name__=="__main__":unittest.main(verbosity=2)
