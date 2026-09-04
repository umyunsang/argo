#!/usr/bin/env python3
"""Tests for the Study B dose-response secondary analysis script."""
import sys, tempfile, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_dose_response as ADR

F = []
def check(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (f" :: {d}" if not ok else ""))
    if not ok: F.append(n)

def main():
    # Test 1: Empty or non-B2 receipts
    r1 = [{"arm": "B0", "ordinal_score": 1}]
    out1 = ADR.analyze_dose_response(r1)
    check("empty B2 returns error", "error" in out1)

    # Test 2: Invariant zero (pivots = 0) correctly marked
    r2 = [
        {"arm": "B2", "ordinal_score": 1, "pivots": 0, "graph_nodes_added": 2, "decisions_recorded": 1, "thresholds_registered": 1, "gate_blocks": 0},
        {"arm": "B2", "ordinal_score": 2, "pivots": 0, "graph_nodes_added": 5, "decisions_recorded": 2, "thresholds_registered": 2, "gate_blocks": 1},
        {"arm": "B2", "ordinal_score": 2, "pivots": 0, "graph_nodes_added": 6, "decisions_recorded": 3, "thresholds_registered": 3, "gate_blocks": 0},
    ]
    out2 = ADR.analyze_dose_response(r2)
    check("evaluates B2 episodes count", out2["n_episodes"] == 3)
    check("pivots with zero variance marked UNFIRED", out2["mechanisms"]["pivots"]["status"] == "UNFIRED_OR_ZERO_VARIANCE")
    check("graph_nodes_added with variance evaluated", out2["mechanisms"]["graph_nodes_added"]["status"] == "EVALUATED")
    check("spearman rho is computed", "rho" in out2["mechanisms"]["graph_nodes_added"])
    check("Holm p-value is computed", "p_holm" in out2["mechanisms"]["graph_nodes_added"])

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
