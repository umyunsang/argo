"""Billing/entitlement integrity fixtures; no network or paid model requests."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from experiments.project_research.contracts import make_contract
from experiments.project_research.model_billing import (
    BillingError, HttpResult, SPECS, allocate_krw, included_subscription_allocation,
    invoice_from_response, probe_payload, qualify, safe_subscription_snapshot,
)
from experiments.project_research.state import AdmissionError, Store


def response(body: dict[str, object], status: int = 200) -> HttpResult:
    return HttpResult(status, body, hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest())


def invoice(index: int = 0) -> dict[str, object]:
    spec = SPECS[index]
    return {"id": f"gen-fixture-{index}", "model": spec.model, "provider": spec.provider_name,
            "usage": {"prompt_tokens": 12, "completion_tokens": 6, "total_tokens": 18,
                      "cost": 0.00014, "cost_details": {"upstream_inference_cost": 999}},
            "choices": [{"message": {"role": "assistant", "content": "BILLING_OK"}, "finish_reason": "stop"}]}


def quota(used: int = 20) -> dict[str, object]:
    return {"plan_type": "pro", "account_id": "private-id-must-not-survive",
            "rate_limit": {"allowed": True, "limit_reached": False,
                "primary_window": {"used_percent": used, "limit_window_seconds": 18000, "reset_at": 20000, "reset_after_seconds": 1200},
                "secondary_window": {"used_percent": used, "limit_window_seconds": 604800, "reset_at": 600000, "reset_after_seconds": 10000}},
            "credits": {"has_credits": False, "unlimited": False, "balance": "0"}}


def native_usage() -> dict[str, object]:
    return {"native": {"input": 12, "output": 6, "cacheRead": 0, "cacheWrite": 0, "totalTokens": 18,
                       "cost": {"total": 20000}},
            "usage_status": "OBSERVED", "stop_reason": "stop", "network_requests": 1}


class RawInvoiceTests(unittest.TestCase):
    def test_raw_account_cost_is_used_and_upstream_estimate_is_ignored(self) -> None:
        found = invoice_from_response(invoice(), SPECS[0].model, "a" * 64)
        self.assertEqual(found["cost_usd"], "0.00014")
        self.assertEqual(found["allocation_krw"], 1)
        self.assertEqual(found["source"], "openrouter.raw_usage.cost")
        self.assertEqual(allocate_krw("0.05000001"), 101)
        self.assertEqual(allocate_krw("0"), 0)

    def test_missing_or_invalid_invoice_cannot_become_zero(self) -> None:
        for value in (None, True, -1, float("nan"), float("inf"), "not-money"):
            with self.subTest(value=value), self.assertRaises(BillingError):
                body = invoice()
                body["usage"]["cost"] = value
                invoice_from_response(body, SPECS[0].model, "a" * 64)
        body = invoice()
        del body["usage"]["cost"]
        with self.assertRaises(BillingError):
            invoice_from_response(body, SPECS[0].model, "a" * 64)
        body = invoice()
        body["usage"]["total_tokens"] = 100
        with self.assertRaises(BillingError):
            invoice_from_response(body, SPECS[0].model, "a" * 64)

    def test_payload_blocks_provider_fallback_and_limits_prices_and_output(self) -> None:
        for spec in SPECS:
            payload = probe_payload(spec)
            self.assertEqual(payload["max_tokens"], 128)
            self.assertEqual(payload["provider"]["only"], [spec.provider_tag])
            self.assertFalse(payload["provider"]["allow_fallbacks"])
            self.assertEqual(payload["provider"]["max_price"], {"prompt": 2, "completion": 10, "request": 0})
            self.assertNotIn("tools", payload)


class QualificationLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temporary.name) / "state.sqlite")
        self.store.append(make_contract("p", "wine", "B", False, "fixture-pool"))
        self.posts: list[dict[str, object]] = []

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def transport(self, credits: str = "1", fail_first: bool = False):
        def send(method, path, payload):
            if path == "/models":
                return response({"data": [{"id": spec.model, "pricing": {"prompt": "0.000002", "completion": "0.00001"}} for spec in SPECS]})
            if path == "/credits":
                return response({"data": {"total_credits": credits, "total_usage": "0.000255"}})
            charges = self.store.snapshot()["charges"]
            self.assertTrue(charges)
            self.assertEqual(charges[-1]["state"], "RESERVED")
            self.assertEqual(charges[-1]["reserved"], 100)
            self.posts.append(payload)
            if fail_first:
                return response({"error": {"code": 402}}, 402)
            return response(invoice(len(self.posts) - 1))
        return send

    def test_insufficient_credits_never_reserves_or_sends_generation(self) -> None:
        report = qualify(self.store, "p", self.transport("0"), execute_probes=True)
        self.assertEqual(report["status"], "BLOCKED_INSUFFICIENT_CREDITS")
        self.assertEqual(report["generation_requests_sent"], 0)
        self.assertEqual(self.posts, [])
        self.assertEqual(self.store.snapshot()["charges"], [])

    def test_two_successes_are_each_reserved_then_settled_using_raw_invoice(self) -> None:
        report = qualify(self.store, "p", self.transport(), execute_probes=True)
        self.assertEqual(report["status"], "QUALIFIED_RAW_HTTP_BILLING")
        self.assertEqual(len(self.posts), 2)
        self.assertEqual(report["charged_allocation_krw"], 2)
        self.assertEqual([entry["state"] for entry in self.store.snapshot()["charges"]], ["SETTLED", "SETTLED"])
        repeated = qualify(self.store, "p", self.transport(), execute_probes=True)
        self.assertEqual(repeated["status"], "BLOCKED_PROBE_ALREADY_ATTEMPTED")
        self.assertEqual(len(self.posts), 2)

    def test_missing_invoice_blocks_second_request_and_future_store_admission(self) -> None:
        report = qualify(self.store, "p", self.transport(fail_first=True), execute_probes=True)
        self.assertEqual(report["status"], "BLOCKED_BILLING_UNKNOWN")
        self.assertEqual(len(self.posts), 1)
        self.assertIsNone(report["charged_allocation_krw"])
        charge = self.store.snapshot()["charges"][0]
        self.assertEqual(charge["state"], "UNKNOWN")
        self.assertIsNone(charge["actual"])
        with self.assertRaises(AdmissionError):
            self.store.reserve_charge("extra", "p", "first_week", 1)


class SubscriptionEntitlementTests(unittest.TestCase):
    def test_safe_receipt_excludes_private_fields_and_captures_both_windows(self) -> None:
        snapshot = safe_subscription_snapshot(quota(), 200, "a" * 64)
        self.assertEqual(snapshot["status"], "AVAILABLE_INCLUDED_ONLY")
        self.assertNotIn("private-id", json.dumps(snapshot))
        self.assertEqual(snapshot["rate_limit"]["secondary_window"]["used_percent"], 20)

    def test_known_zero_requires_two_eligible_windows_and_actual_native_usage(self) -> None:
        before = safe_subscription_snapshot(quota(20), 200, "a" * 64)
        after = safe_subscription_snapshot(quota(21), 200, "b" * 64)
        result = included_subscription_allocation(before, after, native_usage())
        self.assertEqual(result["status"], "KNOWN_ZERO_INCLUDED_SUBSCRIPTION")
        self.assertEqual(result["actual_krw"], 0)
        self.assertNotIn("cost", result["native_tokens"])
        missing = included_subscription_allocation(before, after, {})
        self.assertEqual(missing["status"], "UNKNOWN")
        self.assertIsNone(missing["actual_krw"])

    def test_exhaustion_credit_availability_missing_window_and_reset_stay_unknown(self) -> None:
        before = safe_subscription_snapshot(quota(20), 200, "a" * 64)
        bad_values = []
        exhausted = quota(100)
        bad_values.append(exhausted)
        credited = quota()
        credited["credits"]["has_credits"] = True
        bad_values.append(credited)
        missing = quota()
        del missing["rate_limit"]["secondary_window"]
        bad_values.append(missing)
        reset = quota(21)
        reset["rate_limit"]["primary_window"]["reset_at"] += 18000
        bad_values.append(reset)
        invalid_bool = quota(True)
        bad_values.append(invalid_bool)
        for bad in bad_values:
            with self.subTest(bad=bad):
                after = safe_subscription_snapshot(bad, 200, "b" * 64)
                result = included_subscription_allocation(before, after, native_usage())
                self.assertEqual(result["status"], "UNKNOWN")
                self.assertIsNone(result["actual_krw"])
        error = safe_subscription_snapshot({}, 401, "a" * 64)
        self.assertEqual(error["status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
