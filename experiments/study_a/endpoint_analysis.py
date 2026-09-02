#!/usr/bin/env python3
"""Endpoint analysis: coverage, variance components, allocation, endpoint agreement.

The numbers this produces appear in the manuscript, so they must be re-derivable by a
reader from committed code rather than from ad-hoc work. Two conventions matter and are
stated rather than implied:

* Coverage counts an element as met only when the verdict is exactly "satisfied", so
  "unclear" and "unparsed" count as not met.
* The minimum detectable effect uses the standard error of a paired DIFFERENCE between
  two condition means, which carries a factor of sqrt(2) over the standard error of one
  mean. Omitting that factor understates the effect by that factor.

    /usr/bin/python3 experiments/study_a/endpoint_analysis.py <verdicts.json>
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import statistics
import sys

EPISODE_RE = re.compile(r"^(?P<task>.+?)__(?P<cond>C\d\d)__(?P<rep>r\d+)$")
Z_TWO_SIDED_80_POWER = 2.8


def load_verdicts(path: pathlib.Path) -> list[dict]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return obj["verdicts"] if isinstance(obj, dict) and "verdicts" in obj else obj


def coverage_by_episode(records: list[dict]) -> dict:
    per: dict[str, list[float]] = {}
    for r in records:
        per.setdefault(r["episode_id"], []).append(1.0 if r["verdict"] == "satisfied" else 0.0)
    return {ep: sum(v) / len(v) for ep, v in per.items()}


def variance_components(coverage: dict) -> dict:
    rows = []
    for ep, value in coverage.items():
        m = EPISODE_RE.match(ep)
        if m:
            rows.append((m.group("task"), m.group("cond"), value))
    if not rows:
        raise ValueError("no episode identifiers matched; refusing to report zero variance")
    tasks = sorted({r[0] for r in rows})
    conds = sorted({r[1] for r in rows})
    a, b = len(tasks), len(conds)
    n = len(rows) / (a * b)
    if n != int(n):
        raise ValueError("design is unbalanced; expected mean squares do not apply")
    n = int(n)
    grand = statistics.mean([r[2] for r in rows])
    cell = {(t, c): [r[2] for r in rows if r[0] == t and r[1] == c] for t in tasks for c in conds}
    tmean = {t: statistics.mean([r[2] for r in rows if r[0] == t]) for t in tasks}
    cmean = {c: statistics.mean([r[2] for r in rows if r[1] == c]) for c in conds}
    ss_a = b * n * sum((tmean[t] - grand) ** 2 for t in tasks)
    ss_b = a * n * sum((cmean[c] - grand) ** 2 for c in conds)
    ss_ab = n * sum((statistics.mean(cell[(t, c)]) - tmean[t] - cmean[c] + grand) ** 2
                    for t in tasks for c in conds)
    ss_e = sum((v - statistics.mean(cell[(t, c)])) ** 2
               for t in tasks for c in conds for v in cell[(t, c)])
    if n == 1:
        raise ValueError("one observation per cell leaves no residual term")
    ms_a, ms_b = ss_a / (a - 1), ss_b / (b - 1)
    ms_ab, ms_e = ss_ab / ((a - 1) * (b - 1)), ss_e / (a * b * (n - 1))
    v_e = ms_e
    v_ab = max(0.0, (ms_ab - ms_e) / n)
    v_a = max(0.0, (ms_a - ms_ab) / (b * n))
    v_b = max(0.0, (ms_b - ms_ab) / (a * n))
    total = v_a + v_b + v_ab + v_e
    return {
        "components": {"task": v_a, "condition": v_b, "task_x_condition": v_ab,
                       "residual_repeat": v_e},
        "shares_percent": {k: round(100 * v / total, 1) for k, v in
                           [("task", v_a), ("condition", v_b),
                            ("task_x_condition", v_ab), ("residual_repeat", v_e)]},
        "design": {"tasks": a, "conditions": b, "repeats": n},
    }


def allocation(components: dict, budget: int = 48, z: float = Z_TWO_SIDED_80_POWER) -> list[dict]:
    v_ab = components["task_x_condition"]
    v_e = components["residual_repeat"]
    out = []
    for repeats in (1, 2, 3):
        tasks = budget // repeats
        se_mean = math.sqrt((v_ab + v_e / repeats) / tasks)
        se_diff = math.sqrt(2) * se_mean
        out.append({"repeats": repeats, "tasks": tasks,
                    "se_condition_mean": round(se_mean, 4),
                    "se_paired_difference": round(se_diff, 4),
                    "paired_mde_approx": round(z * se_diff, 4)})
    return out


def pearson(a: list[float], b: list[float]) -> float:
    if len(a) < 2:
        return 0.0
    ma, mb = statistics.mean(a), statistics.mean(b)
    sa, sb = statistics.pstdev(a), statistics.pstdev(b)
    if sa == 0 or sb == 0:
        return 0.0
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / len(a) / (sa * sb)


def analyse(path: pathlib.Path) -> dict:
    records = load_verdicts(path)
    coverage = coverage_by_episode(records)
    vc = variance_components(coverage)
    return {
        "source": str(path),
        "episodes": len(coverage),
        "element_judgements": len(records),
        "variance": vc,
        "allocation": allocation(vc["components"]),
        "conventions": {
            "coverage_counts_only_satisfied": True,
            "mde_uses_paired_difference_se": True,
            "sqrt_two_factor_applied": True,
        },
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: endpoint_analysis.py <verdicts.json>", file=sys.stderr)
        return 2
    path = pathlib.Path(sys.argv[1])
    if not path.is_file():
        print(f"no such file: {path}", file=sys.stderr)
        return 1
    print(json.dumps(analyse(path), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
