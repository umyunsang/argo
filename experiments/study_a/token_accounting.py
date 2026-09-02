#!/usr/bin/env python3
"""Extract measured token usage and cost from a JSON-mode episode transcript.

The pilot recorded token accounting as UNMEASURED because the text output mode
emits no usage record. The JSON mode does. This module reads that stream and
returns the measured totals, so cost stops being proxied by wall-clock duration.

    /usr/bin/python3 experiments/study_a/token_accounting.py <transcript.jsonl>
"""
from __future__ import annotations

import json
import pathlib
import sys

USAGE_FIELDS = ("input", "output", "cacheRead", "cacheWrite", "totalTokens")


def iter_records(text: str):
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def usage_from_transcript(text: str) -> dict:
    """Return the last reported usage, which is cumulative for the run.

    Usage is reported repeatedly and grows monotonically, so summing the records
    would multiply the true cost. The final record is taken instead, and the
    monotonicity assumption is checked rather than assumed.
    """
    seen = []
    model = None
    provider = None
    for rec in iter_records(text):
        msg = rec.get("message") or {}
        usage = msg.get("usage")
        if isinstance(usage, dict) and "totalTokens" in usage:
            seen.append(usage)
            model = msg.get("model", model)
            provider = msg.get("provider", provider)
    if not seen:
        return {"status": "UNMEASURED", "reason": "no usage record in transcript"}
    totals = [u.get("totalTokens", 0) for u in seen]
    monotonic = all(b >= a for a, b in zip(totals, totals[1:]))
    final = seen[-1]
    cost = final.get("cost") or {}
    return {
        "status": "MEASURED",
        "model": model,
        "provider": provider,
        "usage_records": len(seen),
        "monotonic": monotonic,
        "tokens": {k: final.get(k, 0) for k in USAGE_FIELDS},
        "cost_usd_total": cost.get("total", 0),
        "note": ("usage grows across records and the last one is cumulative; "
                 "summing records would overcount"),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: token_accounting.py <transcript.jsonl>", file=sys.stderr)
        return 2
    path = pathlib.Path(sys.argv[1])
    if not path.is_file():
        print(f"no such transcript: {path}", file=sys.stderr)
        return 1
    print(json.dumps(usage_from_transcript(path.read_text(encoding="utf-8")),
                     ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
