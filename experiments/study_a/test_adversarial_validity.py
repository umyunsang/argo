#!/usr/bin/env python3
"""Failing-first fixtures for the adversarial validity check.

This module is the falsifier for cue-based coverage, so its own arithmetic must be
right: a stuffing probe that the scorer counts is a false positive, a paraphrase probe
it misses is a false negative, and neither rate may be silently divided by zero.
Expected values are fixed from the definitions above, not read back from the module.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from adversarial_validity import (  # noqa: E402
    NEGATION_TEMPLATES, _cue_surface, evaluate, scorer_counts, stuffing_probes,
)
from reference_anchor import Element  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def elem(element_id, cues, requirement="requirement text"):
    return Element(element_id=element_id, requirement=requirement, cues=cues)


def main() -> int:
    check("cue surface strips regex syntax",
          _cue_surface(r"match(ed)?[- ]budget") == "matched budget",
          _cue_surface(r"match(ed)?[- ]budget"))
    check("cue surface takes the first alternative",
          _cue_surface("alpha|beta") == "alpha")
    check("cue surface never returns empty for a real pattern",
          _cue_surface(".*") != "")

    e = elem("e1", ["matched", "identical"])
    probes = stuffing_probes(e)
    check("a stuffing probe is built per cue", len(probes) == 2, str(probes))
    check("a stuffing probe negates the cue",
          all(any(t.split("{cue}")[0].strip() in p for t in NEGATION_TEMPLATES) for p in probes),
          str(probes))
    check("a stuffing probe still contains the cue token",
          all("matched" in p or "identical" in p for p in probes))

    check("the scorer counts a plain cue occurrence", scorer_counts("we used matched budgets", e))
    check("the scorer does not count unrelated text", not scorer_counts("nothing here", e))

    # A scorer that counts a negated cue is exactly the failure this module detects.
    rep = evaluate([e], paraphrases={})
    check("stuffing probes are counted", rep["stuffing_probes"] == 2)
    check("counting a negated cue is a false positive", rep["false_positives"] == 2, str(rep))
    check("false positive rate is positives over probes",
          rep["false_positive_rate"] == 1.0, str(rep))
    check("no paraphrase supplied means no paraphrase probe", rep["paraphrase_probes"] == 0)
    check("empty paraphrase set does not divide by zero",
          rep["false_negative_rate"] == 0.0, str(rep))

    rep2 = evaluate([e], paraphrases={"e1": "the arms received equal compute and equal access"})
    check("a paraphrase without the cue is a false negative", rep2["false_negatives"] == 1, str(rep2))
    check("false negative rate is negatives over paraphrase probes",
          rep2["false_negative_rate"] == 1.0, str(rep2))

    rep3 = evaluate([e], paraphrases={"e1": "the arms used matched budgets"})
    check("a paraphrase containing the cue is not a false negative",
          rep3["false_negatives"] == 0, str(rep3))

    rep4 = evaluate([], paraphrases={})
    check("an empty checklist does not divide by zero",
          rep4["false_positive_rate"] == 0.0 and rep4["false_negative_rate"] == 0.0)
    check("an empty checklist reports zero probes", rep4["stuffing_probes"] == 0)

    check("a paraphrase for an unknown element is ignored",
          evaluate([e], paraphrases={"other": "text"})["paraphrase_probes"] == 0)

    print("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
