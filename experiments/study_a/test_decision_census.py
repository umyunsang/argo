#!/usr/bin/env python3
"""Failing-first fixtures for the decision census."""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from decision_census import census, load_records  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool) -> None:
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        FAILURES.append(name)


def main() -> int:
    base = [
        {"decision_id": "A", "falsifier": "f", "evidence": {}, "_group": "round1_decision_records"},
        {"decision_id": "B", "falsifier": "f", "status": "FALSIFIED_BY_MEASUREMENT",
         "_group": "round1_decision_records"},
        {"decision_id": "C", "_group": "round2_decision_records"},
    ]
    r = census(base)
    check("counts every record", r["decision_records"] == 3)
    check("counts recording groups", r["recording_groups"] == 2)
    check("counts falsifiers, not records", r["with_falsifier"] == 2)
    check("counts revised", r["revised"] == 1 and r["revised_ids"] == ["B"])
    check("rate is revised over total", r["revision_rate"] == round(1 / 3, 4))
    check("does not count active as revised", "A" not in r["revised_ids"])

    empty = census([])
    check("empty ledger does not divide by zero", empty["revision_rate"] == 0.0)

    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "led.json"
        p.write_text(json.dumps({
            "round9_decision_records": [{"decision_id": "X"}],
            "updated_at": "now",
            "notes": ["not a record list"],
            "roundabout_decision_records_extra": [{"decision_id": "Y"}],
        }), encoding="utf-8")
        loaded = load_records(p)
        check("loads only round-numbered record lists",
              [x["decision_id"] for x in loaded] == ["X"])

    print(("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES)))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
