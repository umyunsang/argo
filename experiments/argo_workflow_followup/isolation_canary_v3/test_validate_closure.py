#!/usr/bin/env python3
from __future__ import annotations
import json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
from validate_closure import validate
CLOSURE=ROOT/"paper/research/receipts/isolation-canary-v3-closure-v1.json"
def mutate(fn):
 obj=json.loads(CLOSURE.read_text());fn(obj);path=Path(tempfile.mkdtemp())/"closure.json";path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n");return path
class Tests(unittest.TestCase):
 def test_current_passes(self):
  result=validate(CLOSURE,ROOT);self.assertTrue(result["passed"],result["errors"])
 def test_all_nine_checks_required(self):
  path=mutate(lambda o:o["checks"].update({"external_network_blocked":False}));self.assertFalse(validate(path,ROOT)["passed"])
 def test_approved_authorization_bound(self):
  path=mutate(lambda o:o.update({"approved_authorization_sha256":"0"*64}));self.assertFalse(validate(path,ROOT)["passed"])
 def test_authority_consumed_no_retry(self):
  path=mutate(lambda o:o["authorization"].update({"remaining_attempts":1}));self.assertFalse(validate(path,ROOT)["passed"])
 def test_writable_bind_must_remain_zero(self):
  path=mutate(lambda o:o["execution"].update({"writable_host_bind_mounts":1}));self.assertFalse(validate(path,ROOT)["passed"])
 def test_integrated_runner_cannot_be_claimed(self):
  path=mutate(lambda o:o["scope_not_supported"].remove("integrated task runner"));self.assertFalse(validate(path,ROOT)["passed"])
 def test_result_hash_bound(self):
  path=mutate(lambda o:o.update({"result_sha256":"0"*64}));self.assertFalse(validate(path,ROOT)["passed"])
 def test_model_calls_zero(self):
  path=mutate(lambda o:o.update({"model_calls":1}));self.assertFalse(validate(path,ROOT)["passed"])
if __name__=="__main__":unittest.main(verbosity=2)
