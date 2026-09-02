#!/usr/bin/env python3
"""Condition-blind scoring and judge calibration for Study A.

Three layers, in admission order:
  1. deterministic redlines   - programmatic, no model
  2. per-dimension rubric     - one call per dimension (halo control, RD-2026-09-02-09C)
  3. calibration diagnostics  - agreement, severity, halo against a human anchor

A judge is admissible only when calibration passes. Agreement alone is not
sufficient (judge_calibration_requirement). No scientific result is produced here.
"""
from __future__ import annotations

import json
import re
import statistics
from dataclasses import dataclass, field
from pathlib import Path

DIMENSIONS = ("main_comparison", "ablation", "analysis", "resources", "metrics", "uncertainty")

STRUCTURAL = {
    "names_ablation": re.compile(r"\b(ablat|hold[- ]out one|leave[- ]one[- ]out|remove the .{0,30}component)", re.I),
    "names_uncertainty": re.compile(r"\b(confidence interval|bootstrap|standard error|credible interval|permutation test|TOST|power analysis|mixed[- ]effects)\b", re.I),
    "names_concrete_resource": re.compile(r"\b(SWE-bench|GAIA|CORD-19|HotpotQA|MuSiQue|BM25|BGE|Claude|GPT-|Qwen|Llama|Gemini|ICML|ICLR|ACL)\b"),
    "names_primary_outcome": re.compile(r"\b(primary (outcome|endpoint|metric)|main (outcome|metric))\b", re.I),
    "states_stopping_or_falsifier": re.compile(r"\b(stopping rule|stop(ping)? criteri|falsif|would refute|null result)\b", re.I),
}

REDLINES = {
    "fabricated_resource": re.compile(r"\b(?:dataset|model|corpus)\s+`?(?:TBD|XXX|placeholder|unknown)`?", re.I),
    "unexecuted_number": re.compile(r"\b(?:accuracy|f1|score|pass@\d+)\s*[:=]\s*0?\.\d+", re.I),
    "post_outcome_change": re.compile(r"\b(?:after seeing|once we saw|given the result)\b.{0,60}\b(?:changed|switched|dropped)\b", re.I | re.S),
    "missing_control": re.compile(r"\bno\s+(?:control|baseline)\b", re.I),
}


@dataclass
class Episode:
    episode_id: str
    condition: str
    artifact_text: str


@dataclass
class Scored:
    episode_id: str
    redlines: list[str] = field(default_factory=list)
    dimensions: dict[str, float] = field(default_factory=dict)

    @property
    def total(self) -> float:
        return sum(self.dimensions.values())

    @property
    def fatal_error_free(self) -> bool:
        return not self.redlines and all(v > 0 for v in self.dimensions.values())


def run_redlines(text: str) -> list[str]:
    return sorted(name for name, rx in REDLINES.items() if rx.search(text))


def structural_gaps(text: str) -> list[str]:
    """Deterministic completeness checks.

    Added after the 2026-09-02 pilot, where fabrication redlines fired on 0 of 16
    real artifacts while these checks flagged 13 of 16. Specified on pilot
    artifacts, so pilot tasks are development data and are excluded from
    confirmation (RD-2026-09-02-10B).
    """
    return sorted(name for name, rx in STRUCTURAL.items() if not rx.search(text))


def state_use_report(state_text: str, design_text: str, field: str, scaffold_text: str) -> dict:
    """Manipulation check, respecified after the pilot (RD-2026-09-02-10A).

    Verbatim echo of the field name in the deliverable measured compliance, not
    use: 8 of 8 structured episodes filled the scaffold while 7 of 8 did not echo
    the name. Consumption is now evidenced by a filled field, and carry-through is
    reported separately as a weak secondary signal.
    """
    filled = state_text.strip() != scaffold_text.strip()
    value = ""
    for line in state_text.splitlines():
        if line.strip().startswith(field):
            value = line.split(":", 1)[1].strip() if ":" in line else ""
            break
    tokens = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", value)][:12]
    carried = sum(1 for w in set(tokens) if w in design_text.lower())
    return {
        "scaffold_filled": filled,
        "required_field_filled": bool(value),
        "field_value": value[:200],
        "carry_through_tokens": carried,
        "carry_through_ratio": round(carried / len(set(tokens)), 3) if tokens else 0.0,
        "verbatim_echo": field in design_text,
        "consumed": bool(filled and value),
    }


def score_episode(ep: Episode, dimension_scorer) -> Scored:
    """dimension_scorer(dimension, artifact_text) -> float in [0,5].

    Called once per dimension so that a single response cannot spread one
    impression across all dimensions.
    """
    fired = run_redlines(ep.artifact_text)
    dims = {}
    for d in DIMENSIONS:
        v = float(dimension_scorer(d, ep.artifact_text))
        if d in ("resources", "metrics") and fired:
            v = 0.0  # a fatal flaw zeroes the affected dimension
        dims[d] = v
    return Scored(ep.episode_id, fired, dims)


def _pearson(a, b) -> float:
    if len(a) < 2 or statistics.pstdev(a) == 0 or statistics.pstdev(b) == 0:
        return 0.0
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / len(a)
    return cov / (statistics.pstdev(a) * statistics.pstdev(b))


def calibration_report(judge_scores: dict[str, dict[str, float]],
                       human_scores: dict[str, dict[str, float]],
                       severity_tolerance: float = 0.5,  # half a point on the 0-5 dimension scale
                       halo_tolerance: float = 0.95) -> dict:
    """Agreement, severity, and halo against a human-anchored subset."""
    ids = sorted(set(judge_scores) & set(human_scores))
    j_tot = [sum(judge_scores[i].values()) for i in ids]
    h_tot = [sum(human_scores[i].values()) for i in ids]
    agreement = _pearson(j_tot, h_tot)
    # Severity is a rater location parameter on the item scale, so it is the mean
    # per-dimension difference, not the difference of 30-point totals.
    per_dim_diffs = [judge_scores[i][d] - human_scores[i][d] for i in ids for d in DIMENSIONS
                     if d in judge_scores[i] and d in human_scores[i]]
    severity = statistics.fmean(per_dim_diffs) if per_dim_diffs else 0.0
    dim_series = {d: [judge_scores[i][d] for i in ids] for d in DIMENSIONS if all(d in judge_scores[i] for i in ids)}
    pairs = [(_pearson(dim_series[a], dim_series[b]))
             for idx, a in enumerate(sorted(dim_series)) for b in sorted(dim_series)[idx + 1:]]
    halo = statistics.fmean(pairs) if pairs else 0.0
    failures = []
    if abs(severity) > severity_tolerance:
        failures.append(f"severity {severity:+.2f} exceeds tolerance {severity_tolerance}")
    if halo > halo_tolerance:
        failures.append(f"halo {halo:.2f} exceeds tolerance {halo_tolerance}")
    if agreement < 0.5:
        failures.append(f"agreement {agreement:.2f} below floor 0.50")
    return {"n": len(ids), "agreement": round(agreement, 4), "severity": round(severity, 4),
            "halo": round(halo, 4), "admissible": not failures, "failures": failures}


def write_report(path: Path, payload: dict) -> str:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path.name
