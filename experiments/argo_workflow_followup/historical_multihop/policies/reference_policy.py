#!/usr/bin/env python3
"""Deterministic released-facts policy used only to validate the pipeline."""
from __future__ import annotations

import json
import sys
from pathlib import Path

case = json.loads(Path(sys.argv[1]).read_text())
state = dict(case["state_before"])
state.update(case["correction_event"]["updates"])
admitted = all(bool(state[node]) for node in case["decision_rule"]["all_of"])
selected = (
    case["decision_rule"]["if_true"]
    if admitted
    else case["decision_rule"]["if_false"]
)
response = {
    "schema_version": "argo-decision-packet/v1",
    "decision_id": case["decision_rule"]["decision_id"],
    "recheck_decision_ids": [case["decision_rule"]["decision_id"]],
    "evidence": [
        {"id": item["id"], "version": item["version"], "status": "VALID"}
        for item in case["source_identities"]
    ],
    "constraints": [
        {
            "id": item["id"],
            "version": item["version"],
            "applicable": item["applicable"],
        }
        for item in case["current_constraints"]
    ],
    "alternatives": [item["id"] for item in case["alternatives"]],
    "selected": selected,
    "missing_evidence": [],
    "unresolved_conflicts": [],
    "falsifier": "All frozen scorer, action, access, and stratum semantics must remain decision-valid.",
    "next_experiment": {
        "action": "construct an unambiguous stratified B3 contract",
        "observable": "affected-family resolution and unaffected-family no-harm",
        "stop_rule": "stop after the separately authorized eight development episodes",
    },
    "accessed_hidden_oracle": False,
}
Path(sys.argv[2]).write_text(json.dumps(response, sort_keys=True) + "\n")
