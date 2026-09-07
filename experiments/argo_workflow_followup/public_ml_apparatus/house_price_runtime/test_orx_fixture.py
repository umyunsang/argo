"""Inert fixture contract tests; never start the delayed cancellation case."""
from __future__ import annotations
import unittest
from orx_fixture import execute

class FixtureTest(unittest.TestCase):
    def test_three_fixed_modes_have_no_model_data_activity(self):
        for mode in ["success","failure","cancel"]:
            result=execute({"mode":mode,"nonce":"house-price-orx-native-fixture-v1"})
            self.assertEqual(result["mode"],mode)
            self.assertEqual(result["model_calls"]+result["ML_fits"]+result["hidden_scores"],0)
            self.assertEqual(len(result["fixture_code_sha256"]),64)
    def test_unknown_or_injected_config_rejected(self):
        for cfg in [None,{}, {"mode":"exec","nonce":"house-price-orx-native-fixture-v1"},
                    {"mode":"success","nonce":"wrong"},
                    {"mode":"success","nonce":"house-price-orx-native-fixture-v1","command":"sh"}]:
            with self.assertRaises(ValueError):execute(cfg)
if __name__ == "__main__":unittest.main(verbosity=2)
