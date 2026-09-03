#!/usr/bin/env python3
"""Failing-first fixtures for the context-graph schema validator."""
from __future__ import annotations

import copy
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from graph_schema import JUSTIFIED_ORPHANS, validate  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def base():
    # includes the one orphan the module justifies, so "clean" really means clean
    return {"nodes": [
        {"id": "a", "kind": "artifact", "summary": "s", "status": "EXECUTED",
         "next_action": "none", "evidence": "p.json"},
        {"id": "b", "kind": "decision", "summary": "s", "status": "RECORDED",
         "next_action": "x", "evidence": "p.json"},
        {"id": sorted(JUSTIFIED_ORPHANS)[0], "kind": "source", "summary": "reviewed, not cited",
         "status": "VERIFIED", "next_action": "none", "evidence": "z"},
    ], "edges": [{"id": "edge:1", "source": "a", "target": "b", "relation": "constrains_output"}]}


def main() -> int:
    ok = validate(base())
    check("a clean graph passes", ok["passed"], str(ok["enforced_failures"]))
    check("a clean graph has no unjustified orphans",
          ok["unjustified_orphans"] == [] and ok["orphan_nodes"] == sorted(JUSTIFIED_ORPHANS),
          str(ok["orphan_nodes"]))

    g = base(); g["nodes"].append(copy.deepcopy(g["nodes"][1]))
    r = validate(g)
    check("a duplicate node id is refused and named",
          not r["passed"] and r["duplicate_node_ids"] == ["b"], str(r["duplicate_node_ids"]))

    g = base(); g["edges"].append({"id": "edge:2", "source": "a", "target": "ghost",
                                   "relation": "evaluated_by"})
    r = validate(g)
    check("an edge to an absent node is refused",
          not r["passed"] and r["dangling_edge_ids"] == ["edge:2"], str(r["dangling_edge_ids"]))

    g = base(); g["edges"] = []
    r = validate(g)
    check("orphans are refused when unjustified",
          not r["passed"] and sorted(r["unjustified_orphans"]) == ["a", "b"], str(r["unjustified_orphans"]))

    for f in ("summary", "status", "next_action"):
        g = base(); g["nodes"][1].pop(f)
        r = validate(g)
        check(f"a node missing {f} is refused",
              not r["passed"] and any(f in x for x in r["enforced_failures"]),
              str(r["enforced_failures"]))

    g = base(); g["nodes"][1].pop("evidence")
    r = validate(g)
    check("missing evidence is measured, not enforced",
          r["passed"] and r["evidence_coverage"]["without_evidence"] == 1
          and r["evidence_coverage"]["tier"] == "measured", str(r["evidence_coverage"]))

    r = validate(base())
    check("a justified orphan is accepted", r["passed"] and r["orphan_nodes"], str(r["enforced_failures"]))

    g = base()
    g["nodes"] = [n for n in g["nodes"] if n["id"] not in JUSTIFIED_ORPHANS]
    r = validate(g)
    check("a justification that no longer matches an orphan is refused",
          not r["passed"] and r["stale_justifications"], str(r["enforced_failures"]))

    print(f"\n{len(FAILURES)} failing: {', '.join(FAILURES)}" if FAILURES else "\nall checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
