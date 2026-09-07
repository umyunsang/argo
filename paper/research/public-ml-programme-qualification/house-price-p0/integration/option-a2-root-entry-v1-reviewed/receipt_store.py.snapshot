"""Bound trusted dev receipt bytes to independent execution facts and exact regrading.

This helper never reads lifecycle state from an agent field and never launches a run.
The bridge owns native ORX matching, private paths, and input manifest custody.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
import json
import re

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import (
    FileBinding, GradedArtifact, GradingError, grade_files, read_bound,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.trusted_io import DevResultReceipt


class ReceiptError(ValueError):
    def __init__(self):
        super().__init__("RECEIPT_INVALID")


@dataclass(frozen=True)
class ExpectedDevExecution:
    run_id: str
    experiment_id: str
    native_commit: str
    native_source_digest: str
    closure_sha256: str
    solution_sha256: str
    intent_sha256: str
    task_sha256: str
    environment_sha256: str
    protocol_sha256: str
    runner_sha256: str
    native_status: str
    rows: int


@dataclass(frozen=True)
class VerifiedDevReceipt:
    eligibility: DevResultReceipt
    score: GradedArtifact
    run_id: str

    def public_result(self) -> dict[str, object]:
        return {"run_id": self.run_id, "solution_sha256": self.eligibility.code_sha256,
                "valid": True, **self.score.public_metric()}


def _strict_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ReceiptError()
        obj[key] = value
    return obj


def _reject_constant(value):
    raise ReceiptError()


def _expected_values(expected: ExpectedDevExecution) -> dict[str, object]:
    if not isinstance(expected, ExpectedDevExecution) or expected.native_status != "DONE":
        raise ReceiptError()
    values = asdict(expected)
    values.pop("native_status")
    for field, value in values.items():
        if field == "rows":
            if type(value) is not int or not 1 <= value <= 292:
                raise ReceiptError()
        elif field in {"run_id", "experiment_id"}:
            if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", value) is None:
                raise ReceiptError()
        else:
            length = 40 if field == "native_commit" else 64
            if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{"+str(length)+r"}", value) is None:
                raise ReceiptError()
    return values


def verify_dev_receipt(receipt: FileBinding, expected: ExpectedDevExecution,
                       predictions: FileBinding, ids: FileBinding,
                       targets: FileBinding) -> VerifiedDevReceipt:
    values = _expected_values(expected)
    try:
        data = read_bound(receipt, 8192)
        obj = json.loads(data.decode("utf-8"), object_pairs_hook=_strict_object,
                         parse_constant=_reject_constant)
        fixed = {"schema_version":"argo-house-price-dev-receipt/v1", "phase":"dev",
                 **values, "prediction_sha256":predictions.sha256,
                 "prediction_bytes":predictions.bytes,
                 "prediction_mtime_ns_max":predictions.mtime_ns_max,
                 "ids_sha256":ids.sha256, "targets_sha256":targets.sha256}
        if not isinstance(obj, dict) or set(obj) != set(fixed) | {"mae_numerator", "mae_denominator"}:
            raise ReceiptError()
        for field, value in fixed.items():
            if type(obj[field]) is not type(value) or obj[field] != value:
                raise ReceiptError()
        for field in ["mae_numerator", "mae_denominator"]:
            value = obj[field]
            if not isinstance(value, str) or re.fullmatch(r"(?:0|[1-9][0-9]{0,255})", value) is None:
                raise ReceiptError()
        if obj["mae_denominator"] == "0":
            raise ReceiptError()
        stated = Fraction(int(obj["mae_numerator"]), int(obj["mae_denominator"]))
        score = grade_files(predictions, ids, targets, max_rows=expected.rows)
        if (score.row_count != expected.rows or stated != score.mae or
                obj["mae_numerator"] != str(score.mae.numerator) or
                obj["mae_denominator"] != str(score.mae.denominator)):
            raise ReceiptError()
    except (GradingError, ValueError, TypeError, AttributeError, UnicodeError, RecursionError):
        raise ReceiptError() from None
    return VerifiedDevReceipt(DevResultReceipt(receipt.sha256, expected.closure_sha256,
                                              expected.solution_sha256), score, expected.run_id)
