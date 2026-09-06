#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from verify_result import publish_receipt,rederive_pairs,rederive_timing,validation_matches,verify
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
class Tests(unittest.TestCase):
 def test_verifier_receipt_publication_is_exclusive(self):
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/"receipt";digest=publish_receipt(path,{"verdict":"PASS"});self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest)
   with self.assertRaises(FileExistsError):publish_receipt(path,{"verdict":"PASS"})
 def test_relocated_bound_postrun_roles_reach_main(self):
  import shutil
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);module=root/"experiments/argo_workflow_followup/discoveryworld_ui_parity";module.mkdir(parents=True);names=["bootstrap.py","lifecycle.py","protocol.py","state_projection.py","run.py","environment_manifest.py","verify_result.py","admit_result.py"]
   for name in names:shutil.copy2(HERE/name,module/name)
   approval=json.loads((HERE/"approval-template.json").read_text());approval["engine_repo"]=str(root)
   key_by_name={"bootstrap.py":"bootstrap","lifecycle.py":"lifecycle","protocol.py":"protocol","state_projection.py":"state_projection","run.py":"runner","environment_manifest.py":"environment_manifest_module","verify_result.py":"result_verifier","admit_result.py":"admission_consumer"}
   for name,key in key_by_name.items():approval["bindings"][key]={"path":str((module/name).relative_to(root)),"sha256":hashlib.sha256((module/name).read_bytes()).hexdigest()}
   approval_path=module/"approval-template.json";approval_path.write_text(json.dumps(approval))
   for role,needle in [("verifier",'"verdict": "NOT_PASS"'),("admission",'"verdict": "NOT_ADMITTED"')]:
    command=[sys.executable,"-I","-S","-B",str(module/"bootstrap.py"),role,str(module),"--root",str(root),"--approval",str(approval_path)];done=subprocess.run(command,cwd=root,text=True,capture_output=True,check=False);self.assertEqual(done.returncode,1,done.stdout+done.stderr);self.assertIn(needle,done.stdout);self.assertNotIn("ModuleNotFoundError",done.stderr)
 def test_production_isolated_command_imports_verifier(self):
  command=[sys.executable,"-I","-S","-B",str(HERE/"bootstrap.py"),"verifier",str(HERE),"--root",str(ROOT),"--approval",str(HERE/"approval-template.json")];done=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,check=False);self.assertEqual(done.returncode,1,done.stdout+done.stderr);canonical=Path(json.loads((HERE/"approval-template.json").read_text())["engine_repo"]).resolve()==ROOT.resolve();self.assertIn('"schema_version": "argo-ui-parity-post-run-verification/v1"',done.stdout) if canonical else self.assertIn("POSTRUN_IDENTITY",done.stderr);self.assertNotIn("ModuleNotFoundError",done.stderr)
 def test_missing_artifacts_fail(self):
  with tempfile.TemporaryDirectory() as td:self.assertFalse(verify(Path(td),HERE/"approval-template.json")["passed"])
 def test_pair_rederivation_never_uses_reported_pair_status(self):
  manifest={"mode_pairs":[{"pair_id":"p","official":"a","ui_only":"b"}],"ui_repeat_pairs":[]};vector=["a"*64]*1001;cell={"status":"valid_complete","ui_hashes":vector,"pre_state_hashes":vector,"post_state_hashes":vector};mode,repeat=rederive_pairs(manifest,{"a":cell,"b":copy.deepcopy(cell)});self.assertEqual(mode[0]["status"],"EXACT");changed=copy.deepcopy(cell);changed["ui_hashes"][0]="b"*64;self.assertEqual(rederive_pairs(manifest,{"a":cell,"b":changed})[0][0]["status"],"OBSERVED_MISMATCH");a={**cell,"run":{"duration_seconds":2.0}};b={**cell,"run":{"duration_seconds":1.0}};timing=rederive_timing(manifest["mode_pairs"],{"a":a,"b":b})[0];self.assertEqual((timing["ui_minus_official_seconds"],timing["ui_to_official_ratio"]),(-1.0,0.5))
 def test_revalidated_vectors_must_match_result(self):
  value={"status":"valid_complete","ui_hashes":["a"],"pre_state_hashes":["b"],"post_state_hashes":["c"],"event_sha256":"d","ui_gzip_sha256":"e"};self.assertTrue(validation_matches(value,copy.deepcopy(value)));changed=copy.deepcopy(value);changed["post_state_hashes"]=["x"];self.assertFalse(validation_matches(value,changed));changed=copy.deepcopy(value);changed["errors"]=["x"];self.assertFalse(validation_matches(value,changed))
if __name__=="__main__":unittest.main(verbosity=2)
