#!/usr/bin/env python3
"""Failing-first fixtures for element verification.

The judge is nondeterministic, so these fixtures assert the deterministic shell around
it: which spans are retrieved, how a reply is parsed, and what happens when the judge
returns nothing usable. A dependency-injected runner replaces the model, so no fixture
depends on a live call. Expected values are fixed from the contract, not read back from
the module, because an oracle taken from the system under test cannot fail.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from reference_anchor import Element  # noqa: E402
from verify_elements import build_command, candidate_spans, parse_reply, verify  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def elem(cues, element_id="e1", requirement="hold the budget equal across arms"):
    return Element(element_id=element_id, requirement=requirement, cues=cues)


def main() -> int:
    e = elem(["matched", "identical budget"])

    check("no cue match retrieves no span", candidate_spans("nothing relevant here", e) == [])
    spans = candidate_spans("the arms used a matched budget throughout", e)
    check("a cue match retrieves a span", len(spans) == 1)
    check("the retrieved span contains the cue", "matched" in spans[0])

    long_text = ("filler " * 200) + "matched" + (" filler" * 200)
    wide = candidate_spans(long_text, e, window=40)
    check("window bounds the span length", len(wide[0]) <= 40 + len("matched") + 2,
          str(len(wide[0])))

    many = candidate_spans(" ".join(f"segment {i} matched here" for i in range(20)), e)
    check("span count is capped at four", len(many) <= 4, str(len(many)))

    dup = candidate_spans("matched matched matched", elem(["matched"]))
    check("identical spans are not returned twice", len(dup) == len(set(s[:80] for s in dup)))

    check("case insensitive cue matching", candidate_spans("MATCHED budget", e) != [])

    ok_reply = parse_reply('noise {"verdict": "satisfied", "confidence": 0.8, "span": "x"} tail')
    check("parses a verdict out of surrounding noise", ok_reply["verdict"] == "satisfied")
    check("parses confidence", ok_reply["confidence"] == 0.8)

    check("unknown verdict becomes unparsed",
          parse_reply('{"verdict": "definitely", "confidence": 0.9}')["verdict"] == "unparsed")
    check("missing json becomes unparsed",
          parse_reply("the model refused")["verdict"] == "unparsed")
    check("unparsed carries zero confidence, not a default pass",
          parse_reply("the model refused")["confidence"] == 0.0)
    check("malformed json becomes unparsed",
          parse_reply('{"verdict": "satisfied", confidence}')["verdict"] == "unparsed")
    check("confidence above one is clamped",
          parse_reply('{"verdict": "satisfied", "confidence": 4.0}')["confidence"] == 1.0)
    check("negative confidence is clamped",
          parse_reply('{"verdict": "satisfied", "confidence": -2}')["confidence"] == 0.0)
    check("non numeric confidence does not raise",
          parse_reply('{"verdict": "satisfied", "confidence": "high"}')["confidence"] == 0.0)

    no_span = verify("nothing relevant", e, model="m", runner=lambda cmd: "never called")
    check("absent evidence yields not_satisfied, never satisfied",
          no_span["verdict"] == "not_satisfied")
    check("absent evidence reports zero spans", no_span["n_spans"] == 0)

    seen = {}

    def runner(cmd):
        seen["cmd"] = cmd
        return '{"verdict": "satisfied", "confidence": 0.7}'

    out = verify("a matched budget was used", e, model="judge-model", runner=runner)
    check("verdict flows through", out["verdict"] == "satisfied")
    check("element id is attached", out["element"] == "e1")
    check("span count is attached", out["n_spans"] == 1)
    check("the requirement reaches the judge", "hold the budget equal" in seen["cmd"])
    check("the span reaches the judge", "matched budget" in seen["cmd"])
    check("the selected model reaches the judge", "judge-model" in seen["cmd"])

    cmd = build_command("a/b", "hi $(rm -rf /) `x`")
    check("prompt is shell quoted", "'hi $(rm -rf /) `x`'" in cmd)
    check("a safe model name is passed through unquoted", " a/b " in cmd)
    unsafe = build_command("m; rm -rf /", "p")
    check("an unsafe model name is shell quoted", "'m; rm -rf /'" in unsafe)

    print("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
