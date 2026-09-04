#!/usr/bin/env python3
"""Dose-response secondary analysis script for Study B.

Evaluates observational associations between mechanism dosage variables and task outcomes.
Follows paper/research/study-b-mechanism-doseresponse-spec.md.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
from scipy import stats

def analyze_dose_response(receipts: list[dict]) -> dict:
    # Filter to B2 episodes where mechanism tools are active
    b2_eps = [r for r in receipts if r.get("arm") == "B2"]
    if not b2_eps:
        return {"error": "No B2 episodes found in provided receipts"}

    mechanisms = [
        "graph_nodes_added",
        "thresholds_registered",
        "decisions_recorded",
        "gate_blocks",
        "pivots"
    ]

    # Extract outcome
    scores = []
    for r in b2_eps:
        # Prefer ordinal_score if present, else fallback to score ratio
        s = r.get("ordinal_score")
        if s is None:
            sc = r.get("score")
            if isinstance(sc, dict):
                s = sc.get("score", 0)
            else:
                s = float(sc or 0)
        scores.append(float(s))

    y = np.array(scores)
    results = {
        "n_episodes": len(b2_eps),
        "outcome_summary": {
            "mean": float(np.mean(y)),
            "std": float(np.std(y, ddof=1)) if len(y) > 1 else 0.0,
            "min": float(np.min(y)),
            "max": float(np.max(y)),
            "variance": float(np.var(y, ddof=1)) if len(y) > 1 else 0.0
        },
        "mechanisms": {}
    }

    # Analyze each mechanism
    p_values = []
    mech_keys = []

    for m in mechanisms:
        vals = []
        for r in b2_eps:
            # Check in manipulation dict or top-level
            m_dict = r.get("manipulation_check") or {}
            v = r.get(m) if m in r else m_dict.get(m, 0)
            vals.append(float(v or 0))
            
        x = np.array(vals)
        var_x = float(np.var(x, ddof=1)) if len(x) > 1 else 0.0
        
        m_res = {
            "mean": float(np.mean(x)),
            "std": float(np.std(x, ddof=1)) if len(x) > 1 else 0.0,
            "min": float(np.min(x)),
            "max": float(np.max(x)),
            "variance": var_x,
            "distinct_values": len(np.unique(x))
        }

        if var_x == 0.0 or results["outcome_summary"]["variance"] == 0.0:
            m_res["status"] = "UNFIRED_OR_ZERO_VARIANCE"
            m_res["rho"] = None
            m_res["p_value"] = None
        else:
            m_res["status"] = "EVALUATED"
            rho, p_val = stats.spearmanr(x, y)
            m_res["rho"] = float(rho)
            m_res["p_value"] = float(p_val)
            p_values.append(float(p_val))
            mech_keys.append(m)

        results["mechanisms"][m] = m_res

    # Apply Holm-Bonferroni correction to evaluated p-values
    if p_values:
        # Sort p-values
        sorted_indices = np.argsort(p_values)
        m_tests = len(p_values)
        holm_p = {}
        for rank, idx in enumerate(sorted_indices):
            adjusted = min(1.0, p_values[idx] * (m_tests - rank))
            holm_p[mech_keys[idx]] = float(adjusted)
        for k, hp in holm_p.items():
            results["mechanisms"][k]["p_holm"] = hp

    return results

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipts-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    
    rdir = Path(args.receipts_dir)
    receipt_files = list(rdir.glob("*.json"))
    receipts = [json.loads(p.read_text()) for p in receipt_files if p.is_file()]
    
    res = analyze_dose_response(receipts)
    Path(args.out).write_text(json.dumps(res, indent=2) + "\n")
    print(f"Wrote dose-response analysis to {args.out}")
