"""Exact A2 configuration producers; no native controller or auth contents."""
from __future__ import annotations
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_deployment import DeploymentConfigError, FrontendDeploymentInput, _revalidate_frontend_deployment, write_extension_binding, write_frontend_deployment, write_process_config
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_process import capture_interpreter_identity, capture_path_identity
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding

KERNEL=Path("/Users/um-yunsang/.prime/agent/kernel-venv/bin/python")
PRIME=Path("/opt/homebrew/lib/node_modules/prime-agent/dist/index.js")
NODE=Path("/opt/homebrew/bin/node").resolve()
HERE=Path(__file__).parent

def bind(path):
    data=path.read_bytes();return FileBinding(path,hashlib.sha256(data).hexdigest(),len(data),path.stat().st_mtime_ns)

class ControllerDeploymentTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="hp-controller-deployment-");self.root=Path(self.temp.name).resolve()
        self.root.chmod(0o700)
        self.assets=self.root/"assets";self.assets.mkdir(mode=0o700)
        self.artifact=self.root/"artifacts";self.artifact.mkdir(mode=0o700)
        self.directories={"artifact_root":self.artifact,"cwd":self.root/"public","profile":self.root/"profile",
                          "session_dir":self.artifact/"session","temporary_dir":self.artifact/"tmp"}
        for key,path in self.directories.items():
            if key!="artifact_root":path.mkdir(mode=0o700)
        def asset(name,data):
            path=self.assets/name;path.write_bytes(data);return bind(path)
        self.extension=asset("controller-extension.ts",b"export default function synthetic() {}\n")
        self.bootstrap=asset("bridge-entry",b"#!/usr/bin/false\n");self.bootstrap.path.chmod(0o700);self.bootstrap=bind(self.bootstrap.path)
        self.gate=asset("gate-entry",b"#!/usr/bin/false\n");self.gate.path.chmod(0o700);self.gate=bind(self.gate.path)
        settings=self.directories["profile"]/"settings.json"
        settings.write_text(json.dumps({"retry":{"enabled":False,"provider":{"timeoutMs":120000,"maxRetries":0}}}))
        self.raw_assets={"prime_entry":bind(PRIME),"prime_closure_manifest":asset("prime-tree.json",b"{}"),
            "controller_main":asset("controller-main.ts",b'export const synthetic = true;\n'),
            "frontend_closure_manifest":asset("frontend-tree.json",b"{}"),"extension":self.extension,
            "settings":bind(settings),"system_prompt":asset("system.md",b"Synthetic fixed system."),
            "task_prompt":asset("task.md",b"Synthetic fixed task."),"autonomous_gate":self.gate,"node_executable":bind(NODE)}
        self.interpreter=capture_interpreter_identity(KERNEL,KERNEL.parent.parent/"pyvenv.cfg")
    def tearDown(self):self.temp.cleanup()
    def spec(self):
        binding=write_extension_binding(self.extension,self.bootstrap)
        manifest=bind(self.extension.path.with_name("controller-extension.closure.json"))
        return FrontendDeploymentInput({**self.raw_assets,"binding":binding,"frontend_closure_manifest":manifest},self.interpreter,self.directories,"dev")
    def test_extension_binding_is_fixed_bounded_and_no_overwrite(self):
        binding=write_extension_binding(self.extension,self.bootstrap)
        self.assertEqual(binding.path,self.extension.path.with_name("controller-extension.binding.json"))
        obj=json.loads(binding.path.read_bytes())
        self.assertEqual(obj["bridge"],{"command":str(self.bootstrap.path),"argv":[]})
        self.assertEqual(obj["expectedExtensionSha256"],self.extension.sha256)
        self.assertEqual(obj["limits"]["maxRows"],292)
        with self.assertRaises(DeploymentConfigError):write_extension_binding(self.extension,self.bootstrap)
    def test_frontend_and_process_bind_exact_eight_env_and_native_argv_assets(self):
        spec=self.spec();deployment=self.artifact/"deployment.json"
        receipt=write_frontend_deployment(deployment,spec)
        obj=json.loads(deployment.read_bytes())
        self.assertEqual(len(obj["environment"]["exact"]),8);self.assertNotIn("HOME",obj["environment"]["exact"])
        self.assertEqual(obj["assets"]["kernel_interpreter"]["invocation_path"],str(KERNEL))
        self.assertEqual(obj["runtime"]["tools"],['read_solution','write_solution','request_R1_run','read_public_result','read_dev_result','lock_final_artifact'])
        process_path=self.root/"process.json"
        result=write_process_config(process_path,receipt,bind(HERE/"process_exec.py"),time.monotonic_ns())
        process=json.loads(process_path.read_bytes())
        self.assertFalse(process["synthetic_test_context"])
        self.assertEqual(process["artifact_root_identity"]["size"],self.artifact.stat().st_size)
        self.assertEqual(process["child_environment"],obj["environment"]["exact"])
        self.assertEqual(process["caps"]["rss_trigger_bytes"],2147483648)
        self.assertEqual(process["caps"]["model_tokens_between_turns"],120000)
        self.assertEqual(result.sha256,hashlib.sha256(process_path.read_bytes()).hexdigest())
        with self.assertRaises(DeploymentConfigError):write_frontend_deployment(deployment,spec)
    def test_unknown_assets_modified_settings_and_stale_native_dirs_are_denied(self):
        spec=self.spec()
        wrong=replace(spec,assets={**spec.assets,"auth":spec.assets["settings"]})
        with self.assertRaises(DeploymentConfigError):write_frontend_deployment(self.artifact/"wrong.json",wrong)
        (self.directories["session_dir"]/"stale").write_bytes(b"x")
        with self.assertRaises(DeploymentConfigError):write_frontend_deployment(self.artifact/"stale.json",spec)
        self.assertFalse((self.artifact/"stale.json").exists())
    def test_bad_settings_and_process_config_inside_artifact_are_rejected(self):
        spec=self.spec();settings=self.directories["profile"]/"settings.json"
        settings.write_text('{"retry":{"enabled":true,"provider":{"timeoutMs":120000,"maxRetries":0}}}')
        wrong=replace(spec,assets={**spec.assets,"settings":bind(settings)})
        with self.assertRaises(DeploymentConfigError):write_frontend_deployment(self.artifact/"wrong.json",wrong)
        settings.write_text(json.dumps({"retry":{"enabled":False,"provider":{"timeoutMs":120000,"maxRetries":0}}}))
        spec=replace(spec,assets={**spec.assets,"settings":bind(settings)})
        receipt=write_frontend_deployment(self.artifact/"deployment.json",spec)
        with self.assertRaises(DeploymentConfigError):write_process_config(self.artifact/"self-mutating.json",receipt,bind(HERE/"process_exec.py"),time.monotonic_ns())
    def test_profile_auth_contents_are_never_opened_by_producer(self):
        auth=self.directories["profile"]/"auth.json";auth.write_bytes(b"synthetic-unreadable")
        spec=self.spec()
        native_open=os.open
        def checked(path,*args,**kwargs):
            if str(path)==str(auth) or str(path)=="auth.json":raise AssertionError("Auth contents must never be opened")
            return native_open(path,*args,**kwargs)
        with patch("os.open",side_effect=checked):write_frontend_deployment(self.artifact/"deployment.json",spec)

    def test_process_config_does_not_reseal_tampered_frontend_directories(self):
        spec=self.spec();receipt=write_frontend_deployment(self.artifact/"deployment.json",spec)
        sealed=json.loads(receipt.path.read_bytes())
        old=self.directories["profile"];old.rename(self.root/"old-profile");old.mkdir(mode=0o700)
        original=self.root/"old-profile"/"settings.json";(old/"settings.json").write_bytes(original.read_bytes())
        # Rebinding unchanged settings is not allowed to erase the sealed directory's inode.
        sealed["assets"]["settings"]["mtime_ns_max"]=str((old/"settings.json").stat().st_mtime_ns)
        receipt.path.write_text(json.dumps(sealed))
        changed=bind(receipt.path)
        with self.assertRaises(DeploymentConfigError):
            write_process_config(self.root/"rebound-process.json",changed,bind(HERE/"process_exec.py"),time.monotonic_ns())
        self.assertFalse((self.root/"rebound-process.json").exists())

    def test_bootstrap_changed_after_extension_binding_is_not_reauthorized(self):
        spec=self.spec()
        self.bootstrap.path.write_bytes(b"#!/usr/bin/false\n# changed after binding\n")
        with self.assertRaises(DeploymentConfigError):
            write_frontend_deployment(self.artifact/"changed-bootstrap.json",spec)
        self.assertFalse((self.artifact/"changed-bootstrap.json").exists())

    def test_frontend_output_cannot_populate_sealed_empty_native_directories(self):
        spec=self.spec()
        for name in ("session_dir","temporary_dir"):
            output=self.directories[name]/"deployment.json"
            with self.subTest(name=name),self.assertRaises(DeploymentConfigError):
                write_frontend_deployment(output,spec)
            self.assertFalse(output.exists())

    def test_process_output_cannot_mutate_profile_or_public_cwd(self):
        spec=self.spec();receipt=write_frontend_deployment(self.artifact/"deployment.json",spec)
        for name in ("profile","cwd"):
            output=self.directories[name]/"process.json"
            with self.subTest(name=name),self.assertRaises(DeploymentConfigError):
                write_process_config(output,receipt,bind(HERE/"process_exec.py"),time.monotonic_ns())
            self.assertFalse(output.exists())

    def test_capture_cannot_reauthorize_changed_frontend(self):
        spec=self.spec();receipt=write_frontend_deployment(self.artifact/"deployment.json",spec)
        target=spec.assets["controller_main"].path
        real_capture=capture_path_identity
        mutated=False
        def replace_before_capture(path,**kwargs):
            nonlocal mutated
            if Path(path)==target and not mutated:
                mutated=True;target.write_bytes(b"export const changed = 123;\n")
            return real_capture(path,**kwargs)
        output=self.root/"process.json"
        with patch("experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_deployment.capture_path_identity",side_effect=replace_before_capture),self.assertRaises(DeploymentConfigError):
            write_process_config(output,receipt,bind(HERE/"process_exec.py"),time.monotonic_ns())
        self.assertTrue(mutated);self.assertFalse(output.exists())

    def test_capture_cannot_reauthorize_changed_node_deployment_or_exec(self):
        for target_name in ("node", "deployment", "process_exec"):
            case=ControllerDeploymentTest(methodName="test_extension_binding_is_fixed_bounded_and_no_overwrite")
            case.setUp()
            try:
                fake_node=case.assets/"node";fake_node.write_bytes(b"synthetic node\n");fake_node.chmod(0o700)
                fake_exec=case.assets/"process_exec.py";fake_exec.write_bytes(b"synthetic exec\n")
                case.raw_assets["node_executable"]=bind(fake_node)
                with patch("experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_deployment.NODE",str(fake_node)):
                    spec=case.spec();receipt=write_frontend_deployment(case.artifact/"deployment.json",spec)
                    target={"node":fake_node,"deployment":receipt.path,"process_exec":fake_exec}[target_name]
                    real_capture=capture_path_identity
                    mutated=False
                    def replace_before_capture(path,**kwargs):
                        nonlocal mutated
                        if Path(path)==target and not mutated:
                            mutated=True;target.write_bytes(target.read_bytes()+b" ")
                        return real_capture(path,**kwargs)
                    output=case.root/"process.json"
                    with patch("experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_deployment.capture_path_identity",side_effect=replace_before_capture),self.assertRaises(DeploymentConfigError):
                        write_process_config(output,receipt,bind(fake_exec),time.monotonic_ns())
                    self.assertTrue(mutated);self.assertFalse(output.exists())
            finally:case.tearDown()

    def test_provenance_binds_bootstrap_identity_mode_and_runtime_command(self):
        for change in ("bytes", "mode", "inode", "command"):
            case=ControllerDeploymentTest(methodName="test_extension_binding_is_fixed_bounded_and_no_overwrite")
            case.setUp()
            try:
                spec=case.spec();receipt=write_frontend_deployment(case.artifact/"deployment.json",spec)
                if change=="bytes":case.bootstrap.path.write_bytes(b"modified synthetic bridge")
                elif change=="mode":case.bootstrap.path.chmod(0o777)
                elif change=="inode":
                    replacement=case.assets/"replacement";replacement.write_bytes(case.bootstrap.path.read_bytes());replacement.chmod(0o700);replacement.replace(case.bootstrap.path)
                else:
                    binding=spec.assets["binding"].path
                    value=json.loads(binding.read_bytes());value["bridge"]["command"]=str(case.gate.path)
                    binding.write_text(json.dumps(value))
                output=case.root/"process.json"
                with self.subTest(change=change),self.assertRaises(DeploymentConfigError):
                    write_process_config(output,receipt,bind(HERE/"process_exec.py"),time.monotonic_ns())
                self.assertFalse(output.exists())
            finally:case.tearDown()

    def test_successful_publication_keeps_native_seals_valid(self):
        spec=self.spec();receipt=write_frontend_deployment(self.artifact/"deployment.json",spec)
        _revalidate_frontend_deployment(receipt.path,json.loads(receipt.path.read_bytes()))
        write_process_config(self.root/"process.json",receipt,bind(HERE/"process_exec.py"),time.monotonic_ns())
        _revalidate_frontend_deployment(receipt.path,json.loads(receipt.path.read_bytes()))
        self.assertEqual(list(self.directories["session_dir"].iterdir()),[])
        self.assertEqual(list(self.directories["temporary_dir"].iterdir()),[])

if __name__=="__main__":unittest.main(verbosity=2)
