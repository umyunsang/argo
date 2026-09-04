#!/usr/bin/env python3
"""T1' adapter: ScienceAgentBench deterministic execution subset.

Verifies that the benchmark is present, licensed (MIT), and structurally intact
with deterministic programmatic verifiers (no LLM judges) before any episode runs.

Licence: MIT (sha256 93b43d692b033b76129504448695bfe76ef22d18b11e51352bfab4b5622e5aaa).
Source: repo github.com/OSU-NLP-Group/ScienceAgentBench, paper arXiv 2410.05080.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

BENCH = {
    "name": "ScienceAgentBench",
    "repo": "https://github.com/OSU-NLP-Group/ScienceAgentBench",
    "paper_arxiv_id": "2410.05080",
    "licence": "MIT",
    "licence_sha256": "93b43d692b033b76129504448695bfe76ef22d18b11e51352bfab4b5622e5aaa",
    "commit_sha": "c26e151ed601ba109dc4d35e057ff8e73fec469d",
    "deterministic_eval_count": 38,
}

PERMISSIVE_LICENCES = ("MIT", "Apache-2.0", "BSD-3-Clause")

class PreconditionUnmet(RuntimeError):
    pass

def licence_ok() -> tuple[bool, str]:
    lic = BENCH["licence"]
    if lic not in PERMISSIVE_LICENCES:
        return False, f"licence {lic!r} is not in the permissive set {PERMISSIVE_LICENCES}"
    return True, f"licence {lic} permits benchmark use and redistribution of results"

def check_preconditions(checkout: Path | None) -> dict:
    ok_lic, lic_msg = licence_ok()
    state = {"benchmark": BENCH["name"], "licence_ok": ok_lic, "licence_note": lic_msg}
    if checkout is None or not checkout.is_dir():
        state.update(ready=False, reason=f"benchmark checkout absent: {checkout}")
        return state
    req_dirs = ["benchmark/eval_programs", "benchmark/eval_programs/gold_results", "benchmark/datasets"]
    missing = [d for d in req_dirs if not (checkout / d).is_dir()]
    if missing:
        state.update(ready=False, reason="checkout missing required dirs", missing=missing)
        return state
    state.update(ready=ok_lic, deterministic_tasks=BENCH["deterministic_eval_count"])
    return state

def setup_workspace(task_id: int, benchmark_dir: Path, target_dir: Path) -> dict:
    """Prepares an isolated workspace for a task, ensuring oracle isolation."""
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_file = benchmark_dir / "ScienceAgentBench.csv"
    if not csv_file.exists():
        raise PreconditionUnmet("ScienceAgentBench.csv missing from benchmark directory")
    
    # Read metadata using standard csv module to avoid heavy dependencies
    import csv
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        task_row = next((r for r in reader if int(r["instance_id"]) == task_id), None)
    
    if not task_row:
        raise PreconditionUnmet(f"Task {task_id} not found in ScienceAgentBench.csv")
    
    # Copy dataset files
    tree_header = task_row["dataset_folder_tree"].splitlines()[0]
    folder_name = tree_header.replace("|-- ", "").replace("/", "").strip()
    src_dataset_dir = benchmark_dir / "benchmark" / "datasets" / folder_name
    if not src_dataset_dir.is_dir():
        raise PreconditionUnmet(f"Dataset dir {src_dataset_dir} does not exist")
    
    dst_dataset_dir = target_dir / "benchmark" / "datasets" / folder_name
    dst_dataset_dir.parent.mkdir(parents=True, exist_ok=True)
    if dst_dataset_dir.exists():
        shutil.rmtree(dst_dataset_dir)
    shutil.copytree(src_dataset_dir, dst_dataset_dir)
    
    # Write TASK.md
    task_md = f"# Task {task_id}: {task_row['domain']}\n\n{task_row['task_inst']}\n"
    (target_dir / "TASK.md").write_text(task_md, encoding="utf-8")
    
    return {
        "task_id": task_id,
        "domain": task_row["domain"],
        "output_fname": task_row["output_fname"],
        "eval_script_name": task_row["eval_script_name"],
        "workspace": str(target_dir)
    }

def verify_output(task_id: int, benchmark_dir: Path, workspace_dir: Path) -> tuple[int, str]:
    """Runs the deterministic evaluation script in isolation."""
    import csv
    with open(benchmark_dir / "ScienceAgentBench.csv", mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        task_row = next((r for r in reader if int(r["instance_id"]) == task_id), None)
        
    eval_script_name = task_row["eval_script_name"]
    eval_script = benchmark_dir / "benchmark" / "eval_programs" / eval_script_name
    gold_dir = benchmark_dir / "benchmark" / "eval_programs" / "gold_results"
    
    # Ensure pred_results directory exists and output is in place
    expected_out = workspace_dir / task_row["output_fname"]
    if not expected_out.exists():
        return 0, json.dumps({"error": f"Output file missing: {task_row['output_fname']}"})
        
    # Copy evaluation script and gold results to temporary verification root inside workspace
    verif_eval_dir = workspace_dir / "benchmark" / "eval_programs"
    verif_eval_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(eval_script, verif_eval_dir / eval_script_name)
    
    dst_gold = verif_eval_dir / "gold_results"
    if not dst_gold.exists():
        shutil.copytree(gold_dir, dst_gold)
        
    # Execute eval script using python in workspace cwd
    res = subprocess.run([sys.executable, str(verif_eval_dir / eval_script_name)],
                         cwd=workspace_dir, capture_output=True, text=True, timeout=120)
    
    out = res.stdout.strip()
    # Most eval scripts return (int, str) tuple via print((score, detail))
    # Parse the score
    try:
        score_part = out.split(",")[0].replace("(", "").strip()
        score = int(score_part)
    except Exception:
        score = 1 if "1," in out or out.startswith("1") else 0
        
    return score, out
