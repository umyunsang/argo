#!/usr/bin/env python3
"""Reference-anchored analytic scoring with fail-closed selective evaluation.

Two ideas, both taken from reviewed prior work:

* Analytic rubric. Criteria are scored separately rather than in one holistic
  judgement, because agreement shifts with rubric form and single-call scoring
  invites halo (analytic_versus_holistic_rubric, judge_severity_halo_instability).
* Selective evaluation. A judge verdict is admitted only where a calibrated
  confidence threshold bounds disagreement with the human anchor; elsewhere the
  judge abstains and the item escalates (selective_evaluation_agreement_guarantee,
  risk_controlled_judging_threshold).

The anchor is the withheld target design of the source study, held by the
evaluator and never released into an episode workspace.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path


def wilson_upper(errors: int, n: int, delta: float = 0.05) -> float:
    """One-sided upper confidence bound on an error rate.

    The reviewed guarantee is stated at a risk level alpha *and* a significance
    level delta, so a threshold chosen on the empirical rate alone overfits the
    calibration sample. Selection uses this bound instead.
    """
    if n == 0:
        return 1.0
    z = 1.6449 if abs(delta - 0.05) < 1e-9 else abs(_probit(1 - delta))
    p = errors / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return min(1.0, (centre + margin) / denom)


def _probit(q: float) -> float:
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    pl, ph = 0.02425, 1 - 0.02425
    if q < pl:
        x = math.sqrt(-2 * math.log(q))
        return (((((c[0] * x + c[1]) * x + c[2]) * x + c[3]) * x + c[4]) * x + c[5]) / ((((d[0] * x + d[1]) * x + d[2]) * x + d[3]) * x + 1)
    if q > ph:
        x = math.sqrt(-2 * math.log(1 - q))
        return -(((((c[0] * x + c[1]) * x + c[2]) * x + c[3]) * x + c[4]) * x + c[5]) / ((((d[0] * x + d[1]) * x + d[2]) * x + d[3]) * x + 1)
    x = q - 0.5
    r = x * x
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * x / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def minimum_calibration_size(risk_level: float, delta: float = 0.05, max_n: int = 5000) -> int:
    """Smallest flawless calibration set that can certify the risk level."""
    for n in range(1, max_n + 1):
        if wilson_upper(0, n, delta) <= risk_level:
            return n
    return max_n


@dataclass
class Element:
    element_id: str
    requirement: str
    cues: list[str]

    def covered(self, text: str) -> bool:
        return any(re.search(c, text, re.I) for c in self.cues)


def load_checklist(path: Path) -> list[Element]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Element(e["element_id"], e["requirement"], e["cues"]) for e in raw["elements"]]


def coverage(text: str, checklist: list[Element]) -> dict:
    hits = {e.element_id: e.covered(text) for e in checklist}
    n = len(checklist)
    return {"elements": n, "covered": sum(hits.values()),
            "coverage_ratio": round(sum(hits.values()) / n, 3) if n else 0.0,
            "per_element": hits,
            "missed": sorted(k for k, v in hits.items() if not v)}


class SelectiveJudge:
    """Wraps a judge with an abstention rule that fails closed without calibration.

    A verdict is admitted only if its confidence is at least the calibrated
    threshold. The threshold may not be assumed: it must be derived from a
    labelled calibration set at a declared risk level, so an uncalibrated judge
    admits nothing.
    """

    def __init__(self, risk_level: float = 0.1, confidence_level: float = 0.95):
        self.risk_level = risk_level
        self.confidence_level = confidence_level
        self.threshold: float | None = None
        self.calibration_n = 0

    def calibrate(self, records: list[dict]) -> dict:
        """records: [{"confidence": float, "judge_verdict": x, "anchor_verdict": x}]"""
        if not records:
            return {"calibrated": False, "reason": "empty calibration set"}
        ordered = sorted(records, key=lambda r: -r["confidence"])
        best = None
        delta = 1 - self.confidence_level
        for i in range(1, len(ordered) + 1):
            kept = ordered[:i]
            errors = sum(1 for r in kept if r["judge_verdict"] != r["anchor_verdict"])
            if wilson_upper(errors, len(kept), delta) <= self.risk_level:
                best = kept[-1]["confidence"]
        if best is None:
            return {"calibrated": False,
                    "reason": "no threshold certifies the risk level at this confidence on this calibration set",
                    "minimum_flawless_calibration_size": minimum_calibration_size(self.risk_level, delta)}
        self.threshold = best
        self.calibration_n = len(records)
        coverage_at_t = sum(1 for r in records if r["confidence"] >= best) / len(records)
        return {"calibrated": True, "threshold": round(best, 4), "n": len(records),
                "risk_level": self.risk_level, "coverage": round(coverage_at_t, 3)}

    def decide(self, confidence: float, verdict):
        if self.threshold is None:
            return {"admitted": False, "reason": "judge is uncalibrated; no human-anchored calibration set exists"}
        if confidence < self.threshold:
            return {"admitted": False, "reason": "confidence below calibrated threshold", "escalate": True}
        return {"admitted": True, "verdict": verdict}
