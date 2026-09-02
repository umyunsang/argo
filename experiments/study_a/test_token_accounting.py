#!/usr/bin/env python3
"""Failing-first fixtures for measured token accounting.

An earlier fixture asserted that the last usage record was the run total. That
assertion encoded the author's assumption rather than the transcript format, passed,
and protected a defect that understated one measured episode by a factor of 14.4.
The fixtures below assert the opposite and cover the multi-call case directly.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from token_accounting import iter_records, scan_report, usage_from_transcript  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool) -> None:
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        FAILURES.append(name)


def call(total: int, out: int, cost: float, cache_read: int = 0, kind: str = "message_end") -> str:
    return json.dumps({"type": kind, "message": {
        "role": "assistant", "model": "m", "provider": "p",
        "usage": {"input": 1, "output": out, "cacheRead": cache_read, "cacheWrite": 0,
                  "totalTokens": total, "cost": {"total": cost}}}})


def main() -> int:
    stream = "\n".join([call(100, 10, 0.1), call(200, 20, 0.2), call(300, 30, 0.3)])
    r = usage_from_transcript(stream)
    check("sums tokens over completed calls", r["tokens"]["totalTokens"] == 600)
    check("does not take the last record as the total", r["tokens"]["totalTokens"] != 300)
    check("sums output over calls", r["tokens"]["output"] == 60)
    check("sums cost over calls", abs(r["cost_usd_total"] - 0.6) < 1e-9)
    check("counts api calls", r["api_calls"] == 3)
    check("still exposes the last call for reference",
          r["last_call_tokens"]["totalTokens"] == 300)

    streaming = "\n".join([
        json.dumps({"type": "message_start", "message": {"usage": {"totalTokens": 0, "cost": {"total": 0}}}}),
        json.dumps({"type": "message_update", "message": {"usage": {"totalTokens": 0, "cost": {"total": 0}}}}),
        call(500, 50, 0.5),
    ])
    r2 = usage_from_transcript(streaming)
    check("ignores zeroed streaming records", r2["tokens"]["totalTokens"] == 500)
    check("does not count streaming records as calls", r2["api_calls"] == 1)

    check("records without a total are skipped, not counted as zero",
          usage_from_transcript(
              json.dumps({"type": "message_end", "message": {"usage": {"cost": {"total": 1}}}})
              + "\n" + call(70, 7, 0.07))["tokens"]["totalTokens"] == 70)
    check("empty transcript is unmeasured, not zero",
          usage_from_transcript("")["status"] == "UNMEASURED")

    split = '{"type":"message_end","message":{"usage":{"input":1,"output":2,\n"cacheRead":0,"cacheWrite":0,"totalTokens":9,"cost":{"total":0.01}}}}'
    check("rejoins a record split by an embedded newline",
          usage_from_transcript(split)["tokens"]["totalTokens"] == 9)

    truncated = call(11, 1, 0.01) + "\n" + '{"type":"message_end","message":{"usage":{"totalTokens":' \
        + "\n... [999 bytes dropped] ...\n" + call(22, 2, 0.02)
    r3 = usage_from_transcript(truncated)
    check("a truncated record does not swallow later records",
          r3["tokens"]["totalTokens"] == 33)
    check("truncation is reported, not hidden",
          scan_report(truncated)["transcript_complete"] is False)
    check("a clean transcript reports complete",
          scan_report(call(1, 1, 0.0))["transcript_complete"] is True)
    check("iter_records yields dicts", all(isinstance(x, dict) for x in iter_records(stream)))

    print(("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES)))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
