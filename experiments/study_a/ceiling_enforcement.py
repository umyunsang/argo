#!/usr/bin/env python3
"""Post-hoc enforcement of declared episode ceilings.

A ceiling that is declared but never checked is decoration. The runner cannot cap a
provider mid-call, so the ceilings are enforced at scoring admission instead: an episode
whose measured usage exceeds a declared ceiling is inadmissible.

Which quantity a token ceiling refers to must be stated, because the answer changes the
verdict. Context is re-sent on every call, so an episode can sit far below a ceiling in
marginal tokens and far above it in billed total tokens. This module requires the
quantity to be named and refuses to guess.
"""
from __future__ import annotations

import json
import pathlib
import sys

QUANTITIES = ("marginal_tokens", "total_tokens", "api_calls", "wallclock_seconds")


def measured_quantities(usage: dict, wallclock_seconds: float | None = None) -> dict:
    tokens = usage.get("tokens") or {}
    return {
        "marginal_tokens": (tokens.get("input") or 0) + (tokens.get("output") or 0),
        "total_tokens": tokens.get("totalTokens") or 0,
        "api_calls": usage.get("api_calls") or 0,
        "wallclock_seconds": wallclock_seconds,
    }


def enforce(usage: dict, ceilings: dict, wallclock_seconds: float | None = None) -> dict:
    """Return an admission verdict for one episode against declared ceilings."""
    if not ceilings:
        return {"admissible": False, "reason": "no ceilings declared; admission undefined",
                "violations": [], "measured": {}}
    unknown = [k for k in ceilings if k not in QUANTITIES]
    if unknown:
        return {"admissible": False,
                "reason": f"ceiling names an unmeasured quantity: {sorted(unknown)}",
                "violations": [], "measured": {}}
    measured = measured_quantities(usage, wallclock_seconds)
    violations = []
    for name, limit in ceilings.items():
        value = measured.get(name)
        if value is None:
            violations.append({"quantity": name, "limit": limit, "measured": None,
                               "note": "not measured for this episode"})
            continue
        if value > limit:
            violations.append({"quantity": name, "limit": limit, "measured": value,
                               "exceeded_by": value - limit})
    return {"admissible": not violations, "violations": violations, "measured": measured}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: ceiling_enforcement.py <usage.json> <ceilings.json>", file=sys.stderr)
        return 2
    usage = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    ceilings = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
    print(json.dumps(enforce(usage, ceilings), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
