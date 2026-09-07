"""Strict bounded model-origin intent parsing. Does not grant execution/eligibility."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

HEX64 = re.compile(r"[0-9a-f]{64}")
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


class IntentError(ValueError):
    def __init__(self):
        super().__init__("INTENT_INVALID")


@dataclass(frozen=True)
class Intent:
    phase: str
    purpose: str
    solution_sha256: str
    intent_sha256: str
    parent_run_id: str | None = None
    selected_run_id: str | None = None


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise IntentError()
        result[key] = value
    return result


def _reject_constant(value):
    raise IntentError()


def parse_intent(data: bytes, actual_solution_sha256: str,
                 observed_dev_runs: frozenset[str]) -> Intent:
    if (not isinstance(data, bytes) or not 0 < len(data) <= 4096 or
            not isinstance(actual_solution_sha256, str) or HEX64.fullmatch(actual_solution_sha256) is None or
            not isinstance(observed_dev_runs, frozenset) or len(observed_dev_runs) > 4 or
            any(not isinstance(run, str) or UUID.fullmatch(run) is None for run in observed_dev_runs)):
        raise IntentError()
    try:
        obj = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object,
                         parse_constant=_reject_constant)
    except (ValueError, UnicodeError, RecursionError):
        raise IntentError() from None
    if (not isinstance(obj, dict) or obj.get("schema_version") != "argo-house-price-intent/v1" or
            not isinstance(obj.get("phase"), str) or obj.get("phase") not in {"dev", "final_refit"}):
        raise IntentError()
    phase = obj["phase"]
    parent_key = "parent_run_id" if phase == "dev" else "selected_run_id"
    if set(obj) != {"schema_version", "phase", "purpose", "solution_sha256", parent_key}:
        raise IntentError()
    purpose, code = obj["purpose"], obj["solution_sha256"]
    if not isinstance(purpose, str) or not purpose.strip() or "\x00" in purpose:
        raise IntentError()
    try:
        if len(purpose.encode("utf-8")) > 1024:
            raise IntentError()
    except UnicodeError:
        raise IntentError() from None
    if not isinstance(code, str) or HEX64.fullmatch(code) is None:
        raise IntentError()
    reference = obj[parent_key]
    if reference is not None and (not isinstance(reference, str) or reference not in observed_dev_runs):
        raise IntentError()
    if phase == "dev":
        if code != actual_solution_sha256:
            raise IntentError()
        return Intent(phase, purpose, code, hashlib.sha256(data).hexdigest(), parent_run_id=reference)
    if reference is None:
        raise IntentError()
    return Intent(phase, purpose, code, hashlib.sha256(data).hexdigest(), selected_run_id=reference)
