"""Trusted preparation of undisclosed final/future numerical configurations."""
from __future__ import annotations

import datetime
import os
import random
from pathlib import Path

from .common import DomainError, digest, json_bytes, write_new
from .duckdb_workload import DEVELOPMENT_CUTOFFS


def prepare_settings(evaluator_root: Path, seed: int) -> dict[str, object]:
    evaluator_root = Path(evaluator_root)
    if evaluator_root.exists() or evaluator_root.is_symlink() or not evaluator_root.parent.is_dir():
        raise DomainError("evaluator settings root must be new under an existing parent")
    if any(path.is_symlink() for path in evaluator_root.parents):
        raise DomainError("evaluator settings path contains a symlink")
    evaluator_root.mkdir(mode=0o700)
    os.chmod(evaluator_root, 0o700)
    rng = random.Random(seed)
    used_dates = set(DEVELOPMENT_CUTOFFS)
    manifests: dict[str, str] = {}
    for phase in ("final", "future"):
        cutoffs: list[str] = []
        while len(cutoffs) < 6:
            cutoff = (datetime.date(1993, 1, 1) + datetime.timedelta(days=rng.randrange(1900))).isoformat()
            if cutoff not in used_dates:
                cutoffs.append(cutoff)
                used_dates.add(cutoff)
        contents = {
            "schema_version": "project-research-evaluator-settings/v1", "phase": phase,
            "seed": rng.randrange(2**31), "custody": "Evaluator only; never mount to development workers.",
            "duckdb": {"cutoffs": cutoffs, "scale_factor": 0.075 if phase == "final" else 0.12,
                       "repeats": 20, "workload_cycles": 4},
            "diffusion": {"grids": [64, 96] if phase == "final" else [72, 112],
                          "epsilons": [rng.uniform(0.015, 0.04), rng.uniform(0.15, 0.3)],
                          "angles": [rng.uniform(0.1, 0.4), rng.uniform(0.65, 1.0)],
                          "repeats": 3, "rhs_count": 3},
        }
        data = json_bytes(contents)
        write_new(evaluator_root / f"{phase}.json", data)
        manifests[phase] = digest(data)
    return {"schema_version": "project-research-settings-preparation/v1", "configuration_sha256": manifests,
            "values_disclosed": False, "seed_custody": "Controller preparation record only",
            "final_and_future_dates_disjoint": True,
            "boundary": "Files and permissions alone do not prove worker exclusion; controller must verify effective mounts."}
