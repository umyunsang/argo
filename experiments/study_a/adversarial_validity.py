#!/usr/bin/env python3
"""Adversarial validity test for the reference-anchored coverage scorer.

RD-2026-09-02-11A carries its own falsifier: if coverage does not separate
artifacts that a reader would rank differently, it measures vocabulary. The
method here follows planted-shortcut evaluation: construct probes that satisfy
the surface cue without the substance, and probes that carry the substance
without the cue, then measure the scorer's false-positive and false-negative
rates against them.

Two probe families per checklist element:

* stuffing probe   - contains the cue token inside a negation or an irrelevant
                     sentence. A valid scorer must NOT count it.
* paraphrase probe - states the requirement in different words with the cue
                     token removed. A valid scorer SHOULD count it.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference_anchor import Element, load_checklist  # noqa: E402

NEGATION_TEMPLATES = [
    "We deliberately do not use {cue}.",
    "A reviewer might ask about {cue}, but this design omits it entirely.",
    "Unlike other work, {cue} plays no role here.",
]


def _cue_surface(pattern: str) -> str:
    """A readable surface string that the pattern would match."""
    s = re.sub(r"\[- \]", " ", pattern)
    s = re.sub(r"\{[^}]*\}|\.\*|\.\{[^}]*\}|[\\^$()?+*\[\]]", "", s)
    s = s.split("|")[0].strip()
    return s or pattern


def stuffing_probes(element: Element) -> list[str]:
    out = []
    for pattern in element.cues[:2]:
        surface = _cue_surface(pattern)
        if not surface:
            continue
        for t in NEGATION_TEMPLATES[:1]:
            out.append(t.format(cue=surface))
    return out


def scorer_counts(text: str, element: Element) -> bool:
    return element.covered(text)


def evaluate(checklist: list[Element], paraphrases: dict[str, str]) -> dict:
    false_positives, tested_stuffing = [], 0
    for e in checklist:
        for probe in stuffing_probes(e):
            tested_stuffing += 1
            if scorer_counts(probe, e):
                false_positives.append({"element": e.element_id, "probe": probe})
    false_negatives, tested_paraphrase = [], 0
    for e in checklist:
        para = paraphrases.get(e.element_id)
        if not para:
            continue
        tested_paraphrase += 1
        if not scorer_counts(para, e):
            false_negatives.append({"element": e.element_id, "probe": para})
    return {
        "stuffing_probes": tested_stuffing,
        "false_positives": len(false_positives),
        "false_positive_rate": round(len(false_positives) / tested_stuffing, 3) if tested_stuffing else 0.0,
        "paraphrase_probes": tested_paraphrase,
        "false_negatives": len(false_negatives),
        "false_negative_rate": round(len(false_negatives) / tested_paraphrase, 3) if tested_paraphrase else 0.0,
        "false_positive_detail": false_positives[:20],
        "false_negative_detail": false_negatives[:20],
    }


def main() -> int:
    anchors = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("paper/experiments/anchors")
    paraphrase_file = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("paper/experiments/anchors/paraphrase-probes.json")
    paraphrases = json.loads(paraphrase_file.read_text(encoding="utf-8")) if paraphrase_file.is_file() else {}
    results = {}
    for f in sorted(anchors.glob("*.json")):
        if f.name == paraphrase_file.name:
            continue
        results[f.stem] = evaluate(load_checklist(f), paraphrases.get(f.stem, {}))
    fp = sum(r["false_positives"] for r in results.values())
    sp = sum(r["stuffing_probes"] for r in results.values())
    fn = sum(r["false_negatives"] for r in results.values())
    pp = sum(r["paraphrase_probes"] for r in results.values())
    print(json.dumps({"suite": "adversarial_validity", "per_task": results,
                      "overall": {"stuffing_probes": sp, "false_positives": fp,
                                  "false_positive_rate": round(fp / sp, 3) if sp else 0.0,
                                  "paraphrase_probes": pp, "false_negatives": fn,
                                  "false_negative_rate": round(fn / pp, 3) if pp else 0.0}},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
