#!/usr/bin/env python3
"""Failing-first fixtures for the G-study and D-study.

Analytic cases have hand-computable answers. Guard cases assert the reason an
error was raised, not merely that one was raised.
"""
from __future__ import annotations

import itertools
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gstudy import (  # noqa: E402
    Components, DesignError, check_rectangular, d_study, degrees_of_freedom,
    elements_needed, g_study, g_study_repeats,
)

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except DesignError as exc:
        return str(exc)
    except Exception as exc:  # noqa: BLE001
        return f"__WRONG_TYPE__{type(exc).__name__}: {exc}"
    return "__NO_ERROR__"


C = ["c00", "c01", "c10", "c11"]
M = ["span", "full"]
E = [f"e{i}" for i in range(6)]


def build(fn):
    return {(p, m, e): fn(p, m, e) for p in C for m in M for e in E}


def main() -> int:
    # --- analytic cases -------------------------------------------------
    c = g_study(build(lambda p, m, e: 1), C, M, E)
    check("constant data gives zero everywhere",
          all(abs(v) < 1e-12 for v in vars(c).values()), str(vars(c)))

    c = g_study(build(lambda p, m, e: 1 if p in ("c00", "c01") else 0), C, M, E)
    check("pure condition effect isolates the condition component",
          c.condition > 0.2 and all(abs(getattr(c, n)) < 1e-12 for n in
              ("method", "element", "condition_method", "condition_element",
               "method_element", "residual")), str(vars(c)))

    c = g_study(build(lambda p, m, e: 1 if m == "full" else 0), C, M, E)
    check("pure method effect leaves the condition at zero",
          c.method > 0.2 and abs(c.condition) < 1e-12, str(vars(c)))

    c = g_study(build(lambda p, m, e: 1 if e in ("e0", "e1", "e2") else 0), C, M, E)
    check("pure element effect leaves the condition at zero",
          c.element > 0.2 and abs(c.condition) < 1e-12, str(vars(c)))

    c = g_study(build(lambda p, m, e: 1 if (p == "c11" and m == "full") else 0), C, M, E)
    check("a condition by method interaction lands in that component",
          c.condition_method > 0.01, str(vars(c)))

    # --- exact arithmetic, not just direction --------------------------
    c = g_study(build(lambda p, m, e: 1 if p in ("c00", "c01") else 0), C, M, E)
    check("the condition component takes its exact analytic value",
          abs(c.condition - 1.0 / 3.0) < 1e-12,
          f"expected 1/3 for a half-and-half split at 4x2x6, got {c.condition!r}")

    c = Components(0.05, 0.01, 0.02, 0.01, 0.03, 0.01, 0.10)
    d = d_study(c, 2, 6)
    want_rel = 0.01 / 2 + 0.03 / 6 + 0.10 / 12
    want_abs = want_rel + 0.01 / 2 + 0.02 / 6 + 0.01 / 12
    check("relative error variance matches the divisor-by-divisor computation",
          abs(d["relative_error_variance"] - want_rel) < 1e-12,
          f"expected {want_rel!r}, got {d['relative_error_variance']!r}")
    check("absolute error variance matches the divisor-by-divisor computation",
          abs(d["absolute_error_variance"] - want_abs) < 1e-12,
          f"expected {want_abs!r}, got {d['absolute_error_variance']!r}")

    dfs = degrees_of_freedom(4, 2, 6)
    check("degrees of freedom follow the crossed design",
          dfs == {"condition": 3, "method": 1, "element": 5, "condition_method": 3,
                  "condition_element": 15, "method_element": 5, "residual": 15}, str(dfs))
    msg = raises(degrees_of_freedom, 4, 1, 6)
    check("degrees of freedom refuse a one-level facet",
          "at least two levels" in msg, msg)

    neg = Components(0.05, 0.0, 0.0, 0.0, 0.0, 0.0, -0.12)
    d = d_study(neg, 1, 6)
    check("a negative component cannot produce a negative error variance",
          d["relative_error_variance"] >= 0.0, str(d))
    check("a negative component cannot push the coefficient above one",
          d["generalizability_coefficient"] <= 1.0, str(d))

    # residual pinned against an independently computed sum of squares.
    # The three-way sum of squares below is 1.6875 and the crossed design leaves
    # (4-1)(2-1)(2-1) = 3 degrees of freedom, so the component is exactly 0.5625.
    pat = {("c00", "span", "e0"): 1, ("c00", "span", "e1"): 0,
           ("c00", "full", "e0"): 0, ("c00", "full", "e1"): 1,
           ("c01", "span", "e0"): 1, ("c01", "span", "e1"): 1,
           ("c01", "full", "e0"): 1, ("c01", "full", "e1"): 0,
           ("c10", "span", "e0"): 0, ("c10", "span", "e1"): 1,
           ("c10", "full", "e0"): 1, ("c10", "full", "e1"): 1,
           ("c11", "span", "e0"): 0, ("c11", "span", "e1"): 0,
           ("c11", "full", "e0"): 1, ("c11", "full", "e1"): 0}
    rc = g_study(pat, C, M, ["e0", "e1"]).residual
    check("the residual is divided by the three-way degrees of freedom",
          abs(rc - 1.6875 / 3) < 1e-12,
          f"expected 1.6875/3 = 0.5625, got {rc!r}; a wrong divisor changes this")

    # --- clamping -------------------------------------------------------
    c = Components(-0.01, 0.02, 0.0, 0.0, 0.0, 0.0, 0.05)
    check("negative estimates are named", c.negatives() == ["condition"], str(c.negatives()))
    check("clamping zeroes the negative", c.clamped().condition == 0.0)
    check("clamping leaves other components untouched", c.clamped().method == 0.02)

    # --- decision study monotonicity -----------------------------------
    c = Components(0.05, 0.01, 0.02, 0.01, 0.03, 0.01, 0.10)
    check("more elements reduce error variance",
          d_study(c, 1, 12)["absolute_error_variance"] < d_study(c, 1, 1)["absolute_error_variance"])
    check("more methods reduce error variance",
          d_study(c, 4, 6)["absolute_error_variance"] < d_study(c, 1, 6)["absolute_error_variance"])
    check("absolute error is never below relative error",
          all(d_study(c, nm, ne)["absolute_error_variance"]
              >= d_study(c, nm, ne)["relative_error_variance"] - 1e-15
              for nm, ne in itertools.product((1, 2, 5), (1, 3, 9))))
    d = d_study(Components(0.05, 0.04, 0.02, 0.01, 0.03, 0.01, 0.10), 2, 6)
    check("dependability never exceeds generalizability",
          d["dependability_index"] <= d["generalizability_coefficient"] + 1e-15, str(d))
    d0 = d_study(Components(0, 0, 0, 0, 0, 0, 0), 1, 1)
    check("a degenerate design returns zero coefficients rather than dividing by zero",
          d0["generalizability_coefficient"] == 0.0 and d0["dependability_index"] == 0.0)

    # --- element search -------------------------------------------------
    c = Components(0.05, 0.0, 0.0, 0.0, 0.02, 0.0, 0.08)
    n = elements_needed(c, 0.8, n_methods=1)
    check("elements_needed reaches the target", n is not None and
          d_study(c, 1, n)["dependability_index"] >= 0.8, str(n))
    check("elements_needed returns the smallest such count", n is not None and n > 1 and
          d_study(c, 1, n - 1)["dependability_index"] < 0.8, str(n))
    check("an unreachable target returns None",
          elements_needed(Components(0.0001, 0.5, 0, 0, 0, 0, 0), 0.99, 1, cap=50) is None)

    # --- the replicated two-facet design ------------------------------
    CC = ["c00", "c01", "c10", "c11"]
    EE = [f"e{i}" for i in range(6)]

    def rbuild(fn, n=2):
        return {(p, e, r): fn(p, e, r) for p in CC for e in EE for r in range(n)}

    g = g_study_repeats(rbuild(lambda p, e, r: 1), CC, EE, 2)
    check("replicated design on constant data gives zero everywhere",
          all(abs(v) < 1e-12 for v in g["components"].values()), str(g["components"]))

    g = g_study_repeats(rbuild(lambda p, e, r: 1 if p in ("c00", "c01") else 0), CC, EE, 2)
    check("replicated design isolates a pure condition effect",
          abs(g["components"]["condition"] - 1.0 / 3.0) < 1e-12,
          f"expected 1/3, got {g['components']['condition']!r}")
    check("a pure condition effect leaves no residual",
          abs(g["components"]["residual"]) < 1e-12, str(g["components"]))

    # repeats disagree inside every cell: that is error, not interaction
    g = g_study_repeats(rbuild(lambda p, e, r: r % 2), CC, EE, 2)
    check("within-cell disagreement lands in the residual",
          g["components"]["residual"] > 0.2, str(g["components"]))
    check("within-cell disagreement does not create a condition component",
          g["components"]["condition"] <= 0.0 + 1e-12, str(g["components"]))

    g = g_study_repeats(rbuild(lambda p, e, r: 1 if (p == "c11") != (e == "e0") else 0), CC, EE, 2)
    check("a condition by element pattern lands in the interaction",
          g["components"]["condition_element"] > 0.05, str(g["components"]))

    check("clamped shares sum to one when anything is positive",
          abs(sum(g["clamped_share"].values()) - 1.0) < 1e-12, str(g["clamped_share"]))

    msg = raises(g_study_repeats, rbuild(lambda p, e, r: 1, 1), CC, EE, 1)
    check("one repeat cannot separate interaction from error",
          "at least 2 repeats" in msg, msg)

    obs = rbuild(lambda p, e, r: 1); del obs[("c00", "e0", 0)]
    msg = raises(g_study_repeats, obs, CC, EE, 2)
    check("a missing replicate is refused and counted",
          "not rectangular" in msg and "1 of 48" in msg, msg)

    obs = rbuild(lambda p, e, r: 1); obs[("c00", "e0", 0)] = 2
    msg = raises(g_study_repeats, obs, CC, EE, 2)
    check("a non-binary replicate is refused with its value",
          "must be 0 or 1" in msg and "2" in msg, msg)

    # --- guards, asserting the reason -----------------------------------
    obs = build(lambda p, m, e: 1); del obs[("c00", "span", "e0")]
    msg = raises(g_study, obs, C, M, E)
    check("a missing cell is refused and counted",
          "not rectangular" in msg and "1 of 48" in msg, msg)

    obs = build(lambda p, m, e: 1); obs[("c99", "span", "e0")] = 1
    msg = raises(check_rectangular, obs, C, M, E)
    check("an observation outside the declared levels is refused",
          "outside the declared levels" in msg, msg)

    obs = build(lambda p, m, e: 1); obs[("c00", "span", "e0")] = 0.5
    msg = raises(check_rectangular, obs, C, M, E)
    check("a non-binary score is refused with its value",
          "must be 0 or 1" in msg and "0.5" in msg, msg)

    msg = raises(check_rectangular, {(p, "span", e): 1 for p in C for e in E}, C, ["span"], E)
    check("one method cannot support a method facet",
          "method facet needs at least 2" in msg, msg)

    msg = raises(check_rectangular, {("c00", m, e): 1 for m in M for e in E}, ["c00"], M, E)
    check("one condition cannot support a condition component",
          "at least 2 conditions" in msg, msg)

    msg = raises(check_rectangular, {(p, m, "e0"): 1 for p in C for m in M}, C, M, ["e0"])
    check("one element cannot support an element facet",
          "element facet needs at least 2" in msg, msg)

    msg = raises(d_study, Components(0.05, 0, 0, 0, 0, 0, 0.1), 1, 0)
    check("a decision study with zero elements is refused",
          "at least one method and one element" in msg, msg)

    msg = raises(elements_needed, Components(0.05, 0, 0, 0, 0, 0, 0.1), 1.5, 1)
    check("an out-of-range target is refused with its value",
          "strictly between 0 and 1" in msg and "1.5" in msg, msg)

    # tally is computed after every check has run, never before
    print(f"\n{len(FAILURES)} failing: {', '.join(FAILURES)}" if FAILURES else "\nall checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
