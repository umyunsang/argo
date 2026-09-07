"""Regular-file deployment uses fabricated code and mocked exec only."""
from __future__ import annotations
from dataclasses import replace
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_process import capture_interpreter_identity
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.deployment_assets import DeploymentError, LIMITS, NamespaceMember, materialize_namespace, write_module_bootstrap
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.source_closure import verify_tree

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding

PREFIX="experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/"
KERNEL=Path("/Users/um-yunsang/.prime/agent/kernel-venv/bin/python")
MODULE="experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_gate"

def binding(path):
    data=path.read_bytes();return FileBinding(path,hashlib.sha256(data).hexdigest(),len(data),path.stat().st_mtime_ns)

class DeploymentAssetsTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="hp-module-assets-");self.root=Path(self.temp.name).resolve()
        self.root.chmod(0o700)
        self.source=self.root/"source.py";self.source.write_bytes(b'VALUE = "synthetic"\n')
        self.member=NamespaceMember(PREFIX+"phase_gate.py",binding(self.source))
        self.namespace=self.root/"namespace"
        self.config=self.root/"gate.json";self.config.write_bytes(b'{}')
        self.interpreter=capture_interpreter_identity(KERNEL,KERNEL.parent.parent/"pyvenv.cfg")
    def tearDown(self):self.temp.cleanup()

    def test_materializes_exact_regular_namespace_and_never_overwrites(self):
        tree=materialize_namespace(self.namespace,(self.member,))
        self.assertEqual((self.namespace/self.member.relative_path).read_bytes(),self.source.read_bytes())
        inits=list(self.namespace.rglob("__init__.py"));self.assertEqual(len(inits),4)
        self.assertTrue(all(p.read_bytes()==b"" for p in inits));self.assertEqual(tree.file_count,5)
        self.assertFalse(list(self.namespace.rglob("*.pyc")))
        with self.assertRaises(DeploymentError):materialize_namespace(self.namespace,(self.member,))

    def test_rejects_bad_source_identity_and_noncode_namespace_members(self):
        self.source.write_bytes(b'VALUE = "different"\n')
        with self.assertRaises(DeploymentError):materialize_namespace(self.namespace,(self.member,))
        for index,name in enumerate(["../escape.py",PREFIX+"auth.json",PREFIX+"test_phase_gate.py","other/phase_gate.py"]):
            with self.subTest(name=name),self.assertRaises(DeploymentError):
                materialize_namespace(self.root/("denied"+str(index)),(NamespaceMember(name,binding(self.source)),))
        with self.assertRaises(DeploymentError):materialize_namespace(self.root/"duplicate",(self.member,self.member))

    def test_module_bootstrap_uses_fixed_exec_and_environment_not_inherited_arguments(self):
        tree=materialize_namespace(self.namespace,(self.member,))
        output=self.root/"gate-entry"
        receipt=write_module_bootstrap(output,tree,self.interpreter,MODULE,binding(self.config))
        data=output.read_bytes();self.assertEqual(receipt.sha256,hashlib.sha256(data).hexdigest())
        self.assertEqual(output.stat().st_mode&0o777,0o700)
        def replaced_process(*_):raise SystemExit(0)
        with patch("sys.argv",[str(output)]),patch("os.chdir") as chdir,patch("os.fchdir") as fchdir,patch("os.execve",side_effect=replaced_process) as execute,self.assertRaises(SystemExit) as stopped:
            exec(compile(data,str(output),"exec"),{"__name__":"__main__"})
        self.assertEqual(stopped.exception.code,0)
        chdir.assert_not_called();fchdir.assert_called_once()
        with self.assertRaises(OSError):os.fstat(fchdir.call_args.args[0])
        args=execute.call_args.args
        self.assertEqual(args[0],str(KERNEL))
        self.assertEqual(args[1],[str(KERNEL),"-B","-m",MODULE,"--config",str(self.config),"--config-sha256",binding(self.config).sha256])
        self.assertEqual(args[2],{"LANG":"C.UTF-8","LC_ALL":"C.UTF-8","PATH":"/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin","TZ":"UTC"})
        captured=io.StringIO()
        with patch("sys.argv",[str(output),"--extra"]),patch("os.chdir"),patch("os.fchdir"),patch("os.execve") as execute,redirect_stdout(captured),self.assertRaises(SystemExit) as stopped:
            exec(compile(data,str(output),"exec"),{"__name__":"__main__"})
        execute.assert_not_called();self.assertEqual(stopped.exception.code,0)
        self.assertEqual(captured.getvalue(),"STOP_PROTOCOL_INVALID\n")
        with self.assertRaises(DeploymentError):write_module_bootstrap(output,tree,self.interpreter,MODULE,binding(self.config))

    def test_changed_tree_interpreter_or_module_does_not_publish_bootstrap(self):
        tree=materialize_namespace(self.namespace,(self.member,))
        for index,module in enumerate([MODULE+";touch", "untrusted.module"]):
            with self.assertRaises(DeploymentError):write_module_bootstrap(self.root/("bad"+str(index)),tree,self.interpreter,module,binding(self.config))
        wrong=replace(self.interpreter,invocation_path="/usr/bin/python3")
        with self.assertRaises(DeploymentError):write_module_bootstrap(self.root/"wrong-kernel",tree,wrong,MODULE,binding(self.config))
        (self.namespace/self.member.relative_path).write_bytes(b"VALUE=123\n")
        with self.assertRaises(DeploymentError):write_module_bootstrap(self.root/"changed",tree,self.interpreter,MODULE,binding(self.config))
        self.assertFalse((self.root/"changed").exists())

    def test_partial_copy_is_retained_and_cannot_be_retried(self):
        native_write=os.write
        count=0
        def broken(fd,data):
            nonlocal count
            count+=1
            if count>1:raise OSError("synthetic")
            return native_write(fd,data[:3])
        with patch("os.write",side_effect=broken),self.assertRaises(DeploymentError):
            materialize_namespace(self.namespace,(self.member,))
        self.assertTrue(self.namespace.exists())
        with self.assertRaises(DeploymentError):materialize_namespace(self.namespace,(self.member,))

    def test_bootstrap_and_config_must_stay_outside_sealed_namespace(self):
        tree=materialize_namespace(self.namespace,(self.member,))
        before={str(path.relative_to(self.namespace)):path.read_bytes() for path in self.namespace.rglob("*") if path.is_file()}
        with self.assertRaises(DeploymentError):
            write_module_bootstrap(self.namespace/"gate-entry",tree,self.interpreter,MODULE,binding(self.config))
        self.assertFalse((self.namespace/"gate-entry").exists())
        inside_config=self.namespace/self.member.relative_path
        outside_output=self.root/"outside-entry"
        with self.assertRaises(DeploymentError):
            write_module_bootstrap(outside_output,tree,self.interpreter,MODULE,binding(inside_config))
        self.assertFalse(outside_output.exists())
        after={str(path.relative_to(self.namespace)):path.read_bytes() for path in self.namespace.rglob("*") if path.is_file()}
        self.assertEqual(after,before)
        self.assertEqual(verify_tree(self.namespace,tree,LIMITS),tree)

    def test_inside_namespace_config_does_not_publish_or_change_namespace(self):
        tree=materialize_namespace(self.namespace,(self.member,))
        inside=self.namespace/self.member.relative_path
        with self.assertRaises(DeploymentError):
            write_module_bootstrap(self.root/"entry",tree,self.interpreter,MODULE,binding(inside))
        self.assertFalse((self.root/"entry").exists())

    def test_generated_gate_refuses_replaced_directory_with_safe_stop(self):
        tree=materialize_namespace(self.namespace,(self.member,))
        output=self.root/"gate-entry"
        write_module_bootstrap(output,tree,self.interpreter,MODULE,binding(self.config))
        source=output.read_bytes()
        self.namespace.rename(self.root/"old-namespace");self.namespace.mkdir(mode=0o700)
        captured=io.StringIO()
        with patch("sys.argv",[str(output)]),patch("os.chdir"),patch("os.fchdir"),patch("os.execve") as execute,redirect_stdout(captured),self.assertRaises(SystemExit) as stopped:
            exec(compile(source,str(output),"exec"),{"__name__":"__main__"})
        self.assertEqual(stopped.exception.code,0)
        self.assertEqual(captured.getvalue(),"STOP_PROTOCOL_INVALID\n")
        execute.assert_not_called()

    def test_generated_gate_maps_preexec_failures_without_private_text(self):
        tree=materialize_namespace(self.namespace,(self.member,))
        output=self.root/"gate-entry"
        write_module_bootstrap(output,tree,self.interpreter,MODULE,binding(self.config))
        source=output.read_bytes()
        for action in ("os.open","os.fchdir","os.execve"):
            captured=io.StringIO()
            with self.subTest(action=action),patch("sys.argv",[str(output)]),patch("os.chdir"),patch("os.fchdir"),patch("os.execve"),patch(action,side_effect=OSError("private synthetic detail")),redirect_stdout(captured),self.assertRaises(SystemExit) as stopped:
                exec(compile(source,str(output),"exec"),{"__name__":"__main__"})
            self.assertEqual(stopped.exception.code,0)
            self.assertEqual(captured.getvalue(),"STOP_PROTOCOL_INVALID\n")

    def test_generated_bridge_failure_is_fixed_json_and_nonzero(self):
        bridge_member=NamespaceMember(PREFIX+"bridge.py",binding(self.source))
        tree=materialize_namespace(self.namespace,(self.member,bridge_member))
        output=self.root/"bridge-entry"
        module=MODULE.rsplit(".",1)[0]+".bridge"
        write_module_bootstrap(output,tree,self.interpreter,module,binding(self.config))
        captured=io.StringIO()
        with patch("sys.argv",[str(output)]),patch("os.chdir"),patch("os.fchdir"),patch("os.execve",side_effect=OSError("private synthetic detail")),redirect_stdout(captured),self.assertRaises(SystemExit) as stopped:
            exec(compile(output.read_bytes(),str(output),"exec"),{"__name__":"__main__"})
        self.assertEqual(stopped.exception.code,1)
        self.assertEqual(json.loads(captured.getvalue()),{"error":"INTERNAL_ERROR","ok":False})
        self.assertNotIn("private synthetic detail",captured.getvalue())

    def test_namespace_admits_only_the_new_shared_validator_not_test_helpers(self):
        member=NamespaceMember(PREFIX+"controller_deployment.py",binding(self.source))
        tree=materialize_namespace(self.namespace,(member,))
        self.assertEqual((self.namespace/member.relative_path).read_bytes(),self.source.read_bytes())
        self.assertEqual(tree.file_count,5)
        for name in ("test_bridge.py","a2_combination_driver.py","controller_deployment_extra.py"):
            with self.subTest(name=name),self.assertRaises(DeploymentError):
                materialize_namespace(self.root/("denied-"+name),(NamespaceMember(PREFIX+name,binding(self.source)),))

if __name__=="__main__":unittest.main(verbosity=2)
