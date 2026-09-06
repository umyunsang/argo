#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import launcher
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
class Tests(unittest.TestCase):
 def test_seal_uses_retained_exact_bytes(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);bindings={};approval_bytes=b'{"status":"APPROVED"}'
   for key,name in launcher.FILES.items():path=root/name;path.write_bytes(key.encode());bindings[key]={"path":name,"sha256":hashlib.sha256(key.encode()).hexdigest()}
   bindings["launcher"]={"path":"launcher.py","sha256":hashlib.sha256(Path(launcher.__file__).read_bytes()).hexdigest()};approval={"bindings":bindings};dest=root/"seal";digest=launcher.seal_controller(approval,approval_bytes,root/"approval.json",root,dest);self.assertEqual(hashlib.sha256((dest/"seal.json").read_bytes()).hexdigest(),digest);self.assertEqual((dest/"run.py").read_bytes(),b"runner")
 def test_binding_drift_fails_without_exec(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);bindings={}
   for key,name in launcher.FILES.items():path=root/name;path.write_bytes(key.encode());bindings[key]={"path":name,"sha256":"0"*64}
   bindings["launcher"]={"path":"launcher.py","sha256":hashlib.sha256(Path(launcher.__file__).read_bytes()).hexdigest()}
   with self.assertRaises(RuntimeError):launcher.seal_controller({"bindings":bindings},b"{}",root/"approval",root,root/"seal")
 def test_actual_unapproved_controller_imports_only_from_seal(self):
  approval_path=HERE/"approval-template.json";approval_bytes=approval_path.read_bytes();approval=json.loads(approval_bytes)
  with tempfile.TemporaryDirectory() as td:
   destination=Path(td)/"seal";digest=launcher.seal_controller(approval,approval_bytes,approval_path,ROOT,destination);env=dict(os.environ,ARGO_UI_PARITY_CONTROLLER_SEAL=str(destination),ARGO_UI_PARITY_CONTROLLER_SEAL_SHA256=digest);done=subprocess.run([sys.executable,"-I","-S","-B",str(destination/"bootstrap.py"),"controller",str(destination),"--approval",str(approval_path),"--out",str(Path(td)/"out")],cwd=ROOT,env=env,text=True,capture_output=True,check=False);self.assertEqual(done.returncode,2,done.stdout+done.stderr);self.assertIn("BLOCKED_BEFORE_CONSUMPTION",done.stdout)
 def test_unapproved_main_does_not_create_seal_or_exec(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);approval=root/"approval";approval.write_text(json.dumps({"engine_repo":str(root),"status":"AWAITING_USER_APPROVAL","approved_by":None}))
   with patch("launcher.Path.cwd",return_value=root),patch("launcher.tempfile.mkdtemp") as make,patch("launcher.os.execve") as execute,patch("launcher.argparse.ArgumentParser.parse_args",return_value=type("A",(),{"approval":approval,"out":root/"out"})()):self.assertEqual(launcher.main(),2);make.assert_not_called();execute.assert_not_called()
if __name__=="__main__":unittest.main(verbosity=2)
