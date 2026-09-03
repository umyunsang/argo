#!/usr/bin/env python3
"""Study B Block Analysis Runner (v4a Specification).

Executes primary, secondary, sensitivity, and descriptive analyses on completed
Study B screening receipts across seeds 0..N-1.
Outputs the canonical analysis receipt: paper/experiments/study-b-analysis-receipt.json
"""

import sys, os, json, math
from pathlib import Path
import numpy as np
import scipy.stats as stats

ROOT = Path(__file__).resolve().parents[2]
SEEDS_TOTAL = 40
SEED_RNG = 20260903

def load_block_scores(task="T3", n_seeds=SEEDS_TOTAL, block_dir=None):
    """Load item-level pass fractions (0.0 to 1.0) for B0, B1, B2 across seeds."""
    if block_dir is None:
        block_dir = ROOT / "paper/experiments/screening/block"
    scores = {"B0": [], "B1": [], "B2": []}
    
    # seed 0 is in stage1v4
    stage1_dir = ROOT / "paper/experiments/screening/stage1v4"
    for arm in ("B0", "B1", "B2"):
        p0 = stage1_dir / f"{arm}-{task}-seed0-receipt.json"
        if not p0.is_file():
            raise FileNotFoundError(f"Missing seed 0 receipt: {p0}")
        d0 = json.loads(p0.read_text(encoding="utf-8"))
        ep0 = d0["episodes"][0]
        pass_frac0 = ep0["score"]["n_pass"] / ep0["score"]["n_total"]
        scores[arm].append(pass_frac0)
        
    for s in range(1, n_seeds):
        for arm in ("B0", "B1", "B2"):
            p = block_dir / f"{arm}_{task}" / f"seed{s}-receipt.json"
            if not p.is_file():
                raise FileNotFoundError(f"Missing seed {s} receipt for {arm}: {p}")
            d = json.loads(p.read_text(encoding="utf-8"))
            ep = d["episodes"][0]
            pass_frac = ep["score"]["n_pass"] / ep["score"]["n_total"]
            scores[arm].append(pass_frac)
            
    return {k: np.array(v) for k, v in scores.items()}

def paired_wilcoxon(x, y, zero_method="pratt"):
    """Compute paired Wilcoxon signed-rank test."""
    diff = x - y
    n_nonzero = np.sum(diff != 0)
    if n_nonzero == 0:
        return {"stat": 0.0, "p_value": 1.0, "n_nonzero": 0}
    res = stats.wilcoxon(x, y, zero_method=zero_method, alternative="two-sided")
    return {"stat": float(res.statistic), "p_value": float(res.pvalue), "n_nonzero": int(n_nonzero)}

def exact_sign_test(x, y):
    """Exact two-sided binomial sign test on non-zero differences."""
    diff = x - y
    n_pos = int(np.sum(diff > 0))
    n_neg = int(np.sum(diff < 0))
    n_total = n_pos + n_neg
    if n_total == 0:
        return {"p_value": 1.0, "n_pos": 0, "n_neg": 0, "n_total": 0}
    res = stats.binomtest(n_pos, n_total, p=0.5, alternative="two-sided")
    return {"p_value": float(res.pvalue), "n_pos": n_pos, "n_neg": n_neg, "n_total": n_total}

def paired_permutation_test(x, y, n_resamples=10000, seed=SEED_RNG):
    """Paired random sign-flip permutation test on mean difference."""
    diff = x - y
    obs_mean = float(np.mean(diff))
    rng = np.random.default_rng(seed)
    # Randomly flip signs of differences
    signs = rng.choice([-1.0, 1.0], size=(n_resamples, len(diff)))
    perm_means = np.mean(signs * diff, axis=1)
    p_val = float(np.mean(np.abs(perm_means) >= np.abs(obs_mean)))
    return {"obs_mean_diff": obs_mean, "p_value": p_val, "n_resamples": n_resamples}

def bootstrap_mean_diff(x, y, n_resamples=10000, seed=SEED_RNG):
    """Percentile bootstrap 95% confidence interval for mean difference."""
    diff = x - y
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(diff), size=(n_resamples, len(diff)))
    boot_means = np.mean(diff[indices], axis=1)
    ci_low = float(np.percentile(boot_means, 2.5))
    ci_high = float(np.percentile(boot_means, 97.5))
    return {"mean_diff": float(np.mean(diff)), "ci_95": [ci_low, ci_high], "n_resamples": n_resamples}

def run_analysis(scores):
    n = len(scores["B0"])
    
    # 1. Descriptive stats
    desc = {}
    for arm in ("B0", "B1", "B2"):
        v = scores[arm]
        desc[arm] = {
            "mean": float(np.mean(v)),
            "std": float(np.std(v, ddof=1)),
            "min": float(np.min(v)),
            "max": float(np.max(v)),
            "n_perfect_5_of_5": int(np.sum(v == 1.0))
        }
    
    # Ceiling seeds where all three arms scored 5/5
    all_perfect_seeds = int(np.sum((scores["B0"] == 1.0) & (scores["B1"] == 1.0) & (scores["B2"] == 1.0)))
    desc["all_arms_perfect_seeds"] = all_perfect_seeds
    desc["n_seeds_total"] = n
    
    # 2. Primary Hypothesis: B2 vs B0 (Pratt Wilcoxon)
    prim_wilc = paired_wilcoxon(scores["B2"], scores["B0"], zero_method="pratt")
    prim_boot = bootstrap_mean_diff(scores["B2"], scores["B0"])
    primary = {
        "contrast": "B2_vs_B0",
        "method": "paired_wilcoxon_pratt_two_sided",
        "statistic": prim_wilc["stat"],
        "p_value": prim_wilc["p_value"],
        "n_nonzero_pairs": prim_wilc["n_nonzero"],
        "n_zero_diff_pairs": n - prim_wilc["n_nonzero"],
        "effect_size": prim_boot,
        "alpha": 0.05,
        "significant": bool(prim_wilc["p_value"] < 0.05)
    }
    
    # 3. Secondary Hypotheses: B2 vs B1, B1 vs B0 (Holm-Bonferroni)
    sec_contrasts = [("B2", "B1"), ("B1", "B0")]
    raw_sec = []
    for a1, a2 in sec_contrasts:
        w = paired_wilcoxon(scores[a1], scores[a2], zero_method="pratt")
        b = bootstrap_mean_diff(scores[a1], scores[a2])
        raw_sec.append({
            "contrast": f"{a1}_vs_{a2}",
            "statistic": w["stat"],
            "p_value": w["p_value"],
            "n_nonzero_pairs": w["n_nonzero"],
            "effect_size": b
        })
        
    # Apply Holm-Bonferroni correction (m=2)
    # Sort by p-value ascending
    sorted_idx = np.argsort([r["p_value"] for r in raw_sec])
    m = len(raw_sec)
    for rank, idx in enumerate(sorted_idx):
        adj_alpha = 0.05 / (m - rank)
        raw_sec[idx]["adjusted_alpha"] = adj_alpha
        raw_sec[idx]["significant"] = bool(raw_sec[idx]["p_value"] < adj_alpha)
    secondary = raw_sec
    
    # 4. Sensitivity Analyses
    sensitivity = {}
    for c_name, a1, a2 in [("B2_vs_B0", "B2", "B0"), ("B2_vs_B1", "B2", "B1"), ("B1_vs_B0", "B1", "B0")]:
        w_wilcox = paired_wilcoxon(scores[a1], scores[a2], zero_method="wilcox")
        s_test = exact_sign_test(scores[a1], scores[a2])
        perm_test = paired_permutation_test(scores[a1], scores[a2])
        sensitivity[c_name] = {
            "wilcoxon_wilcox_p_value": w_wilcox["p_value"],
            "exact_sign_test_p_value": s_test["p_value"],
            "permutation_test_p_value": perm_test["p_value"]
        }
        
    return {
        "descriptive": desc,
        "primary_hypothesis": primary,
        "secondary_hypotheses": secondary,
        "sensitivity": sensitivity
    }

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="T3")
    ap.add_argument("--n-seeds", type=int, default=SEEDS_TOTAL)
    ap.add_argument("--out", default="paper/experiments/study-b-analysis-receipt.json")
    a = ap.parse_args()
    
    scores = load_block_scores(a.task, a.n_seeds)
    results = run_analysis(scores)
    
    receipt = {
        "schema_version": "study-b-analysis/v1",
        "origin": "verifier",
        "evidence_level": "REPRODUCED_EXPERIMENT",
        "executed": True,
        "task": a.task,
        "n_seeds": a.n_seeds,
        "spec_reference": "paper/research/study-b-analysis-spec-v4a.md",
        "scipy_version": stats.__version__,
        "numpy_version": np.__version__,
        "analysis": results
    }
    
    out_p = ROOT / a.out
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Analysis complete. Receipt written to {out_p}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
