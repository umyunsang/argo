#!/usr/bin/env python3
"""Census of the project's own decision record.

This measures the research process, not the object of study. It reports how many
recorded decisions were later revised, and what triggered each revision. It is a
descriptive census of a single project with no comparison group, so it cannot show
that recording falsifiers causes revision.
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER = ROOT / "paper/research/autonomous-research-decision-ledger.json"


def load_records(ledger_path: pathlib.Path) -> list[dict]:
    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    out: list[dict] = []
    for key, value in data.items():
        if re.match(r"round\d+_decision_records$", key) and isinstance(value, list):
            for rec in value:
                out.append(dict(rec, _group=key))
    return out


def census(records: list[dict]) -> dict:
    revised = [r for r in records if r.get("status", "ACTIVE") != "ACTIVE"]
    return {
        "decision_records": len(records),
        "recording_groups": len({r["_group"] for r in records}),
        "with_falsifier": sum(1 for r in records if r.get("falsifier")),
        "with_executed_evidence": sum(1 for r in records if r.get("evidence")),
        "revised": len(revised),
        "revised_ids": sorted(r["decision_id"] for r in revised),
        "revision_status_counts": dict(collections.Counter(r["status"] for r in revised)),
        "revision_rate": round(len(revised) / len(records), 4) if records else 0.0,
        "blocking": sum(1 for r in records if r.get("blocking")),
    }


def main() -> int:
    records = load_records(LEDGER)
    if not records:
        print("no decision records found", file=sys.stderr)
        return 1
    result = census(records)
    result["scope"] = (
        "descriptive census of one project's decision record; no comparison group, "
        "so no causal claim about the recording practice is supported"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
