"""Synthetic trusted-receipt provenance and exact regrading tests."""
from __future__ import annotations

from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.receipt_store import ReceiptError, ExpectedDevExecution, verify_dev_receipt


def sha(data):return hashlib.sha256(data).hexdigest()


class DevReceiptTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="hp-receipt-test-")
        self.root=Path(self.tmp.name).resolve()
        self.pred=self.bind("pred.csv",b"Id,SalePrice\n001,10.25\n002,19.75\n")
        self.ids=self.bind("ids.json",b'["001","002"]')
        self.targets=self.bind("targets.csv",b"Id,SalePrice\n001,10\n002,20\n")
        self.expected=ExpectedDevExecution(
            run_id="191407a0-84ce-47e6-afa4-298d034b8aa3",
            experiment_id="cbfc2315-b262-4608-806a-65f0080de6e5",
            native_commit="a"*40, native_source_digest="b"*64,
            closure_sha256="c"*64,solution_sha256="d"*64,intent_sha256="e"*64,
            task_sha256="1"*64,environment_sha256="2"*64,protocol_sha256="3"*64,
            runner_sha256="4"*64,native_status="DONE",rows=2)
        self.record={"schema_version":"argo-house-price-dev-receipt/v1","phase":"dev",
            **{k:v for k,v in asdict(self.expected).items() if k!="native_status"},
            "prediction_sha256":self.pred.sha256,"prediction_bytes":self.pred.bytes,
            "prediction_mtime_ns_max":self.pred.mtime_ns_max,"ids_sha256":self.ids.sha256,
            "targets_sha256":self.targets.sha256,"mae_numerator":"1","mae_denominator":"4"}

    def tearDown(self):self.tmp.cleanup()

    def bind(self,name,data):
        path=self.root/name;path.write_bytes(data)
        return FileBinding(path,sha(data),len(data),path.stat().st_mtime_ns)

    def receipt(self,record=None):
        return self.bind("receipt.json",json.dumps(self.record if record is None else record,separators=(",",":")).encode())

    def verify(self,record=None,expected=None):
        receipt=self.receipt(record)
        verified=verify_dev_receipt(receipt,self.expected if expected is None else expected,self.pred,self.ids,self.targets)
        return receipt,verified

    def test_expected_independent_provenance_and_recomputed_score_construct_internal_receipt(self):
        receipt,verified=self.verify()
        self.assertEqual(verified.eligibility.receipt_sha256,receipt.sha256)
        self.assertEqual(verified.eligibility.code_sha256,self.expected.solution_sha256)
        self.assertEqual(verified.eligibility.closure_sha256,self.expected.closure_sha256)
        self.assertEqual(verified.score.mae,Fraction(1,4))
        public=verified.public_result()
        self.assertEqual(public["mae"],"0.250000")
        self.assertNotIn("001",json.dumps(public));self.assertNotIn("targets",json.dumps(public))

    def test_every_expected_identity_field_is_checked_not_self_attested(self):
        for field,value in asdict(self.expected).items():
            if field=="native_status":continue
            record=self.record.copy()
            record[field]=3 if field=="rows" else ("f"*40 if field=="native_commit" else "f"*64)
            with self.subTest(field=field),self.assertRaisesRegex(ReceiptError,"^RECEIPT_INVALID$"):
                self.verify(record)
        for state in ["RUNNING","FAILED","UNKNOWN"]:
            with self.assertRaises(ReceiptError):self.verify(expected=replace(self.expected,native_status=state))

    def test_scalar_metric_and_artifact_bindings_rederived_from_opened_bytes(self):
        for field,value in [("mae_numerator","2"),("mae_denominator","3"),("mae_denominator","0"),
                            ("mae_numerator","1"*257),("prediction_sha256","f"*64),
                            ("prediction_bytes",3),("prediction_mtime_ns_max",0),
                            ("ids_sha256","f"*64),("targets_sha256","f"*64)]:
            record=self.record.copy();record[field]=value
            with self.subTest(field=field),self.assertRaises(ReceiptError):self.verify(record)
        original=self.pred.path.read_bytes();self.pred.path.write_bytes(original.replace(b"10.25",b"11.25"))
        with self.assertRaises(ReceiptError):self.verify()

    def test_exact_schema_duplicate_keys_hidden_phase_and_bad_unicode_are_rejected(self):
        for key,value in [("phase","final_refit"),("schema_version","wrong"),("unexpected","secret")]:
            record=self.record.copy();record[key]=value
            with self.assertRaises(ReceiptError):self.verify(record)
        raw=json.dumps(self.record,separators=(",",":")).encode()
        duplicate=raw[:-1]+b',"phase":"dev"}'
        for data in [duplicate,b'[]',b'\xff',b' '*8193]:
            receipt=self.bind("bad.json",data)
            with self.assertRaises(ReceiptError):verify_dev_receipt(receipt,self.expected,self.pred,self.ids,self.targets)

if __name__=="__main__":unittest.main(verbosity=2)
