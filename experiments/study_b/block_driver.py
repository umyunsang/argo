#!/usr/bin/env python3
"""Driver script to execute Study B screening block sequentially across seeds and arms.

Order: for each seed in [start_seed..end_seed]:
         for each arm in [B0, B1, B2]:
           create node if absent, run, wait, harvest, redact, update ledger, check cap.
"""
import os, sys, json, time, shlex, subprocess, re, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = Path.home() / ".local/share/openresearch/local-runs"
PROJ = "0dd58a66-1f75-45ac-9eb9-020f88411240"
PARENT = "c11c76ef-640e-4de7-8046-0507b163fa71"
RUNS_PREF = "/Users/um-yunsang/.local/share/openresearch/local-runs/"
CAP = 48.47

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def get_cumulative_spend():
    cl_path = ROOT / "paper/supervisor/cost-ledger.md"
    text = cl_path.read_text(encoding="utf-8")
    m = re.findall(r"\*\*\$([0-9]+\.[0-9]+)\*\*", text)
    if m:
        return float(m[-1])
    return 0.840625

def launch_episode(arm, task, seed):
    stage_dir = f"paper/experiments/screening/block/{arm}_{task}"
    out_path = f"{stage_dir}/seed{seed}-receipt.json"
    title = f"study-b/block/{arm}/{task}/s{seed}"
    run_cmd_str = (
        f'env ORX_RUN_ID=$(basename $(dirname "$PWD")) ORX_PROJECT_ID={PROJ} '
        f'/usr/bin/python3 experiments/study_b/run_block.py '
        f'--arm {arm} --task {task} --seeds 1 --out {out_path}'
    )
    desc = f"Study B screening block: arm {arm}, task {task}, seed {seed}."
    
    # Create experiment node
    cmd = (f"orx create-experiment {PROJ} --parent {PARENT} --title {shlex.quote(title)} "
           f"--description {shlex.quote(desc)} --run-command {shlex.quote(run_cmd_str)}")
    rc, out, err = run_cmd(cmd)
    m = [x for x in re.findall(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", out) if x != PARENT]
    if not m:
        raise RuntimeError(f"Failed to create node for {arm} s{seed}: {out} {err}")
    node_id = m[0]
    
    # Run node
    rc, out, err = run_cmd(f"orx exp run {node_id} --backend local")
    m_run = re.search(r"([0-9a-f-]{36})", out)
    if not m_run:
        raise RuntimeError(f"Failed to run node {node_id}: {out} {err}")
    run_id = m_run.group(1)
    return node_id, run_id, out_path

def wait_for_run(run_id, timeout_sec=600):
    t0 = time.time()
    ec_file = RUNS / run_id / "exit_code"
    while time.time() - t0 < timeout_sec:
        if ec_file.is_file():
            return int(ec_file.read_text().strip())
        time.sleep(5)
    raise TimeoutError(f"Run {run_id} timed out after {timeout_sec}s")

def harvest_episode(arm, task, seed, node_id, run_id, out_rel):
    src_repo = RUNS / run_id / "repo"
    receipt_file = src_repo / out_rel
    if not receipt_file.is_file():
        raise FileNotFoundError(f"Receipt {receipt_file} not found in run {run_id}")
    rcp = json.loads(receipt_file.read_text(encoding="utf-8"))
    
    # Redact and copy transcripts
    ddir = ROOT / f"experiments/study_b/receipts/block_{run_id[:8]}_{arm}_{task}_s{seed}"
    ddir.mkdir(parents=True, exist_ok=True)
    src_trans = src_repo / f"paper/experiments/screening/block/{arm}_{task}/{arm}_{task}/seed0"
    if not src_trans.exists():
        src_trans = src_repo / f"paper/experiments/screening/block/{arm}_{task}/seed0"
    
    counts = {}
    if src_trans.is_dir():
        for f in src_trans.iterdir():
            if not f.is_file(): continue
            t = f.read_text(errors="replace")
            n = len(re.findall(r"local/share/openresearch/local", t))
            t = t.replace(RUNS_PREF, "<RUNS_ROOT>/").replace("local/share/openresearch/local-runs/", "<RUNS_ROOT>/").replace("local/share/openresearch/local", "<RUNS_ROOT>")
            (ddir / f.name).write_text(t, encoding="utf-8")
            counts[f.name] = n
            
    usage_file = src_repo / f"paper/experiments/screening/block/{arm}_{task}/usage_{arm}_{task}.json"
    if usage_file.is_file():
        shutil_copy = ddir / "usage.json"
        shutil_copy.write_text(usage_file.read_text(encoding="utf-8"), encoding="utf-8")
        
    (ddir / "REDACTION.json").write_text(json.dumps({
        "replaced": "substrate runs root prefix and streamed fragments -> <RUNS_ROOT>",
        "counts": counts,
        "source_run_id": run_id
    }, indent=2) + "\n")
    
    rcp["provider_usage_log"] = str((ddir / "usage.json").relative_to(ROOT))
    rcp["episode_transcripts_dir"] = str(ddir.relative_to(ROOT))
    for e in rcp["episodes"]:
        e["transcript_path"] = str((ddir / "transcript.txt").relative_to(ROOT))
    rcp["orx_experiment_id"] = node_id
    rcp["stage"] = "screening_block_n40"
    
    # Fill commit from sqlite
    db_path = Path.home() / ".local/share/openresearch/orx.db"
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    c_sha = con.execute("select commit_sha from runs where id=?", (run_id,)).fetchone()
    con.close()
    if c_sha and c_sha[0]:
        rcp["node_commit"] = rcp["harness_commit"] = c_sha[0]
        
    dest_path = ROOT / out_rel
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(json.dumps(rcp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rcp

def run_next_seed(seed, task="T3"):
    print(f"=== Starting seed {seed} on task {task} ===", flush=True)
    spend = get_cumulative_spend()
    if spend >= CAP:
        print(f"Cap reached: ${spend} >= ${CAP}. Halting.", flush=True)
        return False
        
    results = {}
    for arm in ("B0", "B1", "B2"):
        node_id, run_id, out_rel = launch_episode(arm, task, seed)
        print(f"Launched {arm} seed {seed}: node {node_id}, run {run_id}. Waiting...", flush=True)
        ec = wait_for_run(run_id)
        if ec != 0:
            print(f"Run {run_id} failed with exit code {ec}", flush=True)
            return False
        rcp = harvest_episode(arm, task, seed, node_id, run_id, out_rel)
        ep = rcp["episodes"][0]
        cost = ep.get("cost_usd", 0.0)
        n_pass = ep.get("score", {}).get("n_pass", 0)
        results[arm] = {"cost": cost, "n_pass": n_pass, "run_id": run_id}
        print(f"Harvested {arm} seed {seed}: cost=${cost:.6f}, pass={n_pass}/5", flush=True)
        
    triple_cost = sum(r["cost"] for r in results.values())
    new_spend = spend + triple_cost
    print(f"Seed {seed} complete. Triple cost: ${triple_cost:.6f}. New cumulative spend: ${new_spend:.6f} / ${CAP}", flush=True)
    
    # Append to cost ledger
    cl_path = ROOT / "paper/supervisor/cost-ledger.md"
    cl_text = cl_path.read_text(encoding="utf-8")
    log_line = (f"| Block | T3 | s{seed} | B0/B1/B2 | 3 | "
                f"${results['B0']['cost']:.4f}/${results['B1']['cost']:.4f}/${results['B2']['cost']:.4f} | "
                f"**${triple_cost:.6f}** | "
                f"{results['B0']['n_pass']}/{results['B1']['n_pass']}/{results['B2']['n_pass']} | "
                f"**${new_spend:.6f}** |\n")
    cl_path.write_text(cl_text.rstrip() + "\n" + log_line, encoding="utf-8")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        s = int(sys.argv[1])
        run_next_seed(s)
