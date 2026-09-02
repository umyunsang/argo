#!/usr/bin/env python3
"""Failing-first fixtures for measured token accounting."""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from token_accounting import usage_from_transcript  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool) -> None:
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        FAILURES.append(name)


def line(total: int, out: int = 0, cost: float = 0.0) -> str:
    return json.dumps({"type": "message_update", "message": {
        "role": "assistant", "model": "m", "provider": "p",
        "usage": {"input": 1, "output": out, "cacheRead": 0, "cacheWrite": 0,
                  "totalTokens": total, "cost": {"total": cost}}}})


def main() -> int:
    stream = "\n".join([line(10), line(40), line(120, out=50, cost=0.25)])
    r = usage_from_transcript(stream)
    check("reports measured status", r["status"] == "MEASURED")
    check("takes the last cumulative total, not the sum",
          r["tokens"]["totalTokens"] == 120)
    check("does not sum records into 170", r["tokens"]["totalTokens"] != 170)
    check("keeps cost from the final record", r["cost_usd_total"] == 0.25)
    check("counts usage records", r["usage_records"] == 3)
    check("flags monotonic growth", r["monotonic"] is True)
    check("carries model and provider", r["model"] == "m" and r["provider"] == "p")

    r2 = usage_from_transcript("\n".join([line(100), line(20)]))
    check("detects non-monotonic usage instead of trusting it", r2["monotonic"] is False)

    check("empty transcript is unmeasured, not zero",
          usage_from_transcript("")["status"] == "UNMEASURED")
    check("non-json noise is ignored",
          usage_from_transcript("hello\n" + line(7))["tokens"]["totalTokens"] == 7)
    check("records without usage are ignored",
          usage_from_transcript(json.dumps({"type": "turn_start"}) + "\n" + line(5))
          ["usage_records"] == 1)

    print(("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES)))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
