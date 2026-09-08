"""Synthetic files only; no process, fixture server or model is launched."""
from __future__ import annotations
from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_readback as reader
import experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_acceptance as acceptance
import experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance as fixtures
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_driver import _expectation_record, _assessment_record, LIMITATIONS
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_acceptance import CombinationAssessment
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def bind(path):
    data=path.read_bytes()
    return FileBinding(path, hashlib.sha256(data).hexdigest(), len(data), path.stat().st_mtime_ns)


def record(binding):
    return {"path":str(binding.path), "sha256":binding.sha256, "bytes":binding.bytes, "mtime_ns_max":binding.mtime_ns_max}


class TerminalReadbackTests(unittest.TestCase):
    def setUp(self):
        self.external=tempfile.TemporaryDirectory(prefix="c1-readback-external-")
        self.out=Path(self.external.name).resolve()
        self.out.chmod(0o700)
        helper=fixtures.CombinationAcceptanceTests('test_positive_verifies_one_synthetic_combination')
        self.helper=helper
        original_file=helper.file
        directory_map={"artifact":"artifacts", "artifact/session":"artifacts/session", "artifact/tmp":"artifacts/tmp",
                       "cwd":"public", "source":"fixture/source", "trusted":"fixture/trusted-state", "bridge-state":"fixture/bridge-state"}
        file_map={"deployment.json":"artifacts/deployment.json", "normal-process-config.json":"control/normal-process-config.json",
                  "synthetic-process-config.json":"control/synthetic-process-config.json", "bridge-config.json":"fixture/bridge-config.json",
                  "controller-process-receipt.json":"evidence/controller-process-receipt.json",
                  "artifact/a2-synthetic-provider-metadata.json":"artifacts/a2-synthetic-provider-metadata.json"}
        def directory(relative):
            path=self.out/"namespace" if relative=="namespace" else helper.root/directory_map.get(relative,relative)
            path.mkdir(parents=True,exist_ok=True);path.chmod(0o700)
            return path
        def file(relative,data,mode):
            relative=file_map.get(relative,relative)
            (helper.root/relative).parent.mkdir(parents=True,exist_ok=True)
            (helper.root/relative).parent.chmod(0o700)
            return original_file(relative,data,mode)
        helper.directory=directory;helper.file=file
        helper.setUp()
        self.case=helper.root
        faux=helper.frontend/"a2-frontend-probes/a2-combination-frontend.ts"
        faux.parent.mkdir(mode=0o700)
        helper.synthetic_frontend_path.rename(faux)
        helper.synthetic_frontend_path=faux
        helper.synthetic_frontend=helper.binding(faux)
        helper.synthetic_config=replace(helper.synthetic_config,frontend_path=str(faux),
                                        frontend_identity=helper.path_identity(faux,fixtures.FAUX_SHA))
        helper.synthetic_config_binding=helper.bound_data("synthetic-process-config.json",asdict(helper.synthetic_config))
        helper.process_receipt=helper.write_process_receipt(0)
        helper.expectation=replace(helper.expectation,process_receipt=helper.process_receipt,synthetic_process_config=helper.synthetic_config_binding,
                                   synthetic_frontend=helper.synthetic_frontend)
        self.expected=helper.expectation
        seed=self.out/"seed";seed.mkdir(mode=0o700)
        policy={}
        for role in ("raw","auth","profile","controller","public"):
            p=self.out/("protected-"+role);p.mkdir(mode=0o700)
            s=p.stat();policy[role]={"path":str(p),"device":s.st_dev,"inode":s.st_ino}
        self.config_value={"schema_version":"argo-house-price-a2-combination-case-config/v2","case_root":str(self.case),
            "namespace_tree":asdict(self.expected.namespace_tree),"frontend_seed_tree":asdict(helper.tree(seed)),
            "installed_prime_tree":asdict(self.expected.installed_prime_tree),"protected_roots":policy,
            "expected_faux_frontend_sha256":fixtures.FAUX_SHA,"expected_fixture_module_sha256":"c"*64,
            "expected_acceptance_module_sha256":"d"*64}
        self.config=self.write(self.out/"case-config.json",self.config_value)
        self.admission=self.write(self.case/"case-admission.json",{"schema_version":"argo-house-price-a2-synthetic-case-admission/v1",
            "case_id":"A2-Faux-C1","synthetic_only":True,"actual_P0":False,"config":self.config_value})
        self.assessment=CombinationAssessment("PASS","VERIFIED_SYNTHETIC_COMBINATION",278,
            self.expected.current_session.sha256,helper.latest_binding.sha256,helper.latest_binding)
        self.payload={"schema_version":"argo-house-price-a2-synthetic-combination-case/v3","case_id":"A2-Faux-C1",
            "synthetic_only":True,"production_entry_executed":False,"actual_P0":False,"status":"VERIFIED_SYNTHETIC_COMBINATION",
            "stage":"COMPLETE","reason":"VERIFIED","context_id":fixtures.CONTEXT,"process_attempts":1,
            "source_bindings":self.config_value,"case_admission":record(self.admission),"latest_gate":record(helper.latest_binding),
            "expectation":_expectation_record(self.expected),"assessment":_assessment_record(self.assessment),
            "current_session_id":fixtures.SESSION_ID,"elapsed_seconds":10.0,"cleanup_confirmed":True,
            "fixture_close_result":{"schema_version":"argo-house-price-a2-fixture-close/v1","confirmed":True,
                "shutdown_completed":True,"serve_thread_stopped":True,"socket_closed":True,"cleanup_thread_stopped":True,
                "timed_out":False,"error":None,"elapsed_seconds":0.01},"limitations":list(LIMITATIONS)}
        for name in ("normal_process_config","synthetic_process_config","process_receipt","gate_config","metadata","current_session"):
            self.payload[name]=record(getattr(self.expected,name))
        self.result={"status":"VERIFIED_SYNTHETIC_COMBINATION","stage":"COMPLETE","reason":"VERIFIED",
            "receipt":None,"process_attempts":1,"controller_context_id":fixtures.CONTEXT}
        self.save_receipt()
        self.stderr=self.write(self.out/"stderr",b"")

    def tearDown(self):
        self.helper.tearDown();self.external.cleanup()

    def write(self,path,value):
        path.write_bytes(value if isinstance(value,bytes) else canonical(value));path.chmod(0o600)
        return bind(path)

    def save_receipt(self):
        self.receipt=self.write(self.case/"evidence/case-receipt.json",self.payload)
        self.result["receipt"]=record(self.receipt)
        self.save_result()

    def save_result(self):
        self.stdout=self.write(self.out/"stdout",canonical(self.result)+b"\n")

    def invoke(self,returncode=0,complete=True,assessment_effect=None,real_assessor=False):
        with patch.object(reader,"verify_tree",create=True), patch.object(acceptance,"verify_tree"):
            if real_assessor:
                return reader.readback_combination(self.config,returncode=returncode,stdout=self.stdout,stderr=self.stderr,terminal_complete=complete)
            with patch.object(reader,"assess_combination",return_value=self.assessment,side_effect=assessment_effect,create=True) as assessed:
                result=reader.readback_combination(self.config,returncode=returncode,stdout=self.stdout,stderr=self.stderr,terminal_complete=complete)
                self.assess_calls=assessed.call_count
                self.assess_args=assessed.call_args
                return result

    def test_valid_original_bindings_and_terminal_conjunction(self):
        result=self.invoke()
        self.assertEqual((result.status,result.reason),("PASS","VERIFIED_SYNTHETIC_COMBINATION"))
        self.assertEqual(result.case_receipt,self.receipt);self.assertEqual(result.assessment,self.assessment)
        self.assertEqual(self.assess_calls,1);self.assertEqual(self.assess_args.args,(self.expected,))

    def test_existing_pure_assessor_joins_file_fixture(self):
        result=self.invoke(real_assessor=True)
        self.assertEqual(result.status,"PASS");self.assertEqual(result.assessment,self.assessment)

    def test_incomplete_terminal_or_non_integer_zero_never_reads_case(self):
        for code,complete in [(None,True),(0,False),(False,True),(0.0,True),(1,True),(-9,True)]:
            with self.subTest(code=code,complete=complete):
                result=self.invoke(code,complete)
                self.assertNotEqual(result.status,"PASS");self.assertEqual(self.assess_calls,0)

    def test_late_failed_outer_result_beats_pass_looking_receipt(self):
        self.result.update(status="NOT_ADMITTED",reason="STAGE_FAILED",receipt=None);self.save_result()
        result=self.invoke()
        self.assertNotEqual(result.status,"PASS");self.assertEqual(self.assess_calls,0)
        self.assertEqual(json.loads(self.receipt.path.read_bytes())["status"],"VERIFIED_SYNTHETIC_COMBINATION")

    def test_duplicate_extra_or_partial_outer_json_rejected(self):
        original=self.stdout.path.read_bytes()
        bad_values=[original+original,original[:-2],original.replace(b'{',b'{"status":"VERIFIED_SYNTHETIC_COMBINATION",',1),
                    canonical({**self.result,"unknown":True})+b"\n"]
        for data in bad_values:
            with self.subTest(data=data[:80]):
                self.stdout=self.write(self.stdout.path,data)
                self.assertNotEqual(self.invoke().status,"PASS")

    def test_missing_expectation_or_old_schema_rejected(self):
        original=canonical(self.payload)
        for change in ("missing","old"):
            self.payload=json.loads(original)
            if change=="missing":self.payload.pop("expectation")
            else:self.payload["schema_version"]="argo-house-price-a2-synthetic-combination-case/v2"
            self.save_receipt();self.assertNotEqual(self.invoke().status,"PASS")

    def test_original_admission_or_gate_mutation_not_recaptured(self):
        for binding in [self.admission,self.helper.latest_binding]:
            data=binding.path.read_bytes();times=binding.path.stat()
            binding.path.write_bytes(b"x"*len(data));os.utime(binding.path,ns=(times.st_atime_ns,times.st_mtime_ns))
            self.assertNotEqual(self.invoke().status,"PASS")
            binding.path.write_bytes(data);os.utime(binding.path,ns=(times.st_atime_ns,times.st_mtime_ns))

    def test_source_config_or_repeated_binding_mismatch_rejected(self):
        original=canonical(self.payload)
        self.payload["source_bindings"]["expected_acceptance_module_sha256"]="f"*64
        self.save_receipt();self.assertNotEqual(self.invoke().status,"PASS")
        self.payload=json.loads(original);self.payload["metadata"]["sha256"]="0"*64
        self.save_receipt();self.assertNotEqual(self.invoke().status,"PASS")

    def test_wrong_expectation_tree_or_gate_binding_rejected(self):
        original=canonical(self.payload)
        self.payload["expectation"]["namespace_tree"]["tree_sha256"]="1"*64
        self.save_receipt();self.assertNotEqual(self.invoke().status,"PASS")
        self.payload=json.loads(original);self.payload["assessment"]["native_gate_binding"]["sha256"]="2"*64
        self.save_receipt();self.assertNotEqual(self.invoke().status,"PASS")

    def test_nonexact_flags_deadlines_and_cleanup_rejected(self):
        original=canonical(self.payload)
        for key,value in [("process_attempts",True),("synthetic_only",1),("elapsed_seconds",180),("cleanup_confirmed",1)]:
            self.payload=json.loads(original);self.payload[key]=value;self.save_receipt()
            self.assertNotEqual(self.invoke().status,"PASS")
        self.payload=json.loads(original);self.payload["fixture_close_result"]["elapsed_seconds"]=2.01
        self.save_receipt();self.assertNotEqual(self.invoke().status,"PASS")

    def test_assessor_rejection_and_mismatched_usage_rejected(self):
        for outcome in [replace(self.assessment,status="NOT_ADMITTED",reason="GATE_INVALID"),replace(self.assessment,campaign_tokens=279)]:
            self.assertNotEqual(self.invoke(assessment_effect=lambda _e,o=outcome:o).status,"PASS")

    def test_mutation_during_pure_assessment_fails_final_reopen(self):
        def mutate(_expectation):
            self.expected.metadata.path.write_bytes(b"x")
            return self.assessment
        self.assertNotEqual(self.invoke(assessment_effect=mutate).status,"PASS")
        self.assertEqual(self.assess_calls,1)

    def test_config_mutation_and_terminal_symlink_rejected(self):
        original=self.config.path.read_bytes();times=self.config.path.stat()
        self.config.path.write_bytes(b"x"*len(original));os.utime(self.config.path,ns=(times.st_atime_ns,times.st_mtime_ns))
        self.assertNotEqual(self.invoke().status,"PASS")
        self.config.path.write_bytes(original);os.utime(self.config.path,ns=(times.st_atime_ns,times.st_mtime_ns))
        self.stdout.path.rename(self.out/"saved-stdout");self.stdout.path.symlink_to(self.out/"saved-stdout")
        self.assertNotEqual(self.invoke().status,"PASS")

    def test_missing_bound_output_or_oversized_terminal_rejects(self):
        self.stdout.path.unlink()
        with patch.object(reader,"_config",side_effect=AssertionError("case read")) as config:
            result=self.invoke()
        config.assert_not_called()
        self.assertEqual((result.status,result.reason),("UNKNOWN","TERMINAL_INCOMPLETE"))
        self.stdout=self.write(self.out/"stdout",b"x"*65537)
        result=self.invoke()
        self.assertEqual((result.status,result.reason),("NOT_ADMITTED","TERMINAL_INVALID"))

    def test_missing_root_stderr_is_unknown_before_case_read(self):
        self.stderr.path.unlink()
        with patch.object(reader,"_config",side_effect=AssertionError("case read")) as config:
            result=self.invoke()
        config.assert_not_called()
        self.assertEqual((result.status,result.reason),("UNKNOWN","TERMINAL_INCOMPLETE"))

    def test_republished_arbitrary_scope_cannot_receive_pass(self):
        self.payload["limitations"]=["Synthetic receipt now claims production execution."]
        self.save_receipt()
        result=self.invoke()
        self.assertNotEqual(result.status,"PASS")
        self.assertEqual(self.assess_calls,0)

    def test_unknown_expectation_fields_and_typed_binding_counters_reject(self):
        original=canonical(self.payload)
        for mode in ("extra","boolean","negative"):
            self.payload=json.loads(original)
            if mode=="extra":self.payload["expectation"]["unbound_extra"]="ignored"
            if mode=="boolean":self.payload["expectation"]["metadata"]["bytes"]=True
            if mode=="negative":self.payload["expectation"]["metadata"]["mtime_ns_max"]=-1
            self.save_receipt()
            self.assertNotEqual(self.invoke().status,"PASS")

    def test_protected_directory_replacement_is_not_resealed(self):
        path=Path(self.config_value["protected_roots"]["profile"]["path"])
        path.rename(self.out/"old-protected-profile");path.mkdir(mode=0o700)
        self.assertNotEqual(self.invoke().status,"PASS")

    def test_no_writes_or_subprocesses_and_protected_content_unread(self):
        sentinels=[]
        for role in self.config_value["protected_roots"].values():
            p=Path(role["path"])/"private-sentinel";p.write_bytes(b"not to be opened");sentinels.append(p)
        original_open=os.open
        def checked_open(path,flags,*args,**kwargs):
            self.assertFalse(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
            self.assertNotIn(Path(path),sentinels)
            self.assertNotEqual(str(path),"private-sentinel")
            return original_open(path,flags,*args,**kwargs)
        with patch.object(os,"open",side_effect=checked_open),patch("subprocess.Popen",side_effect=AssertionError("process attempted")):
            self.assertEqual(self.invoke().status,"PASS")


if __name__=="__main__":
    unittest.main(verbosity=2)
