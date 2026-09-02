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


def iter_records(text: str, max_join_lines: int = 50):
    """Yield records, rejoining split records without swallowing a truncated stream.

    Two things break naive line parsing. Model output can embed newlines inside a
    JSON string, splitting one record across lines. And a captured transcript may be
    truncated in the middle, leaving a record that never completes. Buffering without
    a bound would swallow every later record after such a truncation, so the buffer
    is abandoned after a bounded number of lines and parsing resumes.
    """
    buffer = ""
    held = 0
    for line in text.splitlines():
        if buffer:
            stripped_line = line.lstrip()
            if stripped_line.startswith("{"):
                try:
                    standalone = json.loads(stripped_line)
                except json.JSONDecodeError:
                    standalone = None
                if standalone is not None:
                    # The buffered record never completed, which happens when a
                    # transcript is truncated. Resynchronise on this valid record
                    # instead of swallowing it into a buffer that cannot close.
                    buffer = ""
                    held = 0
                    yield standalone
                    continue
            buffer = buffer + "\n" + line
            held += 1
            try:
                record = json.loads(buffer)
            except json.JSONDecodeError:
                if held >= max_join_lines:
                    buffer = ""
                    held = 0
                continue
            buffer = ""
            held = 0
            yield record
            continue
        stripped = line.lstrip()
        if not stripped.startswith("{"):
            continue
        try:
            yield json.loads(stripped)
        except json.JSONDecodeError:
            buffer = line
            held = 0


def scan_report(text: str) -> dict:
    """Report how much of a transcript was parsed, so silent loss is visible."""
    starts = sum(1 for line in text.splitlines() if line.lstrip().startswith("{"))
    parsed = sum(1 for _ in iter_records(text))
    truncation_markers = text.count("bytes dropped")
    return {"lines_starting_a_record": starts, "records_parsed": parsed,
            "unparsed_remainder": max(0, starts - parsed),
            "truncation_markers": truncation_markers,
            "transcript_complete": truncation_markers == 0}


def usage_from_transcript(text: str) -> dict:
    """Sum usage over completed API calls in a run.

    An earlier version of this function took the last usage record, on the assumption
    that usage was cumulative for the run. That assumption was wrong and its fixture
    encoded it, so the error survived review. Each completed assistant message is one
    billed API call carrying its own usage, and a multi-turn episode re-sends its
    context on every call. Taking the last record understated one measured episode by
    a factor of 14.4. Usage is therefore summed over completed calls.
    """
    calls = []
    model = None
    provider = None
    for rec in iter_records(text):
        msg = rec.get("message") or {}
        usage = msg.get("usage")
        if rec.get("type") != "message_end" or not isinstance(usage, dict):
            continue
        if usage.get("totalTokens") is None:
            continue
        calls.append(usage)
        model = msg.get("model", model)
        provider = msg.get("provider", provider)
    if not calls:
        return {"status": "UNMEASURED", "reason": "no completed call with usage in transcript"}
    tokens = {k: sum(c.get(k) or 0 for c in calls) for k in USAGE_FIELDS}
    cost_total = sum((c.get("cost") or {}).get("total") or 0 for c in calls)
    return {
        "status": "MEASURED",
        "model": model,
        "provider": provider,
        "api_calls": len(calls),
        "tokens": tokens,
        "cost_usd_total": cost_total,
        "last_call_tokens": {k: calls[-1].get(k, 0) for k in USAGE_FIELDS},
        "note": ("usage is per completed API call and context is re-sent on each call; "
                 "totals are summed over calls, not read from the last record"),
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
