#!/usr/bin/env python3
from __future__ import annotations
import json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
from validate_closure import validate
CLOSURE=ROOT/"paper/research/receipts/discoveryworld-long-horizon-closure-v1.json"
def mutate(fn):
 o=json.loads(CLOSURE.read_text());fn(o);p=Path(tempfile.mkdtemp())/"c.json";p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n");return p
class Tests(unittest.TestCase):
 def test_current_passes(self):
  r=validate(CLOSURE,ROOT);self.assertTrue(r["passed"],r["errors"])
 def test_approval_bound(self):
  p=mutate(lambda o:o.update({"approved_authorization_sha256":"0"*64}));self.assertFalse(validate(p,ROOT)["passed"])
 def test_result_bound(self):
  p=mutate(lambda o:o.update({"result_sha256":"0"*64}));self.assertFalse(validate(p,ROOT)["passed"])
 def test_all_twenty_timeouts_remain(self):
  p=mutate(lambda o:o["execution"].update({"episode_subprocesses_timed_out":19}));self.assertFalse(validate(p,ROOT)["passed"])
 def test_authority_consumed(self):
  p=mutate(lambda o:o["authorization"].update({"remaining_attempts":1}));self.assertFalse(validate(p,ROOT)["passed"])
 def test_zero_sums_are_not_observed_zero_steps(self):
  p=mutate(lambda o:o["observed_semantics"].update({"completed_steps":0}));self.assertFalse(validate(p,ROOT)["passed"])
 def test_no_determinism_judgment(self):
  p=mutate(lambda o:o["not_claimed"].remove("DiscoveryWorld nondeterminism"));self.assertFalse(validate(p,ROOT)["passed"])
 def test_no_posthoc_retry(self):
  p=mutate(lambda o:o["next_requirements"].remove("do not shorten, exclude, or retry these confirmatory-shaped episodes post hoc"));self.assertFalse(validate(p,ROOT)["passed"])
 def test_model_calls_zero(self):
  p=mutate(lambda o:o.update({"model_calls":1}));self.assertFalse(validate(p,ROOT)["passed"])
if __name__=="__main__":unittest.main(verbosity=2)
