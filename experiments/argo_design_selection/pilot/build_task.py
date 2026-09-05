#!/usr/bin/env python3
"""Build one budgeted-verification task workspace.

Shape follows the inherited-stale-constraint setting: a consolidated memory states a
decision constraint, the source that justified it has been superseded by a record that
withdraws it, and the agent may open only a small number of records. The treatment adds
one file: the dependency target computed by the dominance policy from the state graph.
The oracle answer is derived from the state, never from the policy code.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from targeting import policy_dominance, oracle_target  # noqa: E402

BUDGET = 2
TOPICS = [
    ("thermal", "batch size 64", "run-to-run variance above 8 percent"),
    ("retrieval", "top-k of 5", "duplicate passages in the shard"),
    ("calibration", "temperature 0.7", "label noise in the dev split"),
    ("throughput", "two parallel workers", "a scheduler bug that serialises jobs"),
    ("memory", "retain five prior episodes", "stale constraints surviving compaction"),
    ("simulation", "time step 0.02", "numerical instability on the held-out regime"),
    ("geometry", "mesh resolution 128", "boundary artefacts in the validation field"),
    ("sequencing", "minimum depth 30", "coverage bias in the rare subgroup"),
    ("optimizer", "learning rate 0.001", "divergence on the prospective split"),
    ("scheduler", "priority queue policy", "starvation of low-frequency experiments"),
    ("compression", "retain 20 percent of context", "loss of a required provenance span"),
]


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def state_graph(task_id: str) -> dict:
    """Evidence graph for the task. Edge s_old -> memory is the withdrawn support."""
    nodes = [
        {"id": "R1", "kind": "source", "scope": task_id},
        {"id": "R2", "kind": "source", "scope": task_id},
        {"id": "M", "kind": "claim", "scope": task_id},
        {"id": "D", "kind": "decision", "scope": task_id},
        {"id": "A", "kind": "action", "scope": task_id},
    ]
    edges = [
        {"id": "e:R1->M", "source": "R1", "target": "M", "relation": "supports", "scope": task_id},
        {"id": "e:M->D", "source": "M", "target": "D", "relation": "informs", "scope": task_id},
        {"id": "e:D->A", "source": "D", "target": "A", "relation": "governs_action", "scope": task_id},
    ]
    return {
        "schema_version": "argo-dependency-targeting-instance/v1",
        "family": "budgeted_verification",
        "instance_id": task_id,
        "seed": None,
        "roots": ["R1", "R2"],
        "nodes": nodes,
        "edges": edges,
        "event": {"removed_edge_ids": ["e:R1->M"], "kind": "source_support_withdrawn"},
    }


def build(seed: int, condition: str, workdir: Path) -> dict:
    assert condition in ("C_BASE", "C_TARGET")
    topic, setting, reason = TOPICS[seed % len(TOPICS)]
    task_id = f"bv-{seed:02d}-{topic}"
    workdir.mkdir(parents=True, exist_ok=True)
    rec = workdir / "records"
    rec.mkdir(exist_ok=True)

    records = {
        "R1": f"Record R1. The {topic} study recommended {setting} for the next run. "
              f"Status pointer: the current status of this recommendation is recorded in R3.",
        "R2": f"Record R2. Environment inventory for the {topic} study. No recommendation.",
        "R3": f"Record R3. The {topic} recommendation of {setting} is WITHDRAWN because of {reason}. "
              f"Do not carry it into the next run.",
        "R4": f"Record R4. Logging format notes for the {topic} study. No recommendation.",
        "R5": f"Record R5. Storage layout for the {topic} artefacts. No recommendation.",
        "M":  f"Record M. Settled constraint for the {topic} study: use {setting}. Justified by R1.",
    }
    for k, v in records.items():
        (rec / f"{k}.txt").write_text(v + "\n", encoding="utf-8")

    index = {
        "records": [{"id": k, "title": f"Record {k}"} for k in ("R1", "R2", "R3", "R4", "R5", "M")],
        "provenance": [{"claim": "M", "supported_by": ["R1"]}],
        "verification_budget_records": BUDGET,
        "note": "record bodies are not summarised here; opening a record costs one budget slot",
    }
    (workdir / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    graph = state_graph(task_id)
    target = sorted(policy_dominance(graph)["marked"])
    assert target == sorted(oracle_target(graph)), "computed target must equal the state-derived target"

    prefetched_records = []
    remaining_budget = BUDGET
    treatment_line = ""
    if condition == "C_TARGET":
        prefetched_records = ["R1"]
        remaining_budget = BUDGET - 1
        (workdir / "dependency_target.json").write_text(json.dumps({
            "computed_from": "the dependency graph of this state, not from the answer",
            "claim_under_decision": "M",
            "allocated_verification_slot": 1,
            "prefetched_record": {"id": "R1", "content": records["R1"]},
            "remaining_record_reads": remaining_budget,
            "downstream_if_support_fails": target,
            "meaning": "the system allocated one of the two verification slots to M's sole support; this file does not state R1's current status",
        }, indent=2) + "\n", encoding="utf-8")
        treatment_line = (f"\nThe dependency policy allocated one of the {BUDGET} verification slots to R1. "
                          f"`dependency_target.json` contains that prefetched record. You may open at most {remaining_budget} additional record file.\n")

    (workdir / "budget.json").write_text(json.dumps({
        "total_verification_budget": BUDGET,
        "prefetched_records": prefetched_records,
        "remaining_record_reads": remaining_budget,
    }, indent=2) + "\n", encoding="utf-8")

    task_md = f"""# Next-action decision for the {topic} study

You inherited a research state. `index.json` lists the records and the provenance links.
Record bodies are in `records/`.

Total verification budget: {BUDGET} records. You may open at most {remaining_budget} record files. Reading `index.json` is free.{treatment_line}
Decide whether the settled constraint in memory M still holds for the next run.

Write `decision.json` in this directory with exactly these keys:
  "constraint_status": "valid", "withdrawn", or "unverified"
  "action": "proceed" or "recheck"
  "records_inspected": list of record ids you opened
  "reason": one short sentence

Use only the available tools: `read_index`, `read_dependency_target`, `read_record`, and `write_decision`.
Write the file through `write_decision` and stop. Do not run anything else.
"""
    (workdir / "TASK.md").write_text(task_md, encoding="utf-8")

    return {
        "task_id": task_id, "seed": seed, "condition": condition,
        "budget": BUDGET, "remaining_budget": remaining_budget,
        "prefetched_records": prefetched_records, "critical_record": "R3",
        "ground_truth": {"constraint_status": "withdrawn", "action": "recheck"},
        "computed_target": target,
        "task_md_sha256": _sha(task_md),
        "records_sha256": {k: _sha(v) for k, v in records.items()},
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--condition", required=True)
    ap.add_argument("--workdir", type=Path, required=True)
    a = ap.parse_args()
    print(json.dumps(build(a.seed, a.condition, a.workdir), indent=2))
