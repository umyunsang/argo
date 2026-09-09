"""The four project records shared by all comparison conditions."""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path


class ContractError(ValueError):
    pass


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def required(value: dict, names: tuple[str, ...]) -> None:
    for key in names:
        if key not in value or value[key] is None or value[key] == "":
            raise ContractError(f"missing {key}")


def validate_record(value: dict) -> dict:
    if not isinstance(value, dict):
        raise ContractError("record must be an object")
    required(value, ("type", "id", "project_id", "created_at"))
    try:
        parsed = datetime.fromisoformat(value["created_at"])
        if parsed.utcoffset() is None:
            raise ValueError("timezone required")
        canonical(value)
    except (ValueError, TypeError) as exc:
        raise ContractError("invalid timestamp or non-finite record") from exc
    kind = value["type"]
    if kind == "ResearchContract":
        required(value, ("question", "mission", "constraints", "evaluation", "resources", "stop_conditions", "condition", "continuity", "model_pool_digest"))
        if value["condition"] not in ("B", "H", "P") or type(value["continuity"]) is not bool:
            raise ContractError("invalid comparison condition")
        resources = value["resources"]
        for key, ceiling in (("wall_seconds", 28800), ("cpu_core_seconds", 28800), ("cpus", 4), ("memory_mib", 4608)):
            n = resources.get(key)
            if isinstance(n, bool) or not isinstance(n, (float, int)) or not math.isfinite(n) or not 0 < n <= ceiling:
                raise ContractError(f"invalid resource {key}")
        if value["evaluation"].get("final_visible_to_workers") is not False:
            raise ContractError("final evaluation must be private")
    elif kind == "DecisionRecord":
        required(value, ("question", "selected_edge", "alternatives", "evidence", "expected_information", "change_scope", "tool_version"))
        if value["change_scope"] not in ("research", "harness"):
            raise ContractError("research and harness changes must be distinct")
        if not isinstance(value["alternatives"], list) or not value["alternatives"]:
            raise ContractError("alternatives required")
        if not isinstance(value["evidence"], list) or not value["evidence"]:
            raise ContractError("actual evidence locators required")
    elif kind == "Checkpoint":
        required(value, ("question", "artifacts", "uncertainties", "orx_runs", "tool_versions", "budget", "model_id", "session_id", "confirmed_decisions", "first_hypothesis_observed"))
        if type(value["first_hypothesis_observed"]) is not bool:
            raise ContractError("invalid hypothesis flag")
        for run in value["orx_runs"]:
            required(run, ("experiment_id", "run_id", "status"))
        if value["first_hypothesis_observed"] and not value.get("observation_evidence"):
            raise ContractError("continuity trigger needs an observation receipt")
    elif kind == "Assessment":
        required(value, ("layer", "round_id", "session_id", "candidate_id", "findings", "quality", "superiority", "pi_acceptance"))
        if value["layer"] not in ("research_operations", "evaluated_harness"):
            raise ContractError("assessment layers must be separate")
        if value["quality"] not in ("AAA", "REWORK", "UNASSESSED"):
            raise ContractError("invalid quality")
        if value["pi_acceptance"] not in ("PENDING", "ACCEPTED", "REJECTED"):
            raise ContractError("invalid PI outcome")
    else:
        raise ContractError(f"unknown record type {kind}")
    return value


def write_new(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def make_contract(project_id: str, domain: str, condition: str, continuity: bool, pool_digest: str) -> dict:
    missions = {
        "wine": "적·백포도주 예측 성능과 적용 범위를 연구한다.",
        "duckdb": "정확성을 유지하며 준비 비용을 포함한 분석 질의 총비용을 낮춘다.",
        "diffusion": "이방성 확산 선형계 해법의 정확도, 준비비, 계산비와 유효 범위를 연구한다.",
    }
    criteria = {
        "wine": ["color and equal-weight MAE", "feature-duplicate group isolation", "independent refit and score", "negative conclusion permitted"],
        "duckdb": ["equivalent answers", "held-out parameters", "20 or more randomized paired repeats", "setup plus workload", "95% interval supports at least 10% reduction"],
        "diffusion": ["known solution", "independent residual and solution error", "separate setup and solve", "negative conclusion permitted"],
    }
    return validate_record({
        "type": "ResearchContract", "id": f"contract-{project_id}", "project_id": project_id,
        "created_at": utc_now(), "domain": domain, "question": "Agent to refine from literature and development observations",
        "mission": missions[domain], "condition": condition, "continuity": continuity,
        "constraints": ["no native runtime changes", "no hidden-outcome retuning", "preserve failures", "same model pool and tool rights"],
        "evaluation": {"criteria": criteria[domain], "final_visible_to_workers": False, "primary": "PI-accepted research completion within resources", "unit": "project", "official_benchmark_claim": False},
        "resources": {"wall_seconds": 28800, "cpu_core_seconds": 28800, "cpus": 1, "memory_mib": 2048},
        "stop_conditions": ["sufficient verified conclusion", "resource ceiling", "unknown usage or launch requires reconciliation"],
        "model_pool_digest": pool_digest,
    })
