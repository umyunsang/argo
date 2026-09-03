#!/usr/bin/env python3
"""Tests for the usage parser. No model call; nothing here is an episode."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import episode_runner as ER

F = []
def check(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (f" :: {d}" if not ok else ""))
    if not ok: F.append(n)

def main():
    t1 = '{"model":"x","total_tokens": 45210, "cost": "$0.13"}'
    u = ER.parse_usage(t1)
    check("json-style usage is parsed", u["total_tokens"] == 45210 and u["cost_usd"] == 0.13, str(u))

    t2 = "Usage: total tokens: 38,112\nTotal cost: $0.0425"
    u = ER.parse_usage(t2)
    check("prose-style usage is parsed", u["total_tokens"] == 38112 and u["cost_usd"] == 0.0425, str(u))

    u = ER.parse_usage("no usage anywhere")
    check("a transcript without usage yields zero, not a guess",
          u["total_tokens"] == 0 and u["cost_usd"] == 0.0, str(u))

    u = ER.parse_usage("1705817 is not tokens; 12 tokens neither")
    check("implausible values are not counted as tokens", u["total_tokens"] == 0, str(u))

    t3 = "first call total_tokens: 10000\nsecond call total_tokens: 12000"
    u = ER.parse_usage(t3)
    check("multiple usage records are summed", u["total_tokens"] == 22000, str(u))

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
