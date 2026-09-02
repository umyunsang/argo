#!/usr/bin/env python3
"""Failing-first fixtures for block planning."""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from block_planning import cost_per_episode, half_width, plan, required_n, wilson_interval  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def receipt(rates, cost=0.2):
    return {"per_episode": [{"cost_usd": cost} for _ in range(8)],
            "budget_completion": {"per_condition": {c: {"rate": r} for c, r in rates.items()}}}


def main() -> int:
    low, high = wilson_interval(3, 4)
    check("interval brackets the point estimate", low < 0.75 < high, f"{low} {high}")
    check("interval stays inside zero and one", 0.0 <= low and high <= 1.0)

    check("precision improves with n", half_width(0.75, 40) < half_width(0.75, 4))
    check("a rate at one still has width", half_width(1.0, 4) > 0)

    n = required_n(0.75, 0.15)
    check("required n meets the target", half_width(0.75, n) <= 0.15, str(n))
    check("required n is minimal", half_width(0.75, n - 1) > 0.15, str(n))
    check("a tighter target needs more episodes", required_n(0.75, 0.05) > required_n(0.75, 0.15))
    check("a rate at one needs fewer than a rate at one half",
          required_n(1.0, 0.15) < required_n(0.5, 0.15))

    # The message is asserted so a removed guard cannot pass by raising elsewhere.
    for bad, label in ((-0.1, "negative rate"), (1.5, "rate above one")):
        message = ""
        try:
            required_n(bad, 0.1)
        except ValueError as exc:
            message = str(exc)
        check(f"{label} raises for the rate, not incidentally",
              "rate must lie" in message, message or "nothing raised")
    raised = False
    try:
        required_n(0.5, 0)
    except ValueError:
        raised = True
    check("a zero target raises rather than looping", raised)

    raised = False
    try:
        cost_per_episode({"per_episode": []})
    except ValueError:
        raised = True
    check("planning refuses a receipt with no measured cost", raised)

    p = plan(receipt({"C00": 1.0, "C11": 0.75}), 0.15)
    check("planning uses the lowest observed rate", p["planning_rate"] == 0.75, str(p))
    check("cost comes from the receipt", p["measured_cost_per_episode_usd"] == 0.2)
    check("estimated cost is episodes times measured cost",
          abs(p["estimated_cost_usd"] - p["episodes"] * 0.2) < 0.01, str(p))
    check("episodes covers every condition", p["episodes"] == p["n_per_condition"] * 4)

    print("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
