#!/usr/bin/env python3
"""Element verification over candidate spans.

Cue matching was falsified as a decision procedure (RD-2026-09-02-14A), so it is
used only to retrieve candidate spans. Each candidate is then verified by a judge
from a different provider family than the treatment backend, which returns a
verdict and a confidence. Verdicts are inadmissible until the selective evaluator
is calibrated on human-anchored labels.

Contract: the judge must answer with one JSON object and nothing else.
"""
from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference_anchor import Element  # noqa: E402

WINDOW = 600

PROMPT = """You judge whether a design document satisfies one requirement.

REQUIREMENT: {requirement}

CANDIDATE PASSAGES FROM THE DOCUMENT:
{spans}

Answer whether the document satisfies the requirement, judged only on these passages.
A passage that mentions the topic while denying, deferring, or omitting it does NOT satisfy it.
Reply with exactly one JSON object and no other text:
{{"verdict": "satisfied" | "not_satisfied" | "unclear", "confidence": <number between 0 and 1>, "span": "<short quote you relied on>"}}
"""


def candidate_spans(text: str, element: Element, window: int = WINDOW) -> list[str]:
    spans, seen = [], set()
    for cue in element.cues:
        for m in re.finditer(cue, text, re.I):
            s = max(0, m.start() - window // 2)
            e = min(len(text), m.end() + window // 2)
            frag = text[s:e].strip()
            key = frag[:80]
            if key not in seen:
                seen.add(key)
                spans.append(frag)
            if len(spans) >= 4:
                return spans
    return spans


def parse_reply(out: str) -> dict:
    m = re.search(r'\{[^{}]*"verdict"[^{}]*\}', out, re.S)
    if not m:
        return {"verdict": "unparsed", "confidence": 0.0, "raw": out[-300:]}
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"verdict": "unparsed", "confidence": 0.0, "raw": m.group(0)[:300]}
    v = str(obj.get("verdict", "")).lower()
    if v not in {"satisfied", "not_satisfied", "unclear"}:
        v = "unparsed"
    try:
        c = float(obj.get("confidence", 0.0))
    except (TypeError, ValueError):
        c = 0.0
    return {"verdict": v, "confidence": max(0.0, min(1.0, c)), "span": str(obj.get("span", ""))[:300]}


def build_command(model: str, prompt: str) -> str:
    return (f"cd /tmp && timeout 300 prime-agent -p --no-session --offline-tools "
            f"--model {shlex.quote(model)} --thinking off {shlex.quote(prompt)}")


def verify(text: str, element: Element, model: str, runner=None) -> dict:
    spans = candidate_spans(text, element)
    if not spans:
        return {"element": element.element_id, "verdict": "not_satisfied", "confidence": 1.0,
                "reason": "no candidate span retrieved", "n_spans": 0}
    prompt = PROMPT.format(requirement=element.requirement, spans="\n\n---\n\n".join(spans))
    if runner is None:
        runner = lambda cmd: subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
    reply = parse_reply(runner(build_command(model, prompt)))
    reply.update({"element": element.element_id, "n_spans": len(spans)})
    return reply
