#!/usr/bin/env python3
"""Unit tests for analyze_block.py on synthetic data."""
import sys, os, json, tempfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/study_b"))
import analyze_block

F = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" :: {detail}" if not ok else ""))
    if not ok: F.append(name)

def main():
    # Test 1: all identical (complete ceiling / 0 differences)
    scores_ident = {
        "B0": np.ones(20),
        "B1": np.ones(20),
        "B2": np.ones(20)
    }
    res_ident = analyze_block.run_analysis(scores_ident)
    check("zero difference gives p=1.0 and n_nonzero=0",
          res_ident["primary_hypothesis"]["p_value"] == 1.0 and res_ident["primary_hypothesis"]["n_nonzero_pairs"] == 0)
    check("ceiling counter identifies all 20 seeds",
          res_ident["descriptive"]["all_arms_perfect_seeds"] == 20)
    check("zero difference bootstrap mean is 0.0",
          res_ident["primary_hypothesis"]["effect_size"]["mean_diff"] == 0.0)

    # Test 2: clear separation (B2 > B0)
    scores_sep = {
        "B0": np.array([0.2, 0.4, 0.6, 0.2, 0.4] * 4), # mean 0.36
        "B1": np.array([0.6, 0.6, 0.8, 0.6, 0.8] * 4), # mean 0.68
        "B2": np.array([1.0, 1.0, 1.0, 1.0, 1.0] * 4)  # mean 1.00
    }
    res_sep = analyze_block.run_analysis(scores_sep)
    check("significant contrast is detected as significant",
          res_sep["primary_hypothesis"]["significant"] is True)
    check("p-value is strictly less than alpha 0.05",
          res_sep["primary_hypothesis"]["p_value"] < 0.05)
    check("effect size CI is strictly positive",
          res_sep["primary_hypothesis"]["effect_size"]["ci_95"][0] > 0.5)

    # Test 3: Holm-Bonferroni ordering and adjustment
    sec = res_sep["secondary_hypotheses"]
    check("two secondary hypotheses evaluated", len(sec) == 2)
    check("adjusted alphas applied in correct sequence (0.025, 0.05)",
          [s["adjusted_alpha"] for s in sec] == [0.025, 0.05] or [s["adjusted_alpha"] for s in sec] == [0.05, 0.025])

    # Test 4: sensitivity methods all return valid probabilities [0, 1]
    sens = res_sep["sensitivity"]["B2_vs_B0"]
    for k, p in sens.items():
        check(f"sensitivity test {k} returns valid p in [0, 1]", 0.0 <= p <= 1.0, f"got {p}")

    print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
