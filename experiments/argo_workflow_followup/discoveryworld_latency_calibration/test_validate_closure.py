#!/usr/bin/env python3
from __future__ import annotations
import json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
from validate_closure import validate
C=ROOT/"paper/research/receipts/discoveryworld-latency-calibration-closure-v1.json"
def mut(fn):
 o=json.loads(C.read_text());fn(o);p=Path(tempfile.mkdtemp())/"c.json";p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n");return p
class Tests(unittest.TestCase):
 def test_current(self):
  r=validate(C,ROOT);self.assertTrue(r["passed"],r["errors"])
 def test_auth_bound(self):self.assertFalse(validate(mut(lambda o:o.update({"approved_authorization_sha256":"0"*64})),ROOT)["passed"])
 def test_result_bound(self):self.assertFalse(validate(mut(lambda o:o.update({"result_sha256":"0"*64})),ROOT)["passed"])
 def test_analysis_bound(self):self.assertFalse(validate(mut(lambda o:o.update({"analysis_sha256":"0"*64})),ROOT)["passed"])
 def test_all_640_actions(self):self.assertFalse(validate(mut(lambda o:o["execution"].update({"action_successes":639})),ROOT)["passed"])
 def test_chain_pairs(self):self.assertFalse(validate(mut(lambda o:o["measured"].update({"same_cell_chain_pairs_exact":"5/6"})),ROOT)["passed"])
 def test_prefix_pairs(self):self.assertFalse(validate(mut(lambda o:o["measured"].update({"cross_horizon_prefix_groups_exact":"13/14"})),ROOT)["passed"])
 def test_horizon_not_inflated(self):self.assertFalse(validate(mut(lambda o:o["measured"].update({"maximum_observed_horizon":1000})),ROOT)["passed"])
 def test_long_horizon_not_claimed(self):self.assertFalse(validate(mut(lambda o:o["scope_not_supported"].remove("long-horizon determinism")),ROOT)["passed"])
 def test_authority_consumed_and_model_zero(self):self.assertFalse(validate(mut(lambda o:o["authorization"].update({"remaining_attempts":1})),ROOT)["passed"]);self.assertFalse(validate(mut(lambda o:o.update({"model_calls":1})),ROOT)["passed"])
if __name__=="__main__":unittest.main(verbosity=2)
