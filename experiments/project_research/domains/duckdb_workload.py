"""Parameterized public Q1-derived development workload; not a TPC result."""
from __future__ import annotations

import datetime
import decimal
import json
import math
import os
import random
import statistics
import time
from pathlib import Path

import duckdb
import numpy as np

from .common import DomainError, EventSink, digest, emit, file_digest, json_bytes, write_new

SOURCE_PAGE = "https://duckdb.org/docs/lts/core_extensions/tpch"
DEVELOPMENT_CUTOFFS = ("1993-12-01", "1994-12-01", "1995-12-01", "1996-12-01", "1997-12-01", "1998-09-02")
BASELINE_SQL = """
SELECT l_returnflag, l_linestatus,
       sum(l_quantity), sum(l_extendedprice),
       sum(l_extendedprice * (1 - l_discount)),
       sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)),
       avg(l_quantity), avg(l_extendedprice), avg(l_discount), count(*)
FROM lineitem WHERE l_shipdate <= CAST(? AS DATE)
GROUP BY l_returnflag, l_linestatus ORDER BY l_returnflag, l_linestatus
"""
MATERIALIZE_SQL = """
CREATE TEMP TABLE daily_q1 AS
SELECT l_shipdate, l_returnflag, l_linestatus,
       sum(l_quantity) AS sum_qty, sum(l_extendedprice) AS sum_base_price,
       sum(l_extendedprice * (1 - l_discount)) AS sum_disc_price,
       sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) AS sum_charge,
       sum(l_discount) AS sum_discount, count(*) AS row_count
FROM lineitem GROUP BY l_shipdate, l_returnflag, l_linestatus
"""
CANDIDATE_SQL = """
SELECT l_returnflag, l_linestatus,
       sum(sum_qty), sum(sum_base_price), sum(sum_disc_price), sum(sum_charge),
       sum(sum_qty) / sum(row_count), sum(sum_base_price) / sum(row_count),
       sum(sum_discount) / sum(row_count), CAST(sum(row_count) AS BIGINT)
FROM daily_q1 WHERE l_shipdate <= CAST(? AS DATE)
GROUP BY l_returnflag, l_linestatus ORDER BY l_returnflag, l_linestatus
"""


def equivalent_answers(left: list[tuple[object, ...]], right: list[tuple[object, ...]]) -> bool:
    if len(left) != len(right):
        return False
    for left_row, right_row in zip(left, right):
        if len(left_row) != 10 or len(right_row) != 10:
            return False
        for index, (actual, candidate) in enumerate(zip(left_row, right_row)):
            if index in (6, 7, 8):
                if actual is None or candidate is None:
                    if actual is not candidate:
                        return False
                elif not math.isclose(float(actual), float(candidate), rel_tol=1e-12, abs_tol=1e-10):
                    return False
            elif actual != candidate:
                return False
    return True


def answer_digest(answers: list[list[tuple[object, ...]]]) -> str:
    def encode(value: object) -> str:
        if isinstance(value, (decimal.Decimal, datetime.date)):
            return str(value)
        raise TypeError(f"unsupported answer type {type(value).__name__}")
    return digest(json.dumps(answers, default=encode, separators=(",", ":"), allow_nan=False).encode())


def paired_improvement(baseline: list[float], candidate: list[float], seed: int,
                       bootstrap_samples: int = 10000) -> dict[str, object]:
    if len(baseline) != len(candidate) or len(baseline) < 20:
        raise DomainError("system performance requires at least 20 paired observations")
    a, b = np.asarray(baseline, dtype=float), np.asarray(candidate, dtype=float)
    if not np.isfinite(a).all() or not np.isfinite(b).all() or (a <= 0).any() or (b <= 0).any():
        raise DomainError("system times must be positive and finite")
    if not 1000 <= bootstrap_samples <= 100000:
        raise DomainError("bootstrap sample count outside validated limits")
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(a), size=(bootstrap_samples, len(a)))
    reductions = 1.0 - b[indices].mean(axis=1) / a[indices].mean(axis=1)
    lower, upper = np.quantile(reductions, (0.025, 0.975))
    observed = float(1.0 - b.mean() / a.mean())
    return {
        "paired_repeats": len(a), "estimand": "1 - mean(candidate total seconds) / mean(baseline total seconds)",
        "observed_reduction": observed, "ci95": [float(lower), float(upper)],
        "method": "paired percentile bootstrap, resampling whole baseline/candidate pairs",
        "bootstrap_samples": bootstrap_samples, "bootstrap_seed": seed,
        "minimum_required_reduction": 0.10,
        "development_threshold_status": "SUPPORTED" if float(lower) >= 0.10 else "UNCONFIRMED",
        "precision_rule": "A point estimate >=10% is insufficient when the 95% lower bound is below 10%.",
        "scope": "Within this fixed local workload and measurement session; independent repetition remains required.",
    }


def balanced_orders(repeats: int, seed: int) -> list[list[str]]:
    if repeats < 20 or repeats > 100 or repeats % 2:
        raise DomainError("use an even repeat count from 20 to 100")
    orders = [["baseline", "candidate"] for _ in range(repeats // 2)]
    orders += [["candidate", "baseline"] for _ in range(repeats // 2)]
    random.Random(seed).shuffle(orders)
    return orders


def create_database(path: Path, scale_factor: float) -> dict[str, object]:
    if path.exists() or path.is_symlink():
        raise DomainError("DuckDB data output already exists")
    if not math.isfinite(scale_factor) or not 0.01 <= scale_factor <= 0.2:
        raise DomainError("development scale factor must be between 0.01 and 0.2")
    started = time.perf_counter()
    with duckdb.connect(str(path), config={"threads": "1", "memory_limit": "1GB"}) as connection:
        connection.execute("SET autoinstall_known_extensions = false")
        connection.execute("SET autoload_known_extensions = false")
        extension_directory = os.environ.get("DUCKDB_EXTENSION_DIRECTORY")
        if extension_directory is None and Path("/opt/duckdb-extensions").is_dir():
            extension_directory = "/opt/duckdb-extensions"
        if extension_directory is not None:
            connection.execute("SET extension_directory = ?", [extension_directory])
        try:
            connection.execute("LOAD tpch")
        except duckdb.Error as error:
            raise DomainError("tpch extension unavailable; provision it before offline measurement") from error
        connection.execute(f"CALL dbgen(sf = {scale_factor:.17g})")
        query_source = connection.execute("SELECT query FROM tpch_queries() WHERE query_nr = 1").fetchone()[0]
        count = connection.execute("SELECT count(*) FROM lineitem").fetchone()[0]
        extension = connection.execute("SELECT extension_name, extension_version FROM duckdb_extensions() WHERE extension_name='tpch'").fetchone()
        connection.execute("CHECKPOINT")
    elapsed = time.perf_counter() - started
    return {"url": SOURCE_PAGE, "database_sha256": file_digest(path), "database_bytes": path.stat().st_size,
            "lineitem_rows": count, "scale_factor": scale_factor, "tpch_extension": list(extension),
            "query_1_source_sha256": digest(query_source.encode()), "query_1_source": query_source,
            "common_source_generation_seconds": elapsed,
            "source_generation_accounting": "Common one-time source preparation reported separately; timed totals begin at database open.",
            "benchmark_identity": "Reconstructed parameterized Q1 workload; not official TPC-H performance."}


def timed_arm(database: Path, method: str, cutoffs: list[str]) -> tuple[dict[str, float], list[list[tuple[object, ...]]]]:
    started = time.perf_counter()
    connection = duckdb.connect(str(database), read_only=True, config={"threads": "1", "memory_limit": "1GB"})
    try:
        connection.execute("SET autoinstall_known_extensions = false")
        connection.execute("SET autoload_known_extensions = false")
        if method == "candidate":
            connection.execute(MATERIALIZE_SQL)
            query = CANDIDATE_SQL
        elif method == "baseline":
            query = BASELINE_SQL
        else:
            raise DomainError("unknown system method")
        setup_done = time.perf_counter()
        answers = [connection.execute(query, [cutoff]).fetchall() for cutoff in cutoffs]
        query_done = time.perf_counter()
    finally:
        connection.close()
    ended = time.perf_counter()
    return {"setup_seconds": setup_done - started, "query_seconds": query_done - setup_done,
            "cleanup_seconds": ended - query_done, "total_seconds": ended - started}, answers


def run_duckdb(artifact_root: Path, seed: int, scale_factor: float = 0.05,
               repeats: int = 20, workload_cycles: int = 4,
               sink: EventSink | None = None,
               cutoffs: tuple[str, ...] = DEVELOPMENT_CUTOFFS) -> dict[str, object]:
    orders = balanced_orders(repeats, seed)
    if not 1 <= workload_cycles <= 20:
        raise DomainError("workload cycles must be in [1, 20]")
    if not 1 <= len(cutoffs) <= 20:
        raise DomainError("cutoff count must be in [1, 20]")
    for cutoff in cutoffs:
        datetime.date.fromisoformat(cutoff)
    artifact_root.mkdir(mode=0o700)
    database = artifact_root / "development.duckdb"
    source = create_database(database, scale_factor)
    write_new(artifact_root / "source-query-1.sql", source.pop("query_1_source").encode())
    for name, sql in (("baseline.sql", BASELINE_SQL), ("materialize.sql", MATERIALIZE_SQL), ("candidate.sql", CANDIDATE_SQL)):
        write_new(artifact_root / name, sql.encode())
    workload_cutoffs = list(cutoffs) * workload_cycles
    warmup: dict[str, object] = {}
    warm_answers: dict[str, list[list[tuple[object, ...]]]] = {}
    for method in orders[0]:
        warmup[method], warm_answers[method] = timed_arm(database, method, workload_cutoffs)
    if not all(equivalent_answers(a, b) for a, b in zip(warm_answers["baseline"], warm_answers["candidate"])):
        raise DomainError("baseline/candidate warmup answer mismatch")
    emit(sink, "baseline_observation", domain="duckdb", phase="untimed_warmup",
         lineitem_rows=source["lineitem_rows"], equivalence=True)
    rng = random.Random(seed + 1)
    pairs: list[dict[str, object]] = []
    for index, order in enumerate(orders):
        parameters = workload_cutoffs.copy()
        rng.shuffle(parameters)
        times: dict[str, dict[str, float]] = {}
        answers: dict[str, list[list[tuple[object, ...]]]] = {}
        for method in order:
            times[method], answers[method] = timed_arm(database, method, parameters)
        equivalent = all(equivalent_answers(a, b) for a, b in zip(answers["baseline"], answers["candidate"]))
        pair = {"pair": index, "order": order, "cutoffs": parameters, "timings": times,
                "answers_equivalent": equivalent,
                "answer_sha256": {method: answer_digest(value) for method, value in answers.items()}}
        pairs.append(pair)
        emit(sink, "paired_observation", domain="duckdb", **pair)
        if not equivalent:
            write_new(artifact_root / "failed-pairs.json", json_bytes(pairs))
            raise DomainError("baseline/candidate paired answer mismatch; failed observations retained")
    if file_digest(database) != source["database_sha256"]:
        raise DomainError("source database changed during measurement")
    comparison = paired_improvement([pair["timings"]["baseline"]["total_seconds"] for pair in pairs],
                                    [pair["timings"]["candidate"]["total_seconds"] for pair in pairs], seed + 2)
    write_new(artifact_root / "paired-measurements.json", json_bytes(pairs))
    emit(sink, "hypothesis_observation", domain="duckdb", comparison=comparison)
    return {
        "research_question": "Does reusing daily partial aggregates reduce complete Q1-derived workload cost after paying preparation costs?",
        "hypothesis": "One daily aggregation table amortizes over repeated cutoff queries and reduces total time by at least 10%.",
        "source": source, "development_parameters": list(cutoffs),
        "queries_per_arm": len(workload_cutoffs), "workload_cycles": workload_cycles,
        "baseline": "Fresh connection; direct original-column aggregate for every cutoff",
        "candidate": "Fresh connection; recreate daily aggregates; reconstruct exact sums/counts and corresponding averages",
        "sql_sha256": {name: file_digest(artifact_root / name) for name in ("baseline.sql", "materialize.sql", "candidate.sql")},
        "accounting": "Connection/configuration, per-arm materialization, every query and connection cleanup are timed. Source generation and warmups are reported separately.",
        "warmup": warmup, "warmup_in_inference": False, "cache_scope": "Warm OS cache, fresh connection and temporary tables per arm",
        "paired_measurements": pairs, "comparison": comparison,
        "median_total_seconds": {method: statistics.median(pair["timings"][method]["total_seconds"] for pair in pairs)
                                  for method in ("baseline", "candidate")},
        "verification": {"all_answers_equivalent": True, "decimal_sums_keys_counts": "exact equality",
                         "floating_average_tolerance": {"relative": 1e-12, "absolute": 1e-10},
                         "source_database_unchanged": True, "independent_repetition": "REQUIRED_SEPARATE_EXECUTION",
                         "new_hidden_parameters": "NOT_EVALUATED"},
        "limitations": ["Q1-derived repeated aggregation workload only, not all 22 TPC-H queries or official benchmark performance.",
                        "Bootstrap precision is conditional on these paired runs; it does not replace a separate measurement session.",
                        "Performance inference requires external controller serialization and resource receipts."],
    }
