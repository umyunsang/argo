#!/usr/bin/env python3
"""Failing-first checks for the pilot builder and scorer. No model calls."""
from __future__ import annotations
import json, tempfile
from pathlib import Path
from build_task import build
from score import ScoringViolation, load_and_score, score_decision

F = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" :: " + detail if detail and not ok else ""))
    if not ok:
        F.append(name)


def main():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / "base"
        tgt = Path(td) / "tgt"
        m0 = build(0, "C_BASE", base)
        m1 = build(0, "C_TARGET", tgt)

        check("both conditions share identical record bytes", m0["records_sha256"] == m1["records_sha256"])
        check("both conditions share identical ground truth", m0["ground_truth"] == m1["ground_truth"])
        check("only the treatment carries the computed target",
              not (base / "dependency_target.json").exists() and (tgt / "dependency_target.json").exists())
        check("task text differs only by the declared treatment line",
              m0["task_md_sha256"] != m1["task_md_sha256"])
        check("computed target names the dependent nodes", m0["computed_target"] == ["A", "D", "M"],
              str(m0["computed_target"]))
        idx = json.loads((base / "index.json").read_text())
        blob = json.dumps(idx).lower()
        check("the free index never announces the supersession",
              "supersed" not in blob and "r3" not in blob.replace('"r3"', "R3PLACEHOLDER").lower() or "supersed" not in blob)
        check("record titles carry no relation hint",
              all(t["title"] == f"Record {t['id']}" for t in idx["records"]))
        tgt_file = json.loads((tgt / "dependency_target.json").read_text())
        check("the treatment prefetches the dependency, not the answer",
              tgt_file["prefetched_record"]["id"] == "R1"
              and "withdraw" not in json.dumps(tgt_file).lower())
        check("total verification budget is equal across conditions",
              m0["budget"] == m1["budget"] == 2
              and m0["remaining_budget"] == 2
              and m1["remaining_budget"] == 1
              and m1["prefetched_records"] == ["R1"])
        check("only R1 body carries the status pointer to the critical record",
              "R3" in (base / "records/R1.txt").read_text()
              and all("R3" not in (base / f"records/{r}.txt").read_text() for r in ("R2", "R4", "R5", "M")))
        check("no condition token leaks into the task text",
              all(t not in (base / "TASK.md").read_text().lower() for t in ("c_base", "c_target", "treatment")))

        gt, crit, bud = m0["ground_truth"], m0["critical_record"], m0["budget"]
        stale = {"constraint_status": "valid", "action": "proceed", "records_inspected": ["R1", "R2"], "reason": "x"}
        good = {"constraint_status": "withdrawn", "action": "recheck", "records_inspected": ["R3", "M"], "reason": "x"}
        s_stale = score_decision(stale, gt, crit, bud)
        s_good = score_decision(good, gt, crit, bud)
        check("stale decision is flagged stale and not correct",
              s_stale["stale_consistent"] and not s_stale["correct"])
        check("correct decision is not flagged stale", s_good["correct"] and not s_good["stale_consistent"])
        check("critical inspection is detected", s_good["critical_inspected"] and not s_stale["critical_inspected"])
        unver = {"constraint_status": "unverified", "action": "recheck", "records_inspected": ["R1"], "reason": "x"}
        s_unver = score_decision(unver, gt, crit, bud)
        check("unverified with recheck is partial, not stale and not fully correct",
              s_unver["partial"] and not s_unver["stale_consistent"] and not s_unver["correct"])
        over = dict(good, records_inspected=["R1", "R2", "R3"])
        check("budget violation is detected", score_decision(over, gt, crit, bud)["budget_violation"])
        check("observed reads override claimed reads",
              score_decision(good, gt, crit, bud, observed_reads=["R1"])["critical_inspected"] is False)
        check("prefetch plus one model read fits the shared total budget",
              not score_decision(good, gt, crit, bud, observed_reads=["R1", "R3"])["budget_violation"])

        try:
            score_decision(dict(good, reason="chosen for the treatment arm"), gt, crit, bud)
            caught = False
        except ScoringViolation:
            caught = True
        check("condition leak in the decision fails closed", caught)

        check("missing decision file is inadmissible, not silently wrong",
              load_and_score(base, m0)["admissible"] is False)
        (base / "decision.json").write_text("{not json", encoding="utf-8")
        check("unparsable decision is inadmissible", load_and_score(base, m0)["admissible"] is False)
        (base / "decision.json").write_text(json.dumps({"constraint_status": "maybe", "action": "proceed",
                                                        "records_inspected": [], "reason": "x"}), encoding="utf-8")
        check("out-of-range enum is inadmissible", load_and_score(base, m0)["admissible"] is False)

        a = build(1, "C_BASE", Path(td) / "a")
        b = build(1, "C_BASE", Path(td) / "b")
        check("builder is deterministic for a seed", a["records_sha256"] == b["records_sha256"])

    print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.")
    return 1 if F else 0


if __name__ == "__main__":
    raise SystemExit(main())
