#!/usr/bin/env python3
"""Failing-first tests for T1 evaluator failure and ordinal-score semantics."""
from __future__ import annotations

import csv
import json
import tempfile
from pathlib import Path

import run_t1

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + (f" :: {detail}" if not ok else ""))
    if not ok:
        FAILURES.append(name)


def make_benchmark(root: Path) -> tuple[Path, Path]:
    benchmark = root / "benchmark-source"
    dataset = benchmark / "benchmark/datasets/fixture"
    eval_dir = benchmark / "benchmark/eval_programs"
    gold = eval_dir / "gold_results"
    dataset.mkdir(parents=True)
    gold.mkdir(parents=True)
    (dataset / "input.csv").write_text("x\n1\n", encoding="utf-8")
    (gold / "answer.txt").write_text("gold", encoding="utf-8")
    fields = ["instance_id", "domain", "task_inst", "output_fname", "domain_knowledge",
              "dataset_folder_tree", "dataset_preview", "eval_script_name"]
    row = {"instance_id": "999", "domain": "Fixture", "task_inst": "produce output",
           "output_fname": "pred_results/out.csv", "domain_knowledge": "fixture knowledge",
           "dataset_folder_tree": "|-- fixture/\n    |-- input.csv",
           "dataset_preview": "x\n1", "eval_script_name": "fixture_eval.py"}
    with (benchmark / "ScienceAgentBench.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)
    workspace = root / "workspace"
    run_t1.setup_workspace(999, benchmark, workspace)
    out = workspace / "pred_results/out.csv"
    out.parent.mkdir(parents=True)
    out.write_text("prediction\n0\n", encoding="utf-8")
    return benchmark, workspace


def set_evaluator(benchmark: Path, code: str) -> None:
    path = benchmark / "benchmark/eval_programs/fixture_eval.py"
    path.write_text("# gold_results/answer.txt\n" + code + "\n", encoding="utf-8")


def detail(raw: str) -> dict:
    return json.loads(raw)


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        benchmark, workspace = make_benchmark(Path(td))

        set_evaluator(benchmark, 'print("0, wrong result")')
        score, raw = run_t1.verify_output(999, benchmark, workspace)
        obj = detail(raw)
        check("valid wrong result scores one", score == 1, raw)
        check("valid wrong result remains admissible", obj.get("inadmissible_execution") is False, raw)
        check("valid wrong result has exact status", obj.get("status") == "valid_result", raw)

        set_evaluator(benchmark, 'print("1, correct result")')
        score, raw = run_t1.verify_output(999, benchmark, workspace)
        obj = detail(raw)
        check("valid correct result scores two", score == 2, raw)
        check("valid correct result remains admissible", obj.get("inadmissible_execution") is False, raw)

        set_evaluator(benchmark, 'raise RuntimeError("fixture crash")')
        score, raw = run_t1.verify_output(999, benchmark, workspace)
        obj = detail(raw)
        check("evaluator crash scores zero", score == 0, raw)
        check("evaluator crash is inadmissible", obj.get("inadmissible_execution") is True, raw)
        check("evaluator crash reason is exact", obj.get("status") == "evaluator_crash", raw)

        set_evaluator(benchmark, "import sys; sys.exit(7)")
        score, raw = run_t1.verify_output(999, benchmark, workspace)
        obj = detail(raw)
        check("evaluator nonzero exit scores zero", score == 0, raw)
        check("nonzero exit code is recorded", obj.get("exit_code") == 7, raw)

        set_evaluator(benchmark, 'print("not a score")')
        score, raw = run_t1.verify_output(999, benchmark, workspace)
        obj = detail(raw)
        check("parse failure scores zero", score == 0, raw)
        check("parse failure is inadmissible", obj.get("inadmissible_execution") is True, raw)
        check("parse failure reason is exact", obj.get("status") == "output_parse_failure", raw)

        output = workspace / "pred_results/out.csv"
        output.unlink()
        score, raw = run_t1.verify_output(999, benchmark, workspace)
        obj = detail(raw)
        check("missing output scores zero", score == 0, raw)
        check("missing output is inadmissible", obj.get("inadmissible_execution") is True, raw)
        check("missing output reason is exact", obj.get("status") == "missing_output", raw)
        output.write_text("prediction\n0\n", encoding="utf-8")

        timeout_configured = hasattr(run_t1, "EVALUATOR_TIMEOUT_SECONDS")
        check("evaluator timeout is configurable for deterministic fixtures", timeout_configured)
        if timeout_configured:
            old_timeout = run_t1.EVALUATOR_TIMEOUT_SECONDS
            run_t1.EVALUATOR_TIMEOUT_SECONDS = 0.02
            try:
                set_evaluator(benchmark, 'import time; time.sleep(1); print("1, late")')
                score, raw = run_t1.verify_output(999, benchmark, workspace)
            finally:
                run_t1.EVALUATOR_TIMEOUT_SECONDS = old_timeout
            obj = detail(raw)
            check("evaluator timeout scores zero", score == 0, raw)
            check("evaluator timeout is inadmissible", obj.get("inadmissible_execution") is True, raw)
            check("evaluator timeout reason is exact", obj.get("status") == "evaluator_timeout", raw)

        set_evaluator(benchmark, 'import os; print("0, cwd=" + os.getcwd())')
        score, raw = run_t1.verify_output(999, benchmark, workspace)
        obj = detail(raw)
        check("evaluator subprocess runs outside workspace",
              str(workspace.resolve()) not in obj.get("stdout", "") and "t1_eval_999_" in obj.get("stdout", ""), raw)
        check("gold is not copied into agent workspace", not list(workspace.rglob("*gold*")))

    print(f"\n{len(FAILURES)} failing checks" if FAILURES else "\nAll checks passed.")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
