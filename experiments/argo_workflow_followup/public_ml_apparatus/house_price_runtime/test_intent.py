"""Strict model-origin intent parsing; no filesystem, provider or training."""
from __future__ import annotations
import hashlib
import json
import unittest

from intent import IntentError, parse_intent

CODE = hashlib.sha256(b"solution A").hexdigest()
RUN = "191407a0-84ce-47e6-afa4-298d034b8aa3"


def dev():
    return {"schema_version":"argo-house-price-intent/v1","phase":"dev",
            "purpose":"Compare a justified numeric baseline", "parent_run_id":None,
            "solution_sha256":CODE}


def encoded(obj):return json.dumps(obj,ensure_ascii=False,separators=(",",":")).encode()


class IntentTest(unittest.TestCase):
    def test_dev_matches_actual_code_and_parents_come_from_observed_runs(self):
        parsed = parse_intent(encoded(dev()), CODE, frozenset())
        self.assertEqual(parsed.phase,"dev");self.assertIsNone(parsed.parent_run_id)
        obj=dev();obj["parent_run_id"]=RUN
        self.assertEqual(parse_intent(encoded(obj),CODE,frozenset({RUN})).parent_run_id,RUN)
        with self.assertRaises(IntentError):parse_intent(encoded(obj),CODE,frozenset())
        with self.assertRaises(IntentError):parse_intent(encoded(dev()),"0"*64,frozenset())

    def test_final_can_select_older_run_without_recopying_current_code(self):
        obj={"schema_version":"argo-house-price-intent/v1","phase":"final_refit",
             "purpose":"Choose A using eligible dev evidence", "selected_run_id":RUN,
             "solution_sha256":CODE}
        parsed=parse_intent(encoded(obj),"0"*64,frozenset({RUN}))
        self.assertEqual(parsed.solution_sha256,CODE);self.assertEqual(parsed.selected_run_id,RUN)
        with self.assertRaises(IntentError):parse_intent(encoded(obj),CODE,frozenset())

    def test_exact_json_keys_duplicate_fields_and_injections_rejected(self):
        valid=encoded(dev())
        cases=[valid[:-1]+b',"phase":"final_refit"}',valid[:-1]+b',"command":"sh"}',
               valid.replace(b'"parent_run_id":null',b'"parent_run_id":1'),
               valid.replace(b'"purpose":"Compare a justified numeric baseline"',b'"purpose":NaN'),
               b'[]', b'{}', b'\xff',valid.replace(b'"phase":"dev"',b'"phase":"DEV"')]
        for data in cases:
            with self.subTest(data=data),self.assertRaisesRegex(IntentError,"^INTENT_INVALID$"):
                parse_intent(data,CODE,frozenset())
        for field in ["environment","model","scorer","split","max_runs"]:
            obj=dev();obj[field]="bad"
            with self.assertRaises(IntentError):parse_intent(encoded(obj),CODE,frozenset())

    def test_unhashable_nested_phase_is_safe_and_duplicate_guard_is_behavioral(self):
        for phase in [[], {}, ["dev"]]:
            obj=dev();obj["phase"]=phase
            with self.assertRaisesRegex(IntentError,"^INTENT_INVALID$"):
                parse_intent(encoded(obj),CODE,frozenset())
        same_phase=encoded(dev())[:-1]+b',"phase":"dev"}'
        with self.assertRaises(IntentError):parse_intent(same_phase,CODE,frozenset())

    def test_utf8_byte_bounds_and_own_bytes_digest_not_self_attestation(self):
        obj=dev();obj["purpose"]="가"*342
        with self.assertRaises(IntentError):parse_intent(encoded(obj),CODE,frozenset())
        obj["purpose"]="x\x00y"
        with self.assertRaises(IntentError):parse_intent(encoded(obj),CODE,frozenset())
        with self.assertRaises(IntentError):parse_intent(b" "*4097,CODE,frozenset())
        obj=dev();first=encoded(obj);second=json.dumps(obj,indent=2).encode()
        self.assertNotEqual(parse_intent(first,CODE,frozenset()).intent_sha256,
                            parse_intent(second,CODE,frozenset()).intent_sha256)
        self.assertEqual(parse_intent(first,CODE,frozenset()).intent_sha256,hashlib.sha256(first).hexdigest())

if __name__=="__main__":unittest.main(verbosity=2)
