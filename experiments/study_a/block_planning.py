#!/usr/bin/env python3
"""Block size required to estimate a completion rate to a stated precision.

This plans for precision, not for significance. A block that reaches significance on one
comparison can still leave every rate too wide to act on, and the question here is how
many episodes are needed before a completion rate says anything.

The cost per episode is a measured quantity, not an assumption: it is read from an
executed block receipt so a plan cannot quietly rest on a guessed price.

    /usr/bin/python3 experiments/study_a/block_planning.py <receipt.json> [half_width]
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

Z = 1.96


def wilson_interval(successes: int, n: int, z: float = Z) -> tuple[float, float]:
    if n <= 0:
        raise ValueError("n must be positive")
    p = successes / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (centre - margin) / denom), min(1.0, (centre + margin) / denom)


def half_width(rate: float, n: int, z: float = Z) -> float:
    low, high = wilson_interval(round(rate * n), n, z)
    return (high - low) / 2


def required_n(rate: float, target_half_width: float, max_n: int = 5000) -> int | None:
    """Smallest n whose interval half-width at this rate meets the target."""
    if not 0 <= rate <= 1:
        raise ValueError(f"rate must lie in [0, 1]; got {rate}")
    if target_half_width <= 0:
        raise ValueError("target half-width must be positive")
    for n in range(2, max_n + 1):
        if half_width(rate, n) <= target_half_width:
            return n
    return None


def cost_per_episode(receipt: dict) -> float:
    """Measured cost per episode from an executed block, never a guess."""
    episodes = receipt.get("per_episode") or []
    costs = [e["cost_usd"] for e in episodes if isinstance(e.get("cost_usd"), (int, float))]
    if not costs:
        raise ValueError("receipt records no per-episode cost; cannot plan on a guess")
    return sum(costs) / len(costs)


def plan(receipt: dict, target_half_width: float = 0.15, conditions: int = 4) -> dict:
    per_episode = cost_per_episode(receipt)
    observed = (receipt.get("budget_completion") or {}).get("per_condition") or {}
    worst = min((v["rate"] for v in observed.values()), default=0.5)
    n = required_n(worst, target_half_width)
    if n is None:
        return {"feasible": False, "reason": "no n below the search limit reaches this precision"}
    episodes = n * conditions
    return {
        "feasible": True,
        "target_half_width": target_half_width,
        "planning_rate": worst,
        "planning_rate_source": "the lowest observed completion rate, which needs the most episodes",
        "n_per_condition": n,
        "conditions": conditions,
        "episodes": episodes,
        "measured_cost_per_episode_usd": round(per_episode, 4),
        "estimated_cost_usd": round(episodes * per_episode, 2),
        "current_half_width": round(half_width(worst, 4), 3),
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: block_planning.py <receipt.json> [half_width]", file=sys.stderr)
        return 2
    receipt = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    target = float(sys.argv[2]) if len(sys.argv) > 2 else 0.15
    print(json.dumps(plan(receipt, target), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
