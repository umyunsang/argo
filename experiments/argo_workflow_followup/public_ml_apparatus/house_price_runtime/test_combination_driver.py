"""One-case orchestration tests with all fixture/model/process calls mocked."""
from __future__ import annotations
from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_driver import CaseProtectedRoots, CombinationCaseConfig, run_case
import experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_driver as driver
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_fixture import CombinationFixtureError, FixtureCloseResult
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_acceptance import CombinationAssessment
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.source_closure import SourceTree
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.staging import DirectoryIdentity
import experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver as phase_driver_test_helpers
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.usage_observer import UsageObservation

SID="11111111-1111-4111-8111-111111111111"
IDS=("22222222-2222-4222-8222-222222222222","33333333-3333-4333-8333-333333333333")

def bind(path):
    data=path.read_bytes();return FileBinding(path,hashlib.sha256(data).hexdigest(),len(data),path.stat().st_mtime_ns)
def identity(path):
    info=path.stat();return DirectoryIdentity(path,info.st_dev,info.st_ino)
def tree(path):
    info=path.stat();return SourceTree(str(path),info.st_dev,info.st_ino,"a"*64,0,0,0,0,info.st_mtime_ns)

class CaseDriverTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="hp-case-driver-mock-")
        self.root=Path(self.temp.name).resolve();self.root.chmod(0o700)
        roots=[]
        for name in ("namespace","seed","prime"):
            path=self.root/name;path.mkdir(mode=0o700);roots.append(tree(path))
        protected=[]
        for name in ("user-raw","user-auth","user-profile","user-controller","user-public"):
            path=self.root/name;path.mkdir(mode=0o700);protected.append(identity(path))
        self.config=CombinationCaseConfig(self.root/"case",*roots,"b"*64,"c"*64,"d"*64,CaseProtectedRoots(*protected))
        self.closed=0
        self.confirmed=True
        self.helper=phase_driver_test_helpers.PhaseDriverTests("test_startup_guard_is_callable_and_same_observer_finalizes_clean_receipts")
        self.helper.setUp()
        self.receipt=self.helper.process_receipt()
    def tearDown(self):
        self.helper.tearDown();self.temp.cleanup()
    def prepare(self,base):
        base.mkdir(mode=0o700)
        states=[]
        for name in ("source","trusted","bridge"):
            path=base/name;path.mkdir(mode=0o700);states.append(path)
        bridge=base/"bridge.json";bridge.write_bytes(b"{}")
        def close():
            self.closed+=1
            return FixtureCloseResult("argo-house-price-a2-fixture-close/v1",self.confirmed,self.confirmed,
                self.confirmed,self.confirmed,self.confirmed,False,None if self.confirmed else "CLOSE_FAILED",0.01)
        return SimpleNamespace(context_id="e"*64,bridge_config=bind(bridge),source=identity(states[0]),
            trusted_state=identity(states[1]),bridge_state=identity(states[2]),verified_dev_run_ids=IDS,
            research_sha256="f"*64,source_tree=tree(states[0]),trusted_state_tree=tree(states[1]),state_tree=tree(states[2]),close=close)
    def environment(self,config,fixture,started_ns):
        root=config.case_root
        artifact=root/"artifacts";artifact.mkdir(mode=0o700)
        session=artifact/"session";session.mkdir(mode=0o700)
        tmp=artifact/"tmp";tmp.mkdir(mode=0o700)
        control=root/"control";control.mkdir(mode=0o700)
        frontend=root/"frontend";frontend.mkdir(mode=0o700)
        gate_outcomes=root/"gate-outcomes";gate_outcomes.mkdir(mode=0o700)
        latest_gate=gate_outcomes/"0001-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.json";latest_gate.write_bytes(b"{\"synthetic\":true}")
        self.latest_gate=bind(latest_gate)
        normal=control/"normal-process-config.json";normal.write_bytes(b"{}")
        synthetic=control/"synthetic-process-config.json";synthetic.write_bytes(b"{}")
        gate=frontend/"gate.json";gate.write_bytes(b"{}")
        faux=frontend/"faux.ts";faux.write_bytes(b"synthetic entry")
        self.process=replace(self.helper.process_config,session_dir=str(session),artifact_root=str(artifact),
            session_dir_identity=self.helper.directory_path_identity(session),
            artifact_root_identity=self.helper.directory_path_identity(artifact))
        self.session_dir=session
        return SimpleNamespace(normal_process=bind(normal),synthetic_process=bind(synthetic),process_config=self.process,
            gate_config=bind(gate),synthetic_frontend=bind(faux),frontend_tree=tree(frontend),
            session_directory=identity(session),gate_outcome_directory=identity(gate_outcomes),
            cwd=str(root/"public"),artifact_root=artifact)
    def observe(self):
        path=self.session_dir/(SID+".jsonl")
        if not path.exists():return UsageObservation("WAITING_FIRST_USAGE",None,False,None,None,None,None,0)
        data=path.read_bytes();return UsageObservation("WITHIN_BUDGET",None,True,100,100,SID,hashlib.sha256(data).hexdigest(),len(data))
    def process_call(self,config,*,abort_event,campaign_guard):
        self.assertIs(config,self.process)
        self.assertTrue(callable(campaign_guard));self.assertIsNone(campaign_guard())
        path=self.session_dir/(SID+".jsonl");path.write_bytes(b"synthetic native session\n")
        metadata=Path(config.artifact_root)/"a2-synthetic-provider-metadata.json"
        metadata.write_bytes(b"{}");metadata.chmod(0o600)
        self.assertIsNone(campaign_guard())
        return self.receipt
    def accepted_assessment(self):
        return CombinationAssessment(
            "PASS", "VERIFIED_SYNTHETIC_COMBINATION", 100, "a"*64,
            self.latest_gate.sha256, self.latest_gate,
        )
    def invoke(self,assessment=None,fixture_error=False,source_effect=None,assessment_effect=None):
        observer=SimpleNamespace(observe=self.observe)
        self.assessment_expectations=[]
        def evaluate(expectation):
            self.assessment_expectations.append(expectation)
            if assessment_effect is not None:
                return assessment_effect(expectation)
            if assessment is not None:
                return assessment
            return self.accepted_assessment()
        with patch.object(driver,"_verify_sources",side_effect=source_effect), \
                patch.object(driver,"prepare_fixture",side_effect=OSError("private fixture error") if fixture_error else self.prepare), \
                patch.object(driver,"_prepare_environment",side_effect=self.environment), \
                patch.object(driver,"UsageObserver",return_value=observer), \
                patch.object(driver,"run_controller",side_effect=self.process_call) as run, \
                patch.object(driver,"assess_combination",side_effect=evaluate) as assess, \
                patch.object(driver.threading,"Timer") as timer:
            result=run_case(self.config)
        self.run_count=run.call_count;self.assess_count=assess.call_count;self.timer=timer
        return result
    def test_one_synthetic_process_uses_guard_and_typed_cleanup_before_receipt(self):
        result=self.invoke()
        self.assertEqual(result.status,"VERIFIED_SYNTHETIC_COMBINATION")
        self.assertEqual(result.process_attempts,1);self.assertEqual(self.run_count,1);self.assertEqual(self.closed,1)
        self.assertEqual(self.assess_count,2);self.assertEqual(self.timer.call_args.args[0],20)
        self.timer.return_value.start.assert_called_once();self.timer.return_value.cancel.assert_called_once()
        value=json.loads(result.receipt.path.read_bytes())
        self.assertIs(value["synthetic_only"],True);self.assertIs(value["actual_P0"],False)
        self.assertIs(value["production_entry_executed"],False);self.assertIs(value["cleanup_confirmed"],True)
        self.assertEqual(value["fixture_close_result"]["confirmed"],True)
        self.assertEqual(set(p.name for p in (self.config.case_root/"evidence").iterdir()),{"case-receipt.json","controller-process-receipt.json"})
    def test_existing_case_cannot_start_or_write(self):
        self.config.case_root.mkdir(mode=0o700)
        marker=self.config.case_root/"keep";marker.write_bytes(b"held")
        result=self.invoke()
        self.assertEqual((result.status,result.reason),("NOT_STARTED","ALREADY_ATTEMPTED"))
        self.assertEqual(self.run_count,0);self.assertEqual(marker.read_bytes(),b"held")
    def test_unknown_cleanup_or_failed_assessment_never_passes(self):
        self.confirmed=False
        result=self.invoke()
        self.assertEqual(result.status,"NOT_ADMITTED");self.assertEqual(result.reason,"CLEANUP_UNCONFIRMED")
        self.assertEqual(self.closed,1)
        value=json.loads(result.receipt.path.read_bytes());self.assertFalse(value["cleanup_confirmed"])
    def test_rejected_assessment_retains_one_attempt(self):
        result=self.invoke(CombinationAssessment("NOT_ADMITTED","GATE_INVALID",None,None,None))
        self.assertEqual(result.reason,"ASSESSMENT_REJECTED");self.assertEqual(result.process_attempts,1)
        self.assertEqual(self.closed,1);self.assertEqual(self.assess_count,1)
        value=json.loads(result.receipt.path.read_bytes())
        self.assertIsNotNone(value["case_admission"])
        self.assertIsNotNone(value["expectation"])
        self.assertIsNone(value["latest_gate"])
        self.assertIsNone(value["assessment"]["native_gate_binding"])
    def test_fixture_error_preserves_admission_without_process_or_exception_payload(self):
        result=self.invoke(fixture_error=True)
        self.assertEqual(result.status,"NOT_ADMITTED");self.assertEqual(self.run_count,0)
        self.assertTrue((self.config.case_root/"case-admission.json").exists())
        self.assertNotIn("private fixture error",result.receipt.path.read_text())
        value=json.loads(result.receipt.path.read_bytes())
        self.assertIsNotNone(value["case_admission"])
        self.assertIsNone(value["expectation"])
        self.assertIsNone(value["latest_gate"])
    def test_bad_source_fails_before_case_creation(self):
        with patch.object(driver,"_verify_sources",side_effect=ValueError("private source")),patch.object(driver,"prepare_fixture") as fixture:
            result=run_case(self.config)
        self.assertEqual((result.status,result.reason),("NOT_STARTED","SOURCE_MISMATCH"))
        fixture.assert_not_called();self.assertFalse(self.config.case_root.exists())

    def test_partially_created_fixture_with_unconfirmed_close_is_not_generic_failure(self):
        close_result=FixtureCloseResult("argo-house-price-a2-fixture-close/v1",False,False,False,False,False,True,"CLOSE_TIMEOUT",2.1)
        def failed_fixture(base):
            base.mkdir(mode=0o700)
            raise CombinationFixtureError(close_result,identity(base))
        with patch.object(driver,"_verify_sources"),patch.object(driver,"prepare_fixture",side_effect=failed_fixture),patch.object(driver,"run_controller") as run:
            result=run_case(self.config)
        self.assertEqual((result.status,result.reason),("NOT_ADMITTED","CLEANUP_UNCONFIRMED"))
        self.assertEqual(result.stage,"CLEANUP");run.assert_not_called()
        value=json.loads(result.receipt.path.read_bytes())
        self.assertFalse(value["cleanup_confirmed"])
        self.assertEqual(value["fixture_close_result"]["error"],"CLOSE_TIMEOUT")

    def test_evidence_writer_rejects_caps_completes_short_writes_and_retains_partial(self):
        path=self.root/"output";path.mkdir(mode=0o700);root_identity=identity(path)
        original=os.write
        with patch.object(driver.os,"write",side_effect=lambda fd,data:original(fd,data[:5])):
            first=driver._publish(root_identity,"case-receipt.json",{"value":"synthetic"},driver.EVIDENCE_FILES,1114112)
        self.assertEqual(json.loads(first.path.read_bytes()),{"value":"synthetic"})
        with self.assertRaises(driver.CaseError):
            driver._publish(root_identity,"case-receipt.json",{"duplicate":True},driver.EVIDENCE_FILES,1114112)
        with self.assertRaises(driver.CaseError):
            driver._publish(root_identity,"controller-process-receipt.json",{"oversize":"x"*1048576},driver.EVIDENCE_FILES,1114112)
        self.assertFalse((path/"controller-process-receipt.json").exists())
        calls=0
        def partial(fd,data):
            nonlocal calls
            calls+=1
            if calls>1:raise OSError("synthetic partial")
            return original(fd,data[:3])
        with patch.object(driver.os,"write",side_effect=partial),self.assertRaises(OSError):
            driver._publish(root_identity,"controller-process-receipt.json",{"partial":True},driver.EVIDENCE_FILES,1114112)
        self.assertEqual((path/"controller-process-receipt.json").stat().st_size,3)
        with self.assertRaises(driver.CaseError):
            driver._publish(root_identity,"controller-process-receipt.json",{"retry":True},driver.EVIDENCE_FILES,1114112)

    def test_case_root_inside_protected_profile_starts_nothing(self):
        profile=self.root/"user-profile"
        self.config=replace(self.config,case_root=profile/"case")
        result=self.invoke()
        self.assertEqual((result.status,result.reason),("NOT_STARTED","INVALID_INPUT"))
        self.assertEqual(self.run_count,0)
        self.assertFalse(self.config.case_root.exists())

    def test_source_validation_time_counts_before_admission(self):
        clock={"now":0.0}
        def expensive_verification(_):clock["now"]=170.0
        with patch.object(driver.time,"monotonic",side_effect=lambda:clock["now"]):
            result=self.invoke(source_effect=expensive_verification)
        self.assertEqual(self.run_count,0)
        self.assertEqual((result.status,result.reason),("NOT_STARTED","STAGE_FAILED"))
        self.assertFalse(self.config.case_root.exists())

    def test_metadata_deleted_after_assessment_cannot_be_verified(self):
        def delete_metadata(expectation):
            expectation.metadata.path.unlink()
            return self.accepted_assessment()
        result=self.invoke(assessment_effect=delete_metadata)
        self.assertEqual(result.status,"NOT_ADMITTED")
        self.assertEqual(self.run_count,1)
        self.assertEqual(self.closed,1)
        self.assertEqual(json.loads(result.receipt.path.read_bytes())["status"],"NOT_ADMITTED")

    def test_case_policy_is_required_and_replaced_root_blocks_before_creation(self):
        bad=replace(self.config,protected_roots=None)
        with patch.object(driver,"prepare_fixture") as fixture:
            result=run_case(bad)
        self.assertEqual((result.status,result.reason),("NOT_STARTED","INVALID_INPUT"));fixture.assert_not_called()
        profile=self.config.protected_roots.profile.path
        profile.rename(self.root/"old-profile");profile.mkdir(mode=0o700)
        result=self.invoke()
        self.assertEqual((result.status,result.reason),("NOT_STARTED","INVALID_INPUT"))
        self.assertEqual(self.run_count,0);self.assertFalse(self.config.case_root.exists())

    def test_admission_and_final_receipts_bind_policy_without_reading_contents(self):
        protected=self.config.protected_roots
        sentinels=[]
        for name in ("raw","auth","profile","controller","public"):
            path=getattr(protected,name).path/"sensitive-content"
            path.write_bytes(b"synthetic secret sentinel");sentinels.append(path)
        real_open=os.open
        def safe_open(path,*args,**kwargs):
            if str(path)=="sensitive-content" or Path(path) in sentinels:raise AssertionError("protected file opened")
            return real_open(path,*args,**kwargs)
        with patch.object(driver.os,"open",side_effect=safe_open):result=self.invoke()
        self.assertEqual(result.status,"VERIFIED_SYNTHETIC_COMBINATION")
        admission=json.loads((self.config.case_root/"case-admission.json").read_bytes())
        final=json.loads(result.receipt.path.read_bytes())
        expected=driver._config_record(self.config)["protected_roots"]
        self.assertEqual(admission["config"]["protected_roots"],expected)
        self.assertEqual(final["source_bindings"]["protected_roots"],expected)

    def test_cleanup_mutation_or_second_assessment_failure_prevents_verified(self):
        original_prepare=self.prepare
        def mutating_prepare(base):
            fixture=original_prepare(base)
            original_close=fixture.close
            def close():
                answer=original_close()
                (self.config.case_root/"control"/"normal-process-config.json").write_bytes(b"changed")
                return answer
            fixture.close=close
            return fixture
        self.prepare=mutating_prepare
        result=self.invoke()
        self.assertEqual(result.status,"NOT_ADMITTED");self.assertEqual(self.closed,1)
        self.assertEqual(self.assess_count,1)

    def test_metadata_parent_fsync_failure_never_publishes_verified(self):
        real_fsync=os.fsync
        metadata_checked={"seen":False}
        def sync(fd):
            info=os.fstat(fd)
            if hasattr(self,"session_dir"):
                parent=self.session_dir.parent
                if (info.st_dev,info.st_ino)==(parent.stat().st_dev,parent.stat().st_ino):
                    metadata_checked["seen"]=True
                    raise OSError("synthetic metadata parent sync")
            return real_fsync(fd)
        with patch.object(driver.os,"fsync",side_effect=sync):result=self.invoke()
        self.assertTrue(metadata_checked["seen"])
        self.assertEqual(result.status,"NOT_ADMITTED")
        self.assertEqual(json.loads(result.receipt.path.read_bytes())["status"],"NOT_ADMITTED")

    def test_assessment_record_serializes_valid_gate_binding_independently(self):
        gate=FileBinding(Path("/tmp/a2-driver-gate.json"),"a"*64,17,23)
        assessment=CombinationAssessment("NOT_ADMITTED","OUTPUT_LIMIT",278,"b"*64,gate.sha256,gate)
        self.assertEqual(driver._assessment_record(assessment),{
            "status":"NOT_ADMITTED","reason":"OUTPUT_LIMIT","campaign_tokens":278,
            "session_sha256":"b"*64,"native_gate_sha256":"a"*64,
            "native_gate_binding":{"path":"/tmp/a2-driver-gate.json","sha256":"a"*64,
                "bytes":17,"mtime_ns_max":23},
        })

    def test_assessment_record_serializes_paired_null_gate_independently(self):
        assessment=CombinationAssessment("NOT_ADMITTED","GATE_INVALID",None,None,None,None)
        self.assertEqual(driver._assessment_record(assessment),{
            "status":"NOT_ADMITTED","reason":"GATE_INVALID","campaign_tokens":None,
            "session_sha256":None,"native_gate_sha256":None,"native_gate_binding":None,
        })

    def test_assessment_record_rejects_digest_without_original_binding(self):
        assessment=CombinationAssessment("NOT_ADMITTED","OUTPUT_LIMIT",278,"b"*64,"a"*64,None)
        with self.assertRaises(driver.CaseError):driver._assessment_record(assessment)

    def test_assessment_record_rejects_malformed_original_binding(self):
        malformed=FileBinding(Path("relative-gate.json"),"a"*64,-1,-1)
        assessment=CombinationAssessment("NOT_ADMITTED","OUTPUT_LIMIT",278,"b"*64,malformed.sha256,malformed)
        with self.assertRaises(driver.CaseError):driver._assessment_record(assessment)

    def test_v3_receipt_retains_original_admission_expectation_and_latest_gate(self):
        result=self.invoke()
        self.assertEqual(result.status,"VERIFIED_SYNTHETIC_COMBINATION")
        value=json.loads(result.receipt.path.read_bytes())
        self.assertEqual(value["schema_version"],"argo-house-price-a2-synthetic-combination-case/v3")
        self.assertEqual(value["case_admission"]["path"],str(self.config.case_root/"case-admission.json"))
        self.assertEqual(value["case_admission"]["sha256"],hashlib.sha256((self.config.case_root/"case-admission.json").read_bytes()).hexdigest())
        self.assertEqual(value["latest_gate"],driver._binding_dict(self.latest_gate))
        self.assertEqual(value["expectation"],driver._expectation_record(self.assessment_expectations[0]))
        self.assertEqual(value["assessment"]["native_gate_binding"],driver._binding_dict(self.latest_gate))

    def test_admission_mutation_after_first_assessment_rejects_original_binding(self):
        original_prepare=self.prepare
        def mutating_prepare(base):
            fixture=original_prepare(base)
            original_close=fixture.close
            def close():
                answer=original_close()
                (self.config.case_root/"case-admission.json").write_bytes(b"changed admission")
                return answer
            fixture.close=close
            return fixture
        self.prepare=mutating_prepare
        result=self.invoke()
        self.assertEqual((result.status,result.stage,result.reason),("NOT_ADMITTED","ACCEPTANCE","STAGE_FAILED"))
        self.assertEqual(self.assess_count,1)

    def test_latest_gate_mutation_after_first_assessment_rejects_original_binding(self):
        original_prepare=self.prepare
        def mutating_prepare(base):
            fixture=original_prepare(base)
            original_close=fixture.close
            def close():
                answer=original_close()
                self.latest_gate.path.write_bytes(b"changed gate")
                return answer
            fixture.close=close
            return fixture
        self.prepare=mutating_prepare
        result=self.invoke()
        self.assertEqual((result.status,result.stage,result.reason),("NOT_ADMITTED","ACCEPTANCE","STAGE_FAILED"))
        self.assertEqual(self.assess_count,1)

    def test_final_late_failure_still_returns_null_binding_and_preserves_receipt(self):
        original=driver._reopen_final_references
        def fail_after_publication(*args,**kwargs):
            original(*args,**kwargs)
            if (self.config.case_root/"evidence"/"case-receipt.json").exists():
                raise driver.CaseError()
        with patch.object(driver,"_reopen_final_references",side_effect=fail_after_publication):
            result=self.invoke()
        self.assertEqual((result.status,result.reason),("NOT_ADMITTED","STAGE_FAILED"))
        self.assertIsNone(result.receipt)
        retained=json.loads((self.config.case_root/"evidence"/"case-receipt.json").read_bytes())
        self.assertEqual(retained["status"],"VERIFIED_SYNTHETIC_COMBINATION")

    def test_case_config_v2_rejects_missing_policy_and_roundtrips_exact_roles(self):
        path=self.root/"config.json"
        value=driver._config_record(self.config)
        path.write_bytes(json.dumps(value).encode());digest=hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(driver._load_case_config(path,digest),self.config)
        value.pop("protected_roots")
        path.write_bytes(json.dumps(value).encode());digest=hashlib.sha256(path.read_bytes()).hexdigest()
        with self.assertRaises(driver.CaseError):driver._load_case_config(path,digest)

if __name__=="__main__":unittest.main(verbosity=2)
