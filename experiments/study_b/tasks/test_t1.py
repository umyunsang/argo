#!/usr/bin/env python3
"""Tests for the T1' ScienceAgentBench adapter (v2)."""
import sys, tempfile, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_t1

F = []
def check(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (f" :: {d}" if not ok else ""))
    if not ok: F.append(n)

def main():
    check("licence is recorded and permissive", run_t1.licence_ok()[0] is True)
    check("licence note names the licence", "MIT" in run_t1.licence_ok()[1])

    s = run_t1.check_preconditions(None)
    check("absent checkout is not ready", s["ready"] is False)

    sab_dir = Path.home() / ".cache" / "ScienceAgentBench"
    if sab_dir.exists():
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ws_dir = root / "ws"
            
            # Setup workspace
            meta = run_t1.setup_workspace(1, sab_dir, ws_dir)
            check("workspace created", ws_dir.is_dir())
            
            # §1.2 Check all 5 fields in TASK.md
            task_md = (ws_dir / "TASK.md").read_text()
            check("TASK.md contains task_inst", "Train a multitask model" in task_md)
            check("TASK.md contains output_fname", "pred_results/clintox_test_pred.csv" in task_md)
            check("TASK.md contains domain_knowledge", "Domain Knowledge" in task_md)
            check("TASK.md contains dataset_folder_tree", "clintox_test.csv" in task_md)
            check("TASK.md contains dataset_preview", "smiles,FDA_APPROVED,CT_TOX" in task_md)
            
            # §1.3 Check oracle isolation (no gold files in workspace)
            check("workspace has no gold_results", not (ws_dir / "benchmark/eval_programs").exists())
            check("workspace has no gold files", len(list(ws_dir.rglob("*gold*"))) == 0)
            
            # §1.3 (c) Setup wipes existing directory completely
            (ws_dir / "stale_file.txt").write_text("leak")
            run_t1.setup_workspace(1, sab_dir, ws_dir)
            check("setup_workspace wipes previous contents", not (ws_dir / "stale_file.txt").exists())
            
            # §2.1 Ordinal endpoint verification: Level 0 (missing file)
            score0, _ = run_t1.verify_output(1, sab_dir, ws_dir)
            check("missing output gives score 0", score0 == 0)
            
            # Workspace remains clean after verify_output
            check("verify_output does not write into workspace", not (ws_dir / "benchmark/eval_programs").exists())
            
            # Level 1 (file exists, but incorrect)
            pred_dir = ws_dir / "pred_results"
            pred_dir.mkdir(parents=True)
            (pred_dir / "clintox_test_pred.csv").write_text("dummy,columns\n1,2")
            score1, det1 = run_t1.verify_output(1, sab_dir, ws_dir)
            check("invalid/wrong output gives score 1", score1 == 1)
            check("verify_output did not leak gold into workspace", not (ws_dir / "benchmark/eval_programs").exists())

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
