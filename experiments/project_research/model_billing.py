"""Bounded OpenRouter preparation probes and raw-invoice validation.

This module does not qualify an autonomous campaign or alter credentials/accounts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path
from typing import Callable

from .contracts import utc_now, write_new
from .state import AdmissionError, Store

API_ROOT = "https://openrouter.ai/api/v1"
ALLOCATION_RATE = 2000
PROBE_RESERVATION_KRW = 100
PROBE_OUTPUT_TOKENS = 128
PROBE_INPUT_TOKEN_ALLOWANCE = 4096
PROBE_TEXT = "Reply with the literal text BILLING_OK. Do not call any tools."
SUBSCRIPTION_SOURCE = "https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-personal-plans"
CODEX_USAGE_URL = "https://chatgpt.com/backend-api/wham/usage"
ANTHROPIC_USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
ANTHROPIC_SOURCE = "https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan"


class BillingError(ValueError):
    pass


@dataclass(frozen=True)
class ModelSpec:
    model: str
    provider_tag: str
    provider_name: str
    dated_alias: str
    prompt_usd_per_million: int = 2
    completion_usd_per_million: int = 10


SPECS = (
    ModelSpec("openai/gpt-5.6-sol", "openai", "OpenAI", "openai/gpt-5.6-sol-20260709"),
    ModelSpec("anthropic/claude-sonnet-5", "anthropic", "Anthropic", "anthropic/claude-sonnet-5-20260630"),
)


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: dict[str, object]
    response_sha256: str


Transport = Callable[[str, str, dict[str, object] | None], HttpResult]


def amount(value: object, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise BillingError(f"{field} missing or not numeric")
    try:
        number = Decimal(str(value))
    except InvalidOperation as error:
        raise BillingError(f"{field} not decimal") from error
    if not number.is_finite() or number < 0:
        raise BillingError(f"{field} negative or nonfinite")
    return number


def allocate_krw(cost_usd: object) -> int:
    return int((amount(cost_usd, "usage.cost") * ALLOCATION_RATE).to_integral_value(rounding=ROUND_CEILING))


def invoice_from_response(body: dict[str, object], requested_model: str,
                          response_sha256: str) -> dict[str, object]:
    usage = body.get("usage")
    if not isinstance(usage, dict):
        raise BillingError("raw usage object missing")
    cost = amount(usage.get("cost"), "usage.cost")
    for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
        if type(usage.get(field)) is not int or usage[field] < 0:
            raise BillingError(f"{field} missing or invalid")
    if usage["prompt_tokens"] + usage["completion_tokens"] != usage["total_tokens"]:
        raise BillingError("native token arithmetic mismatch")
    for field in ("id", "model", "provider"):
        if not isinstance(body.get(field), str) or not body[field].strip():
            raise BillingError(f"raw response {field} missing")
    if not re.fullmatch(r"[a-f0-9]{64}", response_sha256):
        raise BillingError("raw response hash missing")
    return {
        "source": "openrouter.raw_usage.cost", "generation_id": body["id"],
        "requested_model": requested_model, "returned_model": body["model"], "provider": body["provider"],
        "usage": usage, "cost_usd": str(cost), "accounting_rate_krw_per_usd": ALLOCATION_RATE,
        "allocation_krw": allocate_krw(cost), "response_sha256": response_sha256,
        "allocation_note": "Conservative budget allocation rate, not a quoted foreign-exchange rate.",
    }


def probe_payload(spec: ModelSpec) -> dict[str, object]:
    if spec not in SPECS or len(PROBE_TEXT.encode()) > 128:
        raise BillingError("probe definition outside qualified preparation scope")
    upper_usd = (Decimal(PROBE_INPUT_TOKEN_ALLOWANCE) * spec.prompt_usd_per_million
                 + Decimal(PROBE_OUTPUT_TOKENS) * spec.completion_usd_per_million) / 1_000_000
    if allocate_krw(upper_usd) > PROBE_RESERVATION_KRW:
        raise BillingError("probe reservation does not cover declared token/price bound")
    return {
        "model": spec.model, "messages": [{"role": "user", "content": PROBE_TEXT}],
        "max_tokens": PROBE_OUTPUT_TOKENS, "stream": False,
        "provider": {"only": [spec.provider_tag], "order": [spec.provider_tag],
                     "allow_fallbacks": False, "require_parameters": True,
                     "max_price": {"prompt": spec.prompt_usd_per_million,
                                   "completion": spec.completion_usd_per_million, "request": 0}},
    }


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def private_transport(auth_path: Path) -> Transport:
    try:
        credential = json.loads(auth_path.read_text())["openrouter"]["key"]
        if not isinstance(credential, str) or not credential.strip():
            raise ValueError("missing key")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise BillingError("OPENROUTER_CREDENTIAL_UNAVAILABLE") from error
    opener = urllib.request.build_opener(NoRedirect)

    def send(method: str, path: str, payload: dict[str, object] | None) -> HttpResult:
        if (method, path) not in {("GET", "/models"), ("GET", "/credits"), ("POST", "/chat/completions")}:
            raise BillingError("transport route outside bounded qualification")
        data = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode() if payload is not None else None
        request = urllib.request.Request(API_ROOT + path, data=data, method=method,
            headers={"Authorization": "Bearer " + credential, "Content-Type": "application/json"})
        try:
            response = opener.open(request, timeout=45)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            response_limit = 8 * 1048576 if path == "/models" else 1048576
            raw = response.read(response_limit + 1)
            if len(raw) > response_limit:
                raise BillingError("bounded provider response exceeded")
            status = response.status
        try:
            body = json.loads(raw)
        except (ValueError, UnicodeError) as error:
            raise BillingError("provider response is not JSON") from error
        if not isinstance(body, dict):
            raise BillingError("provider response is not an object")
        # Retain only credential-free response data, never request headers.
        sanitized = json.loads(json.dumps(body, allow_nan=False).replace(credential, "[REDACTED]"))
        return HttpResult(status, sanitized, hashlib.sha256(raw).hexdigest())

    return send


def credit_snapshot(result: HttpResult) -> dict[str, object]:
    if result.status != 200 or not isinstance(result.body.get("data"), dict):
        raise BillingError("CREDIT_BALANCE_UNAVAILABLE")
    data = result.body["data"]
    total = amount(data.get("total_credits"), "total_credits")
    used = amount(data.get("total_usage"), "total_usage")
    return {"endpoint": API_ROOT + "/credits", "http_status": result.status,
            "total_credits_usd": str(total), "total_usage_usd": str(used),
            "remaining_usd": str(total - used), "response_sha256": result.response_sha256,
            "observed_at": utc_now()}


def safe_subscription_snapshot(body: dict[str, object], status: int,
                               response_sha256: str) -> dict[str, object]:
    result: dict[str, object] = {"schema_version": "project-research-codex-subscription-snapshot/v1",
        "endpoint": CODEX_USAGE_URL, "http_status": status, "observed_at": utc_now(),
        "response_sha256": response_sha256, "official_source_url": SUBSCRIPTION_SOURCE,
        "status": "UNKNOWN", "eligible_for_included_zero_allocation": False,
        "scope": "Current included allowance and extra-credit state; not a provider invoice or permanent billing guarantee."}
    try:
        if status != 200 or not re.fullmatch(r"[a-f0-9]{64}", response_sha256):
            raise BillingError("subscription usage endpoint unavailable")
        plan = body.get("plan_type")
        if plan not in {"plus", "pro"}:
            raise BillingError("personal included-plan scope not established")
        limit, credits = body.get("rate_limit"), body.get("credits")
        if not isinstance(limit, dict) or not isinstance(credits, dict):
            raise BillingError("subscription rate-limit or credits fields missing")
        allowed, reached = limit.get("allowed"), limit.get("limit_reached")
        if type(allowed) is not bool or type(reached) is not bool:
            raise BillingError("subscription admission flags missing")
        windows: dict[str, dict[str, object]] = {}
        for name in ("primary_window", "secondary_window"):
            window = limit.get(name)
            if not isinstance(window, dict):
                raise BillingError(f"{name} missing")
            used = window.get("used_percent")
            if isinstance(used, bool) or not isinstance(used, (int, float)) or not math.isfinite(used) or not 0 <= used <= 100:
                raise BillingError(f"{name} usage missing or invalid")
            safe_window = {"used_percent": used}
            for key in ("limit_window_seconds", "reset_at", "reset_after_seconds"):
                value = window.get(key)
                if type(value) is not int or value < 0:
                    raise BillingError(f"{name} {key} missing or invalid")
                safe_window[key] = value
            if safe_window["limit_window_seconds"] == 0:
                raise BillingError(f"{name} interval invalid")
            windows[name] = safe_window
        has_credits, unlimited = credits.get("has_credits"), credits.get("unlimited")
        if type(has_credits) is not bool or type(unlimited) is not bool:
            raise BillingError("extra-credit flags missing")
        balance = amount(credits.get("balance"), "credits.balance")
        result.update({"plan": plan, "rate_limit": {"allowed": allowed, "limit_reached": reached, **windows},
                       "credits": {"has_credits": has_credits, "unlimited": unlimited, "balance": str(balance)}})
        if not allowed or reached or any(window["used_percent"] >= 100 for window in windows.values()):
            raise BillingError("included subscription allowance exhausted or disallowed")
        if has_credits or unlimited or balance != 0:
            raise BillingError("extra-credit availability prevents this zero-additional allocation basis")
        result["status"] = "AVAILABLE_INCLUDED_ONLY"
        result["eligible_for_included_zero_allocation"] = True
    except BillingError as error:
        result["reason"] = str(error)
    return result


def codex_subscription_snapshot(auth_path: Path) -> dict[str, object]:
    """One read-only request using the existing OAuth credential without mutation."""
    try:
        auth = json.loads(Path(auth_path).read_text())["openai-codex"]
        if auth.get("type") != "oauth" or not all(isinstance(auth.get(key), str) and auth[key] for key in ("access", "accountId")):
            raise BillingError("CODEX_OAUTH_UNAVAILABLE")
        request = urllib.request.Request(CODEX_USAGE_URL, method="GET", headers={
            "Authorization": "Bearer " + auth["access"], "chatgpt-account-id": auth["accountId"],
            "originator": "pi", "User-Agent": "prime-agent-readonly-usage-qualification",
        })
        opener = urllib.request.build_opener(NoRedirect)
        try:
            response = opener.open(request, timeout=30)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read(262145)
            status = response.status
        if len(raw) > 262144:
            raise BillingError("CODEX_USAGE_RESPONSE_OVERSIZE")
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise BillingError("CODEX_USAGE_SHAPE_INVALID")
        return safe_subscription_snapshot(value, status, hashlib.sha256(raw).hexdigest())
    except Exception as error:
        return {"schema_version": "project-research-codex-subscription-snapshot/v1",
                "endpoint": CODEX_USAGE_URL, "observed_at": utc_now(), "official_source_url": SUBSCRIPTION_SOURCE,
                "status": "UNKNOWN", "eligible_for_included_zero_allocation": False,
                "reason": str(error) if isinstance(error, BillingError) else type(error).__name__}


def included_subscription_allocation(before: dict[str, object], after: dict[str, object],
                                     usage_receipt: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = {"status": "UNKNOWN", "actual_krw": None,
        "basis": "INCLUDED_SUBSCRIPTION_ENTITLEMENT_NOT_PROVIDER_INVOICE",
        "official_source_url": SUBSCRIPTION_SOURCE, "before": before, "after": after}
    try:
        for snapshot in (before, after):
            if snapshot.get("status") != "AVAILABLE_INCLUDED_ONLY" or snapshot.get("eligible_for_included_zero_allocation") is not True:
                raise BillingError("included-subscription eligibility missing before or after request")
            if not re.fullmatch(r"[a-f0-9]{64}", str(snapshot.get("response_sha256", ""))):
                raise BillingError("trusted entitlement response hash missing")
            verified = safe_subscription_snapshot({"plan_type": snapshot.get("plan"),
                "rate_limit": snapshot.get("rate_limit"), "credits": snapshot.get("credits")},
                snapshot.get("http_status"), snapshot["response_sha256"])
            if verified["eligible_for_included_zero_allocation"] is not True:
                raise BillingError("entitlement fields failed revalidation")
            limit, credits = snapshot.get("rate_limit"), snapshot.get("credits")
            if (not isinstance(limit, dict) or not isinstance(credits, dict) or limit.get("allowed") is not True
                    or limit.get("limit_reached") is not False or credits.get("has_credits") is not False
                    or credits.get("unlimited") is not False or amount(credits.get("balance"), "credits.balance") != 0):
                raise BillingError("included-subscription fields contradict eligibility")
        for name in ("primary_window", "secondary_window"):
            first, last = before["rate_limit"][name], after["rate_limit"][name]
            if (first["reset_at"] != last["reset_at"] or first["limit_window_seconds"] != last["limit_window_seconds"]
                    or not 0 <= first["used_percent"] <= last["used_percent"] < 100):
                raise BillingError("usage window reset, exhausted, or changed unexpectedly")
        if before.get("plan") != after.get("plan"):
            raise BillingError("subscription plan changed during request")
        native = usage_receipt.get("native")
        if (usage_receipt.get("usage_status") != "OBSERVED" or usage_receipt.get("network_requests") != 1
                or usage_receipt.get("stop_reason") not in {"stop", "length", "toolUse"} or not isinstance(native, dict)):
            raise BillingError("successful observed native terminal usage missing")
        for name in ("input", "output", "cacheRead", "cacheWrite", "totalTokens"):
            if type(native.get(name)) is not int or native[name] < 0:
                raise BillingError("native token observation invalid")
        if native["totalTokens"] <= 0 or sum(native[name] for name in ("input", "output", "cacheRead", "cacheWrite")) != native["totalTokens"]:
            raise BillingError("native token arithmetic mismatch")
        result.update({"status": "KNOWN_ZERO_INCLUDED_SUBSCRIPTION", "actual_krw": 0,
                       "native_tokens": {name: native[name] for name in ("input", "output", "cacheRead", "cacheWrite", "totalTokens")},
                       "scope": "Successful observed request remained within both unchanged included-allowance windows; extra credits unavailable in both observations. SDK cost estimates were not used."})
    except (BillingError, KeyError, TypeError) as error:
        result["reason"] = str(error) if isinstance(error, BillingError) else "incomplete entitlement windows"
    return result


def safe_anthropic_snapshot(body: dict[str, object], status: int, response_sha256: str) -> dict[str, object]:
    """Trusted included-allowance view of the Claude subscription usage endpoint."""
    result: dict[str, object] = {"schema_version": "project-research-anthropic-subscription-snapshot/v1",
        "endpoint": ANTHROPIC_USAGE_URL, "http_status": status, "observed_at": utc_now(),
        "response_sha256": response_sha256, "official_source_url": ANTHROPIC_SOURCE,
        "status": "UNKNOWN", "eligible_for_included_zero_allocation": False,
        "scope": "Current included allowance and extra-usage state; not a provider invoice or permanent billing guarantee."}
    try:
        if status != 200 or not re.fullmatch(r"[a-f0-9]{64}", response_sha256):
            raise BillingError("subscription usage endpoint unavailable")
        windows: dict[str, dict[str, object]] = {}
        for name in ("five_hour", "seven_day"):
            window = body.get(name)
            if not isinstance(window, dict):
                raise BillingError(f"{name} missing")
            used = window.get("utilization")
            if isinstance(used, bool) or not isinstance(used, (int, float)) or not math.isfinite(used) or not 0 <= used <= 100:
                raise BillingError(f"{name} utilization missing or invalid")
            resets = window.get("resets_at")
            if used > 0 and (not isinstance(resets, str) or not resets):
                raise BillingError(f"{name} reset time missing")
            if window.get("locked_reason") is not None:
                raise BillingError(f"{name} locked: {window.get('locked_reason')}")
            windows[name] = {"utilization": float(used), "resets_at": resets if isinstance(resets, str) else None}
        extra = body.get("extra_usage")
        if not isinstance(extra, dict) or type(extra.get("is_enabled")) is not bool:
            raise BillingError("extra-usage state missing")
        used_credits = amount(extra.get("used_credits", 0), "extra_usage.used_credits")
        result.update({"rate_limit": windows, "extra_usage": {"is_enabled": extra["is_enabled"], "used_credits": str(used_credits),
                                                              "disabled_reason": extra.get("disabled_reason")}})
        if any(window["utilization"] >= 100 for window in windows.values()):
            raise BillingError("included subscription allowance exhausted")
        if extra["is_enabled"] or used_credits != 0:
            raise BillingError("extra-usage credits enabled; zero-additional allocation basis unavailable")
        result["status"] = "AVAILABLE_INCLUDED_ONLY"
        result["eligible_for_included_zero_allocation"] = True
    except BillingError as error:
        result["reason"] = str(error)
    return result


ANTHROPIC_USAGE_CACHE_SECONDS = 240.0
_anthropic_usage_cache: dict[str, object] = {}


def anthropic_subscription_snapshot(auth_path: Path, *, max_age: float = ANTHROPIC_USAGE_CACHE_SECONDS) -> dict[str, object]:
    """Read-only entitlement view; the endpoint rate-limits bursts with retry-after ~220 s.

    A recent trusted observation is reused within max_age so per-request guards do not
    exhaust the usage endpoint; a cache file carries the last observation across host
    processes. Cached views are marked so settlement can record their age.
    """
    cache_path = Path(auth_path).with_name(".argo-anthropic-usage-cache.json")
    cached = _read_usage_cache(cache_path)
    now = time.time()
    if cached and cached.get("status") == "AVAILABLE_INCLUDED_ONLY" and now - float(cached.get("observed_epoch", 0)) <= max_age:
        return {**cached, "cached": True, "cache_age_seconds": now - float(cached["observed_epoch"])}
    snapshot = _anthropic_snapshot_once(auth_path)
    if snapshot.get("http_status") == 429:
        retry_after = snapshot.get("retry_after_seconds")
        if cached and cached.get("status") == "AVAILABLE_INCLUDED_ONLY" and now - float(cached.get("observed_epoch", 0)) <= max_age + float(retry_after or 0):
            return {**cached, "cached": True, "cache_age_seconds": now - float(cached["observed_epoch"]), "live_status": 429}
    if snapshot.get("status") == "AVAILABLE_INCLUDED_ONLY":
        _write_usage_cache(cache_path, {**snapshot, "observed_epoch": time.time()})
    return snapshot


def _read_usage_cache(path: Path) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else None
    except (OSError, ValueError):
        return None


def _write_usage_cache(path: Path, value: dict[str, object]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(json.dumps(value, allow_nan=False) + "\n")
        temporary.chmod(0o600)
        temporary.replace(path)
    except OSError:
        pass


def _anthropic_snapshot_once(auth_path: Path) -> dict[str, object]:
    try:
        auth = json.loads(Path(auth_path).read_text())["anthropic"]
        if auth.get("type") != "oauth" or not isinstance(auth.get("access"), str) or not auth["access"]:
            raise BillingError("ANTHROPIC_OAUTH_UNAVAILABLE")
        expires = auth.get("expires")
        if type(expires) is not int or expires <= int(time.time() * 1000):
            raise BillingError("ANTHROPIC_OAUTH_EXPIRED")
        request = urllib.request.Request(ANTHROPIC_USAGE_URL, method="GET", headers={
            "Authorization": "Bearer " + auth["access"], "anthropic-beta": "oauth-2025-04-20",
            "User-Agent": "prime-agent-readonly-usage-qualification",
        })
        opener = urllib.request.build_opener(NoRedirect)
        try:
            response = opener.open(request, timeout=30)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read(262145)
            status = response.status
            retry_after = response.headers.get("retry-after")
        if len(raw) > 262144:
            raise BillingError("ANTHROPIC_USAGE_RESPONSE_OVERSIZE")
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise BillingError("ANTHROPIC_USAGE_SHAPE_INVALID")
        snapshot = safe_anthropic_snapshot(value, status, hashlib.sha256(raw).hexdigest())
        if status == 429 and isinstance(retry_after, str) and retry_after.isdecimal():
            snapshot["retry_after_seconds"] = int(retry_after)
        return snapshot
    except Exception as error:
        return {"schema_version": "project-research-anthropic-subscription-snapshot/v1",
                "endpoint": ANTHROPIC_USAGE_URL, "observed_at": utc_now(), "official_source_url": ANTHROPIC_SOURCE,
                "status": "UNKNOWN", "eligible_for_included_zero_allocation": False,
                "reason": str(error) if isinstance(error, BillingError) else type(error).__name__}


def anthropic_included_allocation(before: dict[str, object], after: dict[str, object],
                                  usage_receipt: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = {"status": "UNKNOWN", "actual_krw": None,
        "basis": "INCLUDED_SUBSCRIPTION_ENTITLEMENT_NOT_PROVIDER_INVOICE",
        "official_source_url": ANTHROPIC_SOURCE, "before": before, "after": after}
    try:
        for snapshot in (before, after):
            if snapshot.get("status") != "AVAILABLE_INCLUDED_ONLY" or snapshot.get("eligible_for_included_zero_allocation") is not True:
                raise BillingError("included-subscription eligibility missing before or after request")
            if not re.fullmatch(r"[a-f0-9]{64}", str(snapshot.get("response_sha256", ""))):
                raise BillingError("trusted entitlement response hash missing")
            extra = snapshot.get("extra_usage")
            if not isinstance(extra, dict) or extra.get("is_enabled") is not False or amount(extra.get("used_credits"), "used_credits") != 0:
                raise BillingError("extra-usage state contradicts eligibility")
        for name in ("five_hour", "seven_day"):
            first, last = before["rate_limit"][name], after["rate_limit"][name]
            if not 0 <= last["utilization"] < 100:
                raise BillingError("included allowance exhausted after request")
            if first["resets_at"] == last["resets_at"] and first["utilization"] > last["utilization"]:
                raise BillingError("utilization decreased inside one window; entitlement view inconsistent")
            if first["resets_at"] != last["resets_at"]:
                result.setdefault("window_rollovers", []).append(name)
        # The extra-usage counter is cumulative, so zero after the request evidences no paid consumption.
        result.update({"status": "KNOWN_ZERO_INCLUDED_SUBSCRIPTION", "actual_krw": 0,
                       "scope": "Extra usage disabled and cumulative used_credits zero before and after; included allowance not exhausted. SDK cost estimates were not used.",
                       "observation_freshness": {name: {"cached": bool(snapshot.get("cached")), "age_seconds": snapshot.get("cache_age_seconds")} for name, snapshot in (("before", before), ("after", after))}})
        native = usage_receipt.get("native")
        if (usage_receipt.get("usage_status") != "OBSERVED" or usage_receipt.get("network_requests") != 1
                or usage_receipt.get("stop_reason") not in {"stop", "length", "toolUse"} or not isinstance(native, dict)):
            result["native_tokens"] = "UNOBSERVED"
            result["token_scope"] = "Token usage was not observed for this request; only the zero additional charge is evidenced."
            return result
        for name in ("input", "output", "cacheRead", "cacheWrite", "totalTokens"):
            if type(native.get(name)) is not int or native[name] < 0:
                raise BillingError("native token observation invalid")
        if native["totalTokens"] <= 0 or sum(native[name] for name in ("input", "output", "cacheRead", "cacheWrite")) != native["totalTokens"]:
            raise BillingError("native token arithmetic mismatch")
        result["native_tokens"] = {name: native[name] for name in ("input", "output", "cacheRead", "cacheWrite", "totalTokens")}
    except (BillingError, KeyError, TypeError, InvalidOperation) as error:
        result.update({"status": "UNKNOWN", "actual_krw": None})
        result["reason"] = str(error) if isinstance(error, BillingError) else "incomplete entitlement windows"
    return result


def qualify(store: Store, project: str, send: Transport, *, execute_probes: bool = False) -> dict[str, object]:
    report: dict[str, object] = {
        "schema_version": "project-research-model-billing-qualification/v1", "created_at": utc_now(),
        "scope": "PREPARATION_ONLY", "autonomous_campaign": False, "scientific_run": False,
        "project_id": project, "budget_phase": "first_week", "maximum_generation_requests": 2,
        "per_request_reservation_krw": PROBE_RESERVATION_KRW, "maximum_probe_allocation_krw": 200,
        "accounting_rate_krw_per_usd": ALLOCATION_RATE,
        "catalog_models": [], "attempts": [], "generation_requests_sent": 0,
        "charged_allocation_krw": 0, "charged_allocation_basis": "No generation requests sent yet.",
        "generation_qualification": "UNQUALIFIED", "credentials_modified": False,
    }
    catalog = send("GET", "/models", None)
    if catalog.status != 200 or not isinstance(catalog.body.get("data"), list):
        report["status"] = "BLOCKED_MODEL_CATALOG_UNAVAILABLE"
        return report
    registered = {item["id"]: item for item in catalog.body["data"] if isinstance(item, dict) and isinstance(item.get("id"), str)}
    for spec in SPECS:
        model = registered.get(spec.model)
        if model is None:
            report["status"] = "BLOCKED_REQUESTED_MODEL_UNAVAILABLE"
            report["missing_model"] = spec.model
            return report
        pricing = model.get("pricing")
        try:
            if not isinstance(pricing, dict):
                raise BillingError("model pricing missing")
            if (amount(pricing.get("prompt"), "pricing.prompt") * 1_000_000 > spec.prompt_usd_per_million
                    or amount(pricing.get("completion"), "pricing.completion") * 1_000_000 > spec.completion_usd_per_million):
                raise BillingError("current model pricing exceeds fixed provider price limits")
        except BillingError as error:
            report["status"] = "BLOCKED_MODEL_PRICE_UNQUALIFIED"
            report["blocker"] = str(error)
            return report
        report["catalog_models"].append({**asdict(spec), "pricing": model.get("pricing"),
                                         "context_length": model.get("context_length"),
                                         "supported_parameters": model.get("supported_parameters"),
                                         "catalog_response_sha256": catalog.response_sha256,
                                         "generation_status": "NOT_CALLED"})
    try:
        credits = credit_snapshot(send("GET", "/credits", None))
    except BillingError as error:
        report["status"] = "BLOCKED_CREDIT_BALANCE_UNKNOWN"
        report["blocker"] = str(error)
        return report
    report["credits"] = credits
    remaining = Decimal(credits["remaining_usd"])
    reservation_usd = Decimal(PROBE_RESERVATION_KRW) / ALLOCATION_RATE
    if remaining < reservation_usd:
        report["status"] = "BLOCKED_INSUFFICIENT_CREDITS"
        report["blocker"] = "Available credits do not cover even the first bounded reservation; no generation request sent."
        return report
    if not execute_probes:
        report["status"] = "PREFLIGHT_ONLY_NO_GENERATION"
        return report
    for spec in SPECS:
        request_id = "model-billing-probe-20260909-" + spec.model.replace("/", "-")
        payload = probe_payload(spec)
        if any(entry["id"] == request_id for entry in store.snapshot()["charges"]):
            report["status"] = "BLOCKED_PROBE_ALREADY_ATTEMPTED"
            report["blocker"] = "A persisted reservation or receipt exists; do not repeat this generation."
            break
        if remaining < reservation_usd:
            report["status"] = "BLOCKED_INSUFFICIENT_CREDITS"
            break
        try:
            store.reserve_charge(request_id, project, "first_week", PROBE_RESERVATION_KRW)
        except (AdmissionError, sqlite3.IntegrityError) as error:
            report["status"] = "BLOCKED_LEDGER_ADMISSION"
            report["blocker"] = str(error)
            break
        attempt: dict[str, object] = {"request_id": request_id, "model": spec.model,
                                    "request": payload, "reservation_krw": PROBE_RESERVATION_KRW}
        report["attempts"].append(attempt)
        report["generation_requests_sent"] += 1
        try:
            response = send("POST", "/chat/completions", payload)
            attempt["http_status"] = response.status
            attempt["response_sha256"] = response.response_sha256
            if response.status != 200:
                raise BillingError(f"HTTP_{response.status}_NO_VERIFIED_INVOICE")
            invoice = invoice_from_response(response.body, spec.model, response.response_sha256)
            attempt["provider_invoice"] = invoice
            actual = invoice["allocation_krw"]
            store.settle_charge(request_id, actual, {"scope": "PREPARATION_ONLY", "provider_invoice": invoice})
            attempt["actual_krw"] = actual
            report["charged_allocation_krw"] += actual
            report["charged_allocation_basis"] = "Sum of individually rounded raw usage.cost allocations."
            remaining -= Decimal(invoice["cost_usd"])
            route_matches = (invoice["returned_model"] in (spec.model, spec.dated_alias)
                             and invoice["provider"] == spec.provider_name)
            tokens_bounded = (invoice["usage"]["prompt_tokens"] <= PROBE_INPUT_TOKEN_ALLOWANCE
                              and invoice["usage"]["completion_tokens"] <= PROBE_OUTPUT_TOKENS
                              and invoice["usage"]["total_tokens"] > 0)
            choices = response.body.get("choices")
            attempt["output"] = choices if isinstance(choices, list) else None
            if actual > PROBE_RESERVATION_KRW:
                attempt["status"] = "UNKNOWN_RESERVATION_EXCEEDED"
                report["status"] = "BLOCKED_BILLING_BOUND_EXCEEDED"
                break
            if not route_matches or not tokens_bounded:
                attempt["status"] = "BILLED_ROUTE_OR_TOKEN_BOUND_MISMATCH"
                report["status"] = "BLOCKED_QUALIFICATION_MISMATCH"
                break
            attempt["status"] = "QUALIFIED_RAW_HTTP_BILLING"
        except Exception as error:
            attempt["status"] = "UNKNOWN"
            attempt["blocker"] = str(error) if isinstance(error, BillingError) else type(error).__name__
            store.settle_charge(request_id, None, {"scope": "PREPARATION_ONLY", "billing_status": "UNKNOWN",
                                                 "reason": attempt["blocker"], "http_status": attempt.get("http_status"),
                                                 "response_sha256": attempt.get("response_sha256")})
            report["charged_allocation_krw"] = None
            report["charged_allocation_basis"] = "Missing provider invoice; reservation retained, never defaulted to zero."
            report["status"] = "BLOCKED_BILLING_UNKNOWN"
            break
    else:
        report["status"] = "QUALIFIED_RAW_HTTP_BILLING"
        report["generation_qualification"] = "BOTH_FIXED_MODELS_RAW_HTTP_ONLY"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path.home() / ".local/share/argo-project-research-20260909"
    parser.add_argument("--store", type=Path, default=root / "control/state.sqlite")
    parser.add_argument("--project", default="development-wine")
    parser.add_argument("--auth", type=Path, default=Path.home() / ".prime/agent/auth.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute-probes", action="store_true")
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("qualification output exists; preserve the previous record")
    report = qualify(Store(args.store), args.project, private_transport(args.auth), execute_probes=args.execute_probes)
    write_new(args.output, report)
    print(json.dumps({"status": report["status"], "generation_requests_sent": report["generation_requests_sent"],
                      "charged_allocation_krw": report["charged_allocation_krw"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
