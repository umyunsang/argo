#!/usr/bin/env python3
"""Validate the context graph's structural invariants and field guarantees.

Two tiers, deliberately. A rule that can fail the build is a check; a rule that
cannot is a measurement. Reporting both, and saying which is which, is the point:
an earlier version of this project treated a self-attested field as verified and
that is how a simulation reached the manuscript.

ENFORCED (a violation returns a non-zero exit):
  * no duplicate node ids
  * no edge referencing an absent node
  * every node carries summary, status and next_action
  * every orphan node is on the justified list, and the list is exact

MEASURED (reported, never blocking yet):
  * evidence coverage. 112 nodes still have no evidence path. Forcing a value
    there would manufacture provenance, which is the defect this whole effort
    exists to remove, so the deficit is reported with its count instead.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "paper" / "context-graph.json"

REQUIRED_FIELDS = ("summary", "status", "next_action")
# A source that was reviewed and deliberately not cited has no claim chain by
# design. Forcing an edge onto it would invent a relation the record contradicts.
JUSTIFIED_ORPHANS = {"source:arxiv:2606.14924"}


def validate(graph: dict) -> dict:
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    ids = [n.get("id") for n in nodes]
    dupes = sorted(k for k, v in Counter(ids).items() if v > 1)
    idset = set(ids)
    dangling = [e.get("id") for e in edges
                if e.get("source") not in idset or e.get("target") not in idset]
    touched = set()
    for e in edges:
        touched.add(e.get("source"))
        touched.add(e.get("target"))
    orphans = sorted(idset - touched)
    unjustified = [o for o in orphans if o not in JUSTIFIED_ORPHANS]
    unneeded_justification = sorted(JUSTIFIED_ORPHANS - set(orphans))
    missing = {f: sorted(n["id"] for n in nodes if not n.get(f)) for f in REQUIRED_FIELDS}
    evidence_missing = sorted(n["id"] for n in nodes if not n.get("evidence"))

    failures = []
    if dupes:
        failures.append("duplicate node ids: %s" % ", ".join(dupes[:5]))
    if dangling:
        failures.append("edges referencing absent nodes: %s" % ", ".join(dangling[:5]))
    for f in REQUIRED_FIELDS:
        if missing[f]:
            failures.append("nodes missing %s: %d (first %s)" % (f, len(missing[f]), missing[f][0]))
    if unjustified:
        failures.append("orphan nodes without justification: %s" % ", ".join(unjustified[:5]))
    if unneeded_justification:
        failures.append("justified-orphan entries that are no longer orphans: %s"
                        % ", ".join(unneeded_justification[:5]))

    return {
        "nodes": len(nodes),
        "edges": len(edges),
        "node_kinds": dict(Counter(n.get("kind") for n in nodes)),
        "duplicate_node_ids": dupes,
        "dangling_edge_ids": dangling,
        "orphan_nodes": orphans,
        "justified_orphans": sorted(JUSTIFIED_ORPHANS),
        "unjustified_orphans": unjustified,
        "stale_justifications": unneeded_justification,
        "missing_field_counts": {f: len(missing[f]) for f in REQUIRED_FIELDS},
        "evidence_coverage": {
            "with_evidence": len(nodes) - len(evidence_missing),
            "without_evidence": len(evidence_missing),
            "tier": "measured",
            "why_not_enforced": "a manufactured evidence path is worse than an absent one",
        },
        "enforced_failures": failures,
        "passed": not failures,
    }


def main() -> int:
    if not GRAPH.is_file():
        print(json.dumps({"passed": False, "enforced_failures": ["context graph missing"]}))
        return 1
    report = validate(json.loads(GRAPH.read_text(encoding="utf-8")))
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
