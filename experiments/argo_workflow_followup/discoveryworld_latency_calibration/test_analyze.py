#!/usr/bin/env python3
from __future__ import annotations
import copy,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
from analyze import analyze
RESULT=json.loads((ROOT/"paper/research/receipts/discoveryworld-latency-calibration-result-v1.json").read_text())
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a=analyze(RESULT)
 def test_current_passes(self):self.assertTrue(self.a["passed"],self.a["errors"])
 def test_all_cells_and_steps(self):self.assertEqual((self.a["measured"]["episodes_completed"],self.a["measured"]["completed_steps"]),(12,640))
 def test_actions_and_ticks(self):self.assertEqual((self.a["measured"]["action_successes"],self.a["measured"]["tick_successes"]),(640,640))
 def test_repeat_chains_exact(self):self.assertEqual(self.a["measured"]["same_cell_chain_pairs_exact"],"6/6")
 def test_prefix_groups_exact(self):self.assertEqual(self.a["measured"]["cross_horizon_prefix_groups_exact"],"14/14")
 def test_hidden_and_vision_absent(self):self.assertEqual((self.a["measured"]["hidden_key_episodes"],self.a["measured"]["vision_accessed_episodes"]),(0,0))
 def test_observed_horizon_is_only_100(self):self.assertEqual(self.a["measured"]["maximum_observed_horizon"],100);self.assertFalse(self.a["long_horizon_certified"])
 def test_median_projection_exceeds_old_timeout(self):self.assertTrue(all(x["median_projected_1000_seconds"]>120 for x in self.a["latency_by_scenario"].values()))
 def test_chain_mutation_fails(self):
  x=copy.deepcopy(RESULT);x["episodes"][1]["complete"]["chain_sha256"]="0"*64;self.assertFalse(analyze(x)["passed"])
 def test_seed_rows_remain_nested(self):self.assertEqual(self.a["inference_units"],2);self.assertNotEqual(self.a["inference_units"],12)
if __name__=="__main__":unittest.main(verbosity=2)
