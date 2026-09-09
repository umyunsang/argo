"""Data-integrity and solver fixtures; these tests are not research campaigns."""
from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import duckdb
import numpy as np

from experiments.project_research.domains.cli import main
from experiments.project_research.domains.common import DomainError, digest, json_bytes, write_new
from experiments.project_research.domains.custody import prepare_settings
from experiments.project_research.domains.diffusion import check_solution, make_problem, solve_method
from experiments.project_research.domains.duckdb_workload import (
    BASELINE_SQL, CANDIDATE_SQL, DEVELOPMENT_CUTOFFS, MATERIALIZE_SQL,
    balanced_orders, equivalent_answers, paired_improvement,
)
from experiments.project_research.domains.wine import (
    WineRow, disjoint_roots, encode_rows, load_worker, partition_rows, score_predictions,
)


def sample_rows() -> list[WineRow]:
    rows = []
    for color in ("red", "white"):
        for index in range(150):
            offset = index + (1000 if color == "white" else 0)
            rows.append(WineRow(f"{color}-{index}", color, tuple(str(offset + j / 10) for j in range(11)), str(4 + index % 4)))
    return rows


class WineIntegrityTests(unittest.TestCase):
    def test_all_partitions_keep_duplicate_inputs_together_across_color_and_target(self) -> None:
        rows = sample_rows()
        first = rows[0]
        cross_color = WineRow("different-color-same-input", "white", first.features, "9")
        formatting = WineRow("same-numbers-different-format", "red", tuple(f"{float(value):.3f}" for value in first.features), "2")
        split = partition_rows([*rows, cross_color, formatting], 42)
        locations = {row.row_id: name for name, entries in split.items() for row in entries}
        self.assertEqual(locations[first.row_id], locations[cross_color.row_id])
        self.assertEqual(locations[first.row_id], locations[formatting.row_id])
        groups = {name: {row.group_id for row in entries} for name, entries in split.items()}
        for first_name, first_groups in groups.items():
            for second_name, second_groups in groups.items():
                if first_name != second_name:
                    self.assertFalse(first_groups & second_groups)
        self.assertEqual(sum(len(entries) for entries in split.values()), len(rows) + 2)

    def test_custody_rejects_existing_and_nested_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            with self.assertRaises(DomainError):
                disjoint_roots(root / "worker", root / "worker" / "evaluator")
            (root / "worker").mkdir()
            with self.assertRaises(DomainError):
                disjoint_roots(root / "worker", root / "evaluator")
            (root / "link").symlink_to(root, target_is_directory=True)
            with self.assertRaises(DomainError):
                disjoint_roots(root / "link" / "worker2", root / "evaluator")

    def test_worker_loader_detects_leakage_and_unexpected_holdout_files(self) -> None:
        rows = sample_rows()
        split = partition_rows(rows, 42)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            train = encode_rows(split["train"])
            dev = encode_rows([*split["dev"], split["train"][0]])
            for name, data in (("train.csv", train), ("dev.csv", dev)):
                write_new(root / name, data)
            manifest = {"schema_version": "project-research-wine-worker-data/v1",
                        "files": {"train.csv": {"sha256": digest(train)}, "dev.csv": {"sha256": digest(dev)}}}
            write_new(root / "manifest.json", json_bytes(manifest))
            with self.assertRaisesRegex(DomainError, "crosses train/dev"):
                load_worker(root)
            write_new(root / "final.csv", encode_rows(split["final"]))
            with self.assertRaisesRegex(DomainError, "only train/dev"):
                load_worker(root)

    def test_equal_color_mae_differs_from_row_weighting(self) -> None:
        rows = [WineRow("r", "red", ("1",) * 11, "1"),
                WineRow("w1", "white", ("2",) * 11, "2"),
                WineRow("w2", "white", ("3",) * 11, "2")]
        score = score_predictions(rows, np.zeros(3))
        self.assertEqual(score["red_mae"], 1)
        self.assertEqual(score["white_mae"], 2)
        self.assertEqual(score["equal_weight_mae"], 1.5)
        self.assertAlmostEqual(score["row_weight_mae"], 5 / 3)
        with self.assertRaises(DomainError):
            score_predictions(rows, np.array([0.0, np.nan, 0.0]))


class SystemIntegrityTests(unittest.TestCase):
    def test_paired_precision_does_not_promote_uncertain_ten_percent_estimate(self) -> None:
        stable = paired_improvement([1.0] * 20, [0.8] * 20, 7)
        self.assertEqual(stable["development_threshold_status"], "SUPPORTED")
        uncertain = paired_improvement([1.0] * 20, [0.5] * 10 + [1.25] * 10, 7)
        self.assertGreater(uncertain["observed_reduction"], 0.10)
        self.assertLess(uncertain["ci95"][0], 0.10)
        self.assertEqual(uncertain["development_threshold_status"], "UNCONFIRMED")
        with self.assertRaises(DomainError):
            paired_improvement([1.0] * 19, [0.8] * 19, 7)
        with self.assertRaises(DomainError):
            paired_improvement([1.0] * 20, [float("nan")] * 20, 7)

    def test_order_is_balanced_and_reproducible(self) -> None:
        orders = balanced_orders(20, 7)
        self.assertEqual(sum(order[0] == "baseline" for order in orders), 10)
        self.assertEqual(orders, balanced_orders(20, 7))
        self.assertNotEqual(orders, balanced_orders(20, 8))

    def test_aggregation_preserves_exact_sums_and_average_semantics(self) -> None:
        with duckdb.connect(":memory:", config={"threads": "1"}) as connection:
            connection.execute("""CREATE TABLE lineitem(
                l_returnflag VARCHAR, l_linestatus VARCHAR, l_shipdate DATE,
                l_quantity DECIMAL(15,2), l_extendedprice DECIMAL(15,2),
                l_discount DECIMAL(15,2), l_tax DECIMAL(15,2))""")
            connection.execute("""INSERT INTO lineitem VALUES
                ('A','F','1993-01-01',3,11.13,0.03,0.07),
                ('A','F','1993-01-01',5,10.01,0.04,0.08),
                ('R','F','1994-01-01',7,20.17,0.09,0.05),
                ('A','F','1995-01-01',9,30.23,0.05,0.01),
                ('N','O','1998-01-01',1,40.31,0.07,0.00)""")
            connection.execute(MATERIALIZE_SQL)
            for cutoff in ("1992-01-01", "1993-12-01", "1994-12-01", "1998-09-02"):
                original = connection.execute(BASELINE_SQL, [cutoff]).fetchall()
                candidate = connection.execute(CANDIDATE_SQL, [cutoff]).fetchall()
                self.assertTrue(equivalent_answers(original, candidate), cutoff)
            original = connection.execute(BASELINE_SQL, ["1998-09-02"]).fetchall()
            self.assertEqual(sum(row[-1] for row in original), 5)
            connection.execute("UPDATE daily_q1 SET sum_qty = sum_qty + 1")
            wrong = connection.execute(CANDIDATE_SQL, ["1998-09-02"]).fetchall()
            self.assertFalse(equivalent_answers(original, wrong))

    def test_final_and_future_settings_are_separate_and_do_not_print_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "settings"
            public = prepare_settings(root, 42)
            final = json.loads((root / "final.json").read_text())
            future = json.loads((root / "future.json").read_text())
            final_dates = set(final["duckdb"]["cutoffs"])
            future_dates = set(future["duckdb"]["cutoffs"])
            self.assertFalse(final_dates & future_dates)
            self.assertFalse(final_dates & set(DEVELOPMENT_CUTOFFS))
            self.assertFalse(future_dates & set(DEVELOPMENT_CUTOFFS))
            self.assertFalse(any(value in json.dumps(public) for value in final_dates | future_dates))


class NumericalIntegrityTests(unittest.TestCase):
    def test_actual_solvers_match_independent_stencil_and_known_solution(self) -> None:
        matrix, stencil, truth, rhs = make_problem(8, 0.1, math.pi / 6, 2, 42)
        for method in ("sparse_direct", "jacobi_cg", "amg_cg"):
            solution, observation = solve_method(matrix, rhs, method, 42)
            self.assertTrue(observation["solver_success"])
            self.assertGreater(observation["setup_seconds"], 0)
            self.assertGreater(observation["solve_seconds"], 0)
            for index in range(2):
                self.assertTrue(check_solution(stencil, (8, 8), rhs[:, index], truth[:, index], solution[:, index])["passed"])

    def test_independent_check_rejects_corrupted_solution(self) -> None:
        _matrix, stencil, truth, rhs = make_problem(8, 0.1, math.pi / 6, 1, 42)
        corrupted = truth[:, 0].copy()
        corrupted[3] += 1
        check = check_solution(stencil, (8, 8), rhs[:, 0], truth[:, 0], corrupted)
        self.assertFalse(check["passed"])
        self.assertGreater(check["relative_residual"], 1e-9)
        self.assertGreater(check["relative_solution_error"], 1e-7)


class EvidenceFailureTests(unittest.TestCase):
    def test_failed_attempt_is_recorded_and_cannot_overwrite_previous_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "failed.json"
            with patch("experiments.project_research.domains.cli.environment", return_value={"matches_pins": False}):
                self.assertEqual(main(["diffusion", "--output", str(output)]), 1)
            evidence = json.loads(output.read_text())
            self.assertEqual(evidence["status"], "FAILED")
            self.assertFalse(evidence["autonomous_campaign"])
            self.assertTrue(evidence["development_only"])
            self.assertEqual(evidence["failure"]["type"], "DomainError")
            self.assertEqual(evidence["command"][1:4], ["-m", "experiments.project_research.domains.cli", "diffusion"])
            journal = output.with_suffix(".events.jsonl").read_text()
            self.assertIn('"event": "failed"', journal)
            prior = output.read_bytes()
            with self.assertRaises(SystemExit):
                main(["diffusion", "--output", str(output)])
            self.assertEqual(output.read_bytes(), prior)


if __name__ == "__main__":
    unittest.main()
