"""Exact native return-code type in shared continuation receipt validation."""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.bridge import _valid_prior_process_receipt
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion import CompletionFixture

class PriorReceiptTypeTest(unittest.TestCase):
    def test_only_exact_integer_zero_proves_success(self):
        with tempfile.TemporaryDirectory(prefix="hp-shared-zero-") as temporary:
            fixture=CompletionFixture(Path(temporary))
            original=json.loads(fixture.process_receipt_path.read_bytes())
            self.assertTrue(_valid_prior_process_receipt(original,fixture.session_path))
            for value in (False,True,0.0,None,"0",[],{}):
                receipt=dict(original);receipt["returncode"]=value
                with self.subTest(value=value):self.assertFalse(_valid_prior_process_receipt(receipt,fixture.session_path))
            receipt=dict(original);receipt.pop("returncode")
            self.assertFalse(_valid_prior_process_receipt(receipt,fixture.session_path))
            self.assertEqual(list(fixture.paths["completion"].iterdir()),[])

if __name__=="__main__":unittest.main(verbosity=2)
