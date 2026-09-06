#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import launcher
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def approved_value():
 value=json.loads((HERE/"approval-template.json").read_text());self_sha=hashlib.sha256(Path(launcher.__file__).read_bytes()).hexdigest()
 for key,spec in launcher.PINNED.items():value.setdefault("bindings",{})[key]={"path":spec["path"],"sha256":spec["sha256"]}
 value["bindings"]["launcher"]={"path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/launcher.py","sha256":self_sha};value.update({"engine_repo":str(ROOT),"controller_interpreter":launcher.CONTROLLER_INTERPRETER,"controller_interpreter_sha256":launcher.CONTROLLER_INTERPRETER_SHA256,"execution_root_sha256":launcher.execution_root(value,self_sha),"status":"APPROVED","approved_by":"user","approved_at":"2026-09-06T00:00:00+09:00"});required=f'I approve exactly one local zero-model DiscoveryWorld UI-parity run {value.get("run_id")} for execution root {value["execution_root_sha256"]} and design SHA-256 {value["bindings"]["design"]["sha256"]}, limited to {value.get("cells")} cells, {value.get("steps_per_cell")} transitions per cell, a {value.get("controller_hard_deadline_seconds")}-second launch/execution deadline, zero model calls, zero Docker calls, and USD 0 API spend. No retry or resume.';value["required_approval_text"]=required;value["user_approval_message"]=required;value["user_approval_message_sha256"]=hashlib.sha256(required.encode()).hexdigest();return value
class Tests(unittest.TestCase):
 def test_seal_uses_pinned_paths_not_approval_paths(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"source.py";source.write_bytes(b"pinned");evil=root/"evil.py";evil.write_bytes(b"evil");pinned={"runner":{"path":"source.py","sha256":hashlib.sha256(b"pinned").hexdigest(),"name":"run.py"}};approval={"bindings":{"runner":{"path":str(evil),"sha256":hashlib.sha256(b"evil").hexdigest()}}};destination=root/"seal";launcher.seal_controller(approval,b"{}",root/"approval",root,destination,pinned=pinned);self.assertEqual((destination/"run.py").read_bytes(),b"pinned")
 def test_pinned_drift_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"source";source.write_bytes(b"changed");pinned={"runner":{"path":"source","sha256":"0"*64,"name":"run.py"}}
   with self.assertRaises(RuntimeError):launcher.seal_controller({},b"{}",root/"approval",root,root/"seal",pinned=pinned)
 def test_actual_unapproved_controller_imports_only_from_seal(self):
  approval_path=HERE/"approval-template.json";approval_bytes=approval_path.read_bytes();approval=json.loads(approval_bytes)
  with tempfile.TemporaryDirectory() as td:
   destination=Path(td)/"seal";digest=launcher.seal_controller(approval,approval_bytes,approval_path,ROOT,destination);env=dict(os.environ,ARGO_UI_PARITY_CONTROLLER_SEAL=str(destination),ARGO_UI_PARITY_CONTROLLER_SEAL_SHA256=digest);done=subprocess.run([launcher.CONTROLLER_INTERPRETER,"-I","-S","-B",str(destination/"bootstrap.py"),"controller",str(destination),"--approval",str(approval_path),"--out",str(Path(td)/"out")],cwd=ROOT,env=env,text=True,capture_output=True,check=False);self.assertEqual(done.returncode,2,done.stdout+done.stderr);self.assertIn("BLOCKED_BEFORE_CONSUMPTION",done.stdout)
 def test_unapproved_main_does_not_create_seal_or_exec(self):
  args=type("A",(),{"approval":HERE/"approval-template.json","out":ROOT/"out"})()
  with patch("launcher.argparse.ArgumentParser.parse_args",return_value=args),patch("launcher.tempfile.mkdtemp") as make,patch("launcher.os.execve") as execute:self.assertEqual(launcher.main(),2);make.assert_not_called();execute.assert_not_called()
 def test_canonical_approved_value_passes(self):
  value=approved_value();self_sha=hashlib.sha256(Path(launcher.__file__).read_bytes()).hexdigest();self.assertTrue(launcher.validate_canonical_approval(value,HERE/"approval-template.json",ROOT,self_sha))
 def test_approved_main_seals_nonexistent_child_and_reaches_exec(self):
  approval_path=HERE/"approval-template.json"
  with tempfile.TemporaryDirectory() as td:
   parent=Path(td)/"parent";parent.mkdir();args=type("A",(),{"approval":approval_path,"out":Path(td)/"out"})()
   with patch("launcher.argparse.ArgumentParser.parse_args",return_value=args),patch("launcher.Path.cwd",return_value=ROOT),patch("launcher.validate_canonical_approval",return_value=True),patch("launcher.tempfile.mkdtemp",return_value=str(parent)),patch("launcher.os.execve") as execute:launcher.main();execute.assert_called_once();self.assertTrue((parent/"controller/seal.json").is_file())
if __name__=="__main__":unittest.main(verbosity=2)
