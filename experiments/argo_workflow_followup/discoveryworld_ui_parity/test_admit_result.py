#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from admit_result import admit
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
class Tests(unittest.TestCase):
 def test_missing_is_not_admitted(self):
  with tempfile.TemporaryDirectory() as td:self.assertEqual(admit(Path(td),HERE/"approval-template.json",Path(td)/"missing")["verdict"],"NOT_ADMITTED")
 def test_exact_rederived_verifier_can_admit(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);approval=root/"approval";manifest=root/"manifest";result=root/"result";verification=root/"verification";approval.write_text(json.dumps({"bindings":{"manifest":{"path":str(manifest)}},"execution_root_sha256":"e","authority_root_sha256":"a"}));manifest.write_text(json.dumps({"paths":{"result":str(result),"post_run_verification":str(verification)}}));result.write_text(json.dumps({"execution_root_sha256":"e"}));value={"verdict":"PASS","status":"PASS","execution_root_sha256":"e","result_sha256":"r","ledger_sha256":"l"};verification.write_text(json.dumps(value))
   with patch("admit_result.verify",return_value=value):self.assertEqual(admit(root,approval,verification)["verdict"],"ADMITTED")
 def test_changed_verifier_receipt_is_not_admitted(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);approval=root/"approval";manifest=root/"manifest";result=root/"result";verification=root/"verification";approval.write_text(json.dumps({"bindings":{"manifest":{"path":str(manifest)}},"execution_root_sha256":"e","authority_root_sha256":"a"}));manifest.write_text(json.dumps({"paths":{"result":str(result),"post_run_verification":str(verification)}}));result.write_text(json.dumps({"execution_root_sha256":"e"}));verification.write_text(json.dumps({"verdict":"PASS"}))
   with patch("admit_result.verify",return_value={"verdict":"PASS","status":"PASS","execution_root_sha256":"e"}):self.assertEqual(admit(root,approval,verification)["verdict"],"NOT_ADMITTED")
 def test_production_isolated_command_imports_admitter(self):
  command=[sys.executable,"-I","-S","-B",str(HERE/"bootstrap.py"),"admission",str(HERE),"--root",str(ROOT),"--approval",str(HERE/"approval-template.json")];done=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,check=False);self.assertEqual(done.returncode,1,done.stdout+done.stderr);canonical=Path(json.loads((HERE/"approval-template.json").read_text())["engine_repo"]).resolve()==ROOT.resolve();self.assertIn('"verdict": "NOT_ADMITTED"',done.stdout) if canonical else self.assertIn("POSTRUN_IDENTITY",done.stderr);self.assertNotIn("ModuleNotFoundError",done.stderr)
if __name__=="__main__":unittest.main(verbosity=2)
