#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));from admit_result import decide
class Tests(unittest.TestCase):
 def test_pass_admits_only_narrow_scope(self):
  r={"run_id":"dw-font-registry-qual-20260906-v1","status":"PASS"};v={"run_id":r["run_id"],"verdict":"PASS","controller_status":"PASS"};out=decide(r,v);self.assertEqual(out["verdict"],"ADMITTED");self.assertIn("not UI parity",out["scope"])
 def test_invalid_not_admitted(self):
  r={"run_id":"dw-font-registry-qual-20260906-v1","status":"INVALID"};v={"run_id":r["run_id"],"verdict":"PASS","controller_status":"INVALID"};self.assertEqual(decide(r,v)["verdict"],"NOT_ADMITTED")
 def test_verifier_fail_not_admitted(self):
  r={"run_id":"dw-font-registry-qual-20260906-v1","status":"PASS"};v={"run_id":r["run_id"],"verdict":"FAIL","controller_status":"PASS"};self.assertEqual(decide(r,v)["verdict"],"NOT_ADMITTED")
if __name__=="__main__":unittest.main(verbosity=2)
