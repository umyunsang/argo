#!/usr/bin/env python3
"""T1' adapter: ScienceAgentBench deterministic execution subset.

Verifies that the benchmark is present, licensed (MIT), and structurally intact
with deterministic programmatic verifiers (no LLM judges) before any episode runs.

Licence: MIT (sha256 93b43d692b033b76129504448695bfe76ef22d18b11e51352bfab4b5622e5aaa).
Source: repo github.com/OSU-NLP-Group/ScienceAgentBench, paper arXiv 2410.05080.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, re, shutil, subprocess, sys, tempfile
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
    """Prepares an isolated workspace for a task, wiping target_dir and ensuring oracle isolation."""
    # §1.3 (c): completely wipe and recreate target_dir to prevent cross-arm state leakage
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    
    csv_file = benchmark_dir / "ScienceAgentBench.csv"
    if not csv_file.exists():
        raise PreconditionUnmet("ScienceAgentBench.csv missing from benchmark directory")
    
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        task_row = next((r for r in reader if int(r["instance_id"]) == task_id), None)
    
    if not task_row:
        raise PreconditionUnmet(f"Task {task_id} not found in ScienceAgentBench.csv")
    
    # Copy dataset files only
    tree_header = task_row["dataset_folder_tree"].splitlines()[0]
    folder_name = tree_header.replace("|-- ", "").replace("/", "").strip()
    src_dataset_dir = benchmark_dir / "benchmark" / "datasets" / folder_name
    if not src_dataset_dir.is_dir():
        raise PreconditionUnmet(f"Dataset dir {src_dataset_dir} does not exist")
    
    dst_dataset_dir = target_dir / "benchmark" / "datasets" / folder_name
    dst_dataset_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_dataset_dir, dst_dataset_dir)
    
    # §1.2: TASK.md MUST include all 5 essential fields from ScienceAgentBench.csv
    task_md = f"""# Task {task_id}: {task_row['domain']}

## Task Instruction
{task_row['task_inst']}

## Expected Output File
Save your output to: `{task_row['output_fname']}`

## Domain Knowledge
{task_row['domain_knowledge']}

## Dataset Folder Structure
```
{task_row['dataset_folder_tree']}
```

## Dataset Preview
```
{task_row['dataset_preview']}
```
"""
    (target_dir / "TASK.md").write_text(task_md, encoding="utf-8")
    
    return {
        "task_id": task_id,
        "domain": task_row["domain"],
        "output_fname": task_row["output_fname"],
        "eval_script_name": task_row["eval_script_name"],
        "workspace": str(target_dir)
    }

def verify_output(task_id: int, benchmark_dir: Path, workspace_dir: Path) -> tuple[int, str]:
    """Runs evaluation OUTSIDE the workspace, copying only the single task's gold file.
    
    Returns:
      (ordinal_score, detail)
      where ordinal_score is in {0, 1, 2}:
        0: missing output or invalid execution
        1: valid output generated, but failed task criteria (score 0)
        2: task criteria passed (score 1)
    """
    csv_file = benchmark_dir / "ScienceAgentBench.csv"
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        task_row = next((r for r in reader if int(r["instance_id"]) == task_id), None)
        
    eval_script_name = task_row["eval_script_name"]
    eval_script = benchmark_dir / "benchmark" / "eval_programs" / eval_script_name
    gold_dir = benchmark_dir / "benchmark" / "eval_programs" / "gold_results"
    
    expected_out = workspace_dir / task_row["output_fname"]
    if not expected_out.is_file():
        return 0, json.dumps({"ordinal_score": 0, "status": "missing_output", "expected": task_row["output_fname"]})
        
    # Read script to find the specific gold file needed
    script_text = eval_script.read_text(encoding="utf-8", errors="ignore")
    gold_matches = re.findall(r"gold_results/([a-zA-Z0-9_\-\.]+)", script_text)
    
    # Execute verification in an isolated temporary directory OUTSIDE the workspace
    with tempfile.TemporaryDirectory(prefix=f"t1_eval_{task_id}_") as eval_tmp:
        tmp_dir = Path(eval_tmp)
        
        # Copy agent's pred_results directory into temporary eval dir
        tmp_pred = tmp_dir / "pred_results"
        tmp_pred.mkdir(parents=True, exist_ok=True)
        shutil.copy(expected_out, tmp_dir / task_row["output_fname"])
        
        # Setup eval_programs with ONLY the required gold file(s)
        tmp_eval_dir = tmp_dir / "benchmark" / "eval_programs"
        tmp_eval_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(eval_script, tmp_eval_dir / eval_script_name)
        
        tmp_gold_dir = tmp_eval_dir / "gold_results"
        tmp_gold_dir.mkdir(parents=True, exist_ok=True)
        for gm in gold_matches:
            src_gold = gold_dir / gm
            if src_gold.is_file():
                shutil.copy(src_gold, tmp_gold_dir / gm)
                
        # Run eval script in tmp_dir cwd
        try:
            res = subprocess.run([sys.executable, str(tmp_eval_dir / eval_script_name)],
                                 cwd=tmp_dir, capture_output=True, text=True, timeout=120)
            out = res.stdout.strip()
            err = res.stderr.strip()
            
            if res.returncode != 0:
                # Output file existed, but evaluation script crashed -> level 1
                return 1, json.dumps({"ordinal_score": 1, "status": "eval_crash", "error": err[:200]})
                
            # Parse raw 0/1 score
            try:
                score_part = out.split(",")[0].replace("(", "").strip()
                raw_score = int(score_part)
            except Exception:
                raw_score = 1 if "1," in out or out.startswith("1") else 0
                
            ordinal_score = 2 if raw_score == 1 else 1
            return ordinal_score, json.dumps({"ordinal_score": ordinal_score, "raw_score": raw_score, "stdout": out[:300]})
        except subprocess.TimeoutExpired:
            return 1, json.dumps({"ordinal_score": 1, "status": "eval_timeout"})
