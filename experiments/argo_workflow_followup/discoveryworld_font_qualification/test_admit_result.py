#!/usr/bin/env python3
import hashlib,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));from admit_result import VERIFICATION_FIELDS,decide;from run import canonical
RUN="dw-font-registry-qual-20260906-v1";H="a"*64
def values(status="PASS"):
 result={"run_id":RUN,"status":status};rb=canonical(result)+b"\n";verification={"schema_version":"argo-font-qualification-verification/v1","run_id":RUN,"verdict":"PASS","controller_status":status,"errors":[],"result_sha256":hashlib.sha256(rb).hexdigest(),"ledger_sha256":H,"marker_sha256":H,"cells":2,"execution_root_sha256":"e","authority_root_sha256":"a"};vb=canonical(verification)+b"\n";return result,verification,rb,vb
def call(status="PASS",gate=True):
 r,v,rb,vb=values(status);return decide(r,v,rb,vb,{"approved":gate},"e","a")
class Tests(unittest.TestCase):
 def test_pass_admits_only_narrow_scope(self):out=call();self.assertEqual(out["verdict"],"ADMITTED");self.assertIn("not UI parity",out["scope"])
 def test_invalid_not_admitted(self):self.assertEqual(call("INVALID")["verdict"],"NOT_ADMITTED")
 def test_approval_must_be_current(self):self.assertIn("APPROVAL_NOT_VALID",call(gate=False)["errors"])
 def test_result_drift_fails(self):
  r,v,rb,vb=values();rb=canonical({**r,"changed":True})+b"\n";out=decide(r,v,rb,vb,{"approved":True},"e","a");self.assertIn("NONCANONICAL_BYTES",out["errors"]);self.assertIn("RESULT_DRIFT",out["errors"])
 def test_verification_schema_and_roots_fail_closed(self):
  r,v,rb,vb=values();v.pop("ledger_sha256");vb=canonical(v)+b"\n";out=decide(r,v,rb,vb,{"approved":True},"e","a");self.assertIn("VERIFICATION_SCHEMA",out["errors"])
if __name__=="__main__":unittest.main(verbosity=2)
