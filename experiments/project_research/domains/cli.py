"""Create-only domain evidence commands, intended to be launched through ORX."""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np
from threadpoolctl import threadpool_limits

from .common import DomainError, environment, file_digest, json_bytes, now, provenance, read_regular, write_new
from .custody import prepare_settings
from .diffusion import run_diffusion, verify_artifact
from .duckdb_workload import run_duckdb
from .wine import load_worker, prepare_wine, run_wine, score_predictions


def rescore_wine(worker_root: Path, original_result: Path) -> dict[str, object]:
    _train, dev, _manifest = load_worker(worker_root)
    source = json.loads(read_regular(original_result))
    if source.get("domain") != "wine" or source.get("status") != "OBSERVATIONS_RECORDED":
        raise DomainError("wine rescore input is not a completed wine result")
    artifact_root = original_result.with_name(original_result.stem + "-artifacts")
    observations = source["result"]["observations"]
    checks: dict[str, object] = {}
    for method, observation in observations.items():
        name = observation["prediction_file"]
        if Path(name).name != name or name != f"{method}.predictions.csv":
            raise DomainError("prediction filename mismatch")
        path = artifact_root / name
        if file_digest(path) != observation["prediction_sha256"]:
            raise DomainError("prediction hash mismatch")
        reader = csv.reader(io.StringIO(read_regular(path).decode()), strict=True)
        if next(reader, []) != ["row_id", "prediction"]:
            raise DomainError("prediction schema mismatch")
        rows = list(reader)
        if any(len(row) != 2 for row in rows) or [row[0] for row in rows] != [row.row_id for row in dev]:
            raise DomainError("prediction rows misaligned")
        values = np.array([float(row[1]) for row in rows])
        metrics = score_predictions(dev, values)
        if any(not math.isclose(value, observation["metrics"][name], rel_tol=1e-12, abs_tol=1e-12)
               for name, value in metrics.items()):
            raise DomainError("published wine metric does not match retained predictions")
        checks[method] = {"metrics": metrics, "matched": True}
    if set(checks) != {"pooled_histogram_boosting", "pooled_extra_trees", "separate_color_extra_trees"}:
        raise DomainError("wine result omits required baseline or alternative")
    return {"original_result_sha256": file_digest(original_result), "checks": checks,
            "passed": True, "scope": "Fresh process arithmetic rescore; not independent model retraining or final evaluation."}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare-wine", help="Trusted source acquisition and grouped custody split")
    prepare.add_argument("--worker-root", type=Path, required=True)
    prepare.add_argument("--evaluator-root", type=Path, required=True)
    prepare.add_argument("--source-archive", type=Path)
    settings = subparsers.add_parser("prepare-settings", help="Trusted final/future configuration preparation")
    settings.add_argument("--evaluator-root", type=Path, required=True)
    wine = subparsers.add_parser("wine", help="Real Wine Quality development baseline and hypothesis")
    wine.add_argument("--input", type=Path, required=True)
    system = subparsers.add_parser("duckdb", help="Real dbgen/Q1-derived development baseline and hypothesis")
    system.add_argument("--scale-factor", type=float, default=0.05)
    system.add_argument("--repeats", type=int, default=20)
    system.add_argument("--workload-cycles", type=int, default=4)
    numerical = subparsers.add_parser("diffusion", help="Actual anisotropic linear-system development study")
    numerical.add_argument("--grids", default="48,80")
    numerical.add_argument("--epsilons", default="0.1,0.01")
    numerical.add_argument("--angles", default="0,0.5235987755982988")
    numerical.add_argument("--repeats", type=int, default=3)
    numerical.add_argument("--rhs-count", type=int, default=3)
    wine_check = subparsers.add_parser("rescore-wine", help="Separate arithmetic rescore of retained dev predictions")
    wine_check.add_argument("--input", type=Path, required=True)
    wine_check.add_argument("--result", type=Path, required=True)
    diffusion_check = subparsers.add_parser("rescore-diffusion", help="Separate numerical checks of retained solution artifacts")
    diffusion_check.add_argument("--artifacts", type=Path, required=True)
    for command in (prepare, settings, wine, system, numerical, wine_check, diffusion_check):
        command.add_argument("--output", type=Path, required=True)
        command.add_argument("--seed", type=int, default=20260909)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if not 0 <= args.seed < 2**31 - 100:
        raise SystemExit("seed must be in [0, 2**31 - 100)")
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("output exists; preserve it and select a new attempt path")
    if not args.output.parent.is_dir():
        raise SystemExit("output parent must already exist")
    event_path = args.output.with_suffix(".events.jsonl")
    artifact_root = args.output.with_name(args.output.stem + "-artifacts")
    event_fd = os.open(event_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(event_fd, "w") as journal:
        def event_sink(event: dict[str, object]) -> None:
            journal.write(json.dumps(event, sort_keys=True, allow_nan=False) + "\n")
            journal.flush()
            os.fsync(journal.fileno())

        started = time.perf_counter()
        cpu_started = time.process_time()
        record = provenance(args.command, args.seed)
        record["command"] = [sys.executable, "-m", "experiments.project_research.domains.cli",
                             *(argv if argv is not None else sys.argv[1:])]
        if args.command.startswith("prepare-"):
            record["evidence_stage"] = "PREPARATION_ONLY"
        elif args.command.startswith("rescore-"):
            record["evidence_stage"] = "DEVELOPMENT_RESCORE_ONLY"
        event_sink({"at": now(), "event": "started", "command": args.command, "seed": args.seed})
        exit_code = 0
        try:
            if not environment()["matches_pins"]:
                raise DomainError("installed package versions do not match domains/requirements.txt")
            with threadpool_limits(limits=1):
                if args.command == "prepare-wine":
                    payload = prepare_wine(args.worker_root, args.evaluator_root, args.seed, args.source_archive)
                elif args.command == "prepare-settings":
                    payload = prepare_settings(args.evaluator_root, args.seed)
                elif args.command == "wine":
                    payload = run_wine(args.input, artifact_root, args.seed, event_sink)
                elif args.command == "duckdb":
                    payload = run_duckdb(artifact_root, args.seed, args.scale_factor, args.repeats,
                                         args.workload_cycles, event_sink)
                elif args.command == "diffusion":
                    payload = run_diffusion(artifact_root, args.seed,
                        tuple(int(value) for value in args.grids.split(",")),
                        tuple(float(value) for value in args.epsilons.split(",")),
                        tuple(float(value) for value in args.angles.split(",")),
                        args.repeats, args.rhs_count, event_sink)
                elif args.command == "rescore-wine":
                    payload = rescore_wine(args.input, args.result)
                else:
                    artifacts = sorted(args.artifacts.glob("case-*-repeat-*.npz"))
                    if not artifacts:
                        raise DomainError("no diffusion artifacts to rescore")
                    checks = {path.name: verify_artifact(path) for path in artifacts}
                    payload = {"checks": checks, "passed": all(item["passed"] for item in checks.values()),
                               "scope": "Fresh process independent stencil checks; not a new solver experiment or final evaluation."}
            record["result"] = payload
            record["status"] = "OBSERVATIONS_RECORDED"
            event_sink({"at": now(), "event": "completed", "status": record["status"]})
        except Exception as error:
            exit_code = 1
            record["status"] = "FAILED"
            record["failure"] = {"type": type(error).__name__, "message": str(error),
                                 "partial_evidence": event_path.name,
                                 "artifacts_retained": artifact_root.name if artifact_root.exists() else None}
            event_sink({"at": now(), "event": "failed", "failure": record["failure"]})
        record["elapsed_seconds"] = time.perf_counter() - started
        record["cpu_seconds"] = time.process_time() - cpu_started
        record["max_rss_raw"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        record["max_rss_units"] = "bytes" if sys.platform == "darwin" else "KiB"
        record["event_journal"] = event_path.name
    record["event_journal_sha256"] = file_digest(event_path)
    write_new(args.output, json_bytes(record))
    print(json.dumps({"status": record["status"], "output": str(args.output), "sha256": file_digest(args.output),
                      "evidence_stage": record["evidence_stage"]}, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
