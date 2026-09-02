#!/usr/bin/env python3
"""Failing-first fixtures for block re-derivation.

The dangerous failure for this module is a silent zero: matching no artifacts and then
reporting no leaks and no redlines, which reads as a pass. That case must raise.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from recheck_block import episodes, recheck  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


# Satisfies all five structural checks: ablation, uncertainty, a concrete named
# resource, a primary outcome, and a stopping rule or falsifier.
CLEAN = ("Ablation over three arms on SWE-bench, primary outcome is task success, "
         "reported with a bootstrap confidence interval, and the stopping rule is "
         "fixed in advance.\n")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp)
        (d / "T1-task__C00.design.md").write_text(CLEAN, encoding="utf-8")
        (d / "K1-task__C11__r2.design.md").write_text(CLEAN, encoding="utf-8")
        (d / "K1-task__C11__r2.state.md").write_text("state\n", encoding="utf-8")
        (d / "notes.md").write_text("ignore me\n", encoding="utf-8")

        found = episodes(d)
        check("matches an episode without a repeat suffix", "T1-task__C00" in found, str(sorted(found)))
        check("matches an episode with a repeat suffix", "K1-task__C11__r2" in found, str(sorted(found)))
        check("does not count a state file as an episode", len(found) == 2, str(sorted(found)))
        check("ignores unrelated files", "notes" not in str(sorted(found)))

        r = recheck(d, canary=None)
        check("counts every matched episode", r["episodes"] == 2)
        check("a clean artifact reports no redline", r["fabrication_redlines_fired"] == 0)
        check("a clean artifact reports no structural gap",
              r["episodes_with_structural_gaps"] == 0, str(r["per_episode"]))
        check("no canary supplied means no leak counted", r["canary_leaks"] == 0)
        check("judged verdicts are declared out of scope", bool(r["excluded_from_recheck"]))

        (d / "K2-task__C00.design.md").write_text("we plan to do something.\n", encoding="utf-8")
        r2 = recheck(d, canary=None)
        check("an incomplete artifact is counted as a structural gap",
              r2["episodes_with_structural_gaps"] == 1, str(r2["episodes_with_structural_gaps"]))
        check("adding an incomplete artifact never lowers the gap count",
              r2["episodes_with_structural_gaps"] >= r["episodes_with_structural_gaps"])

        (d / "K4-task__C00.design.md").write_text(
            CLEAN + "We evaluate with dataset TBD and no baseline.\n", encoding="utf-8")
        r_red = recheck(d, canary=None)
        check("a fabricated resource fires a redline",
              r_red["fabrication_redlines_fired"] == 1, str(r_red["fabrication_redlines_fired"]))
        check("the redline names the offending rule",
              any("fabricated_resource" in p["redlines"] for p in r_red["per_episode"]),
              str([p["redlines"] for p in r_red["per_episode"]]))

        (d / "K3-task__C00.design.md").write_text(CLEAN + "WITHHELD-ABC123\n", encoding="utf-8")
        r3 = recheck(d, canary="WITHHELD-ABC123")
        check("a present canary is counted as a leak", r3["canary_leaks"] == 1)
        check("an absent canary is not counted",
              recheck(d, canary="WITHHELD-NOPE")["canary_leaks"] == 0)

    with tempfile.TemporaryDirectory() as empty:
        raised = False
        try:
            recheck(pathlib.Path(empty), canary=None)
        except ValueError:
            raised = True
        check("an empty directory raises instead of reporting a clean zero", raised)

    print("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
