#!/usr/bin/env python3
"""Failing-first tests for the Study B ablation extensions."""
import json, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXT_DIR = ROOT / "experiments/study_b/harness/extensions"

F = []
def check(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (f" :: {d}" if not ok else ""))
    if not ok: F.append(n)

def main():
    b2_js = (EXT_DIR / "b2_harness.js").read_text()
    b2_g_js = (EXT_DIR / "b2_g_harness.js").read_text()
    b2_p_js = (EXT_DIR / "b2_p_harness.js").read_text()
    b2_r_js = (EXT_DIR / "b2_r_harness.js").read_text()

    # Test B2-G: graph_add and graph_query removed
    check("B2-G does not register graph_add", 'name: "graph_add"' not in b2_g_js)
    check("B2-G does not register graph_query", 'name: "graph_query"' not in b2_g_js)
    check("B2-G keeps decision_record", 'name: "decision_record"' in b2_g_js)
    check("B2-G keeps threshold_register", 'name: "threshold_register"' in b2_g_js)
    check("B2-G keeps fail-closed gate", 'event.toolName === "ipython"' in b2_g_js)

    # Test B2-P: decision_record, threshold_register, and gate removed
    check("B2-P does not register decision_record", 'name: "decision_record"' not in b2_p_js)
    check("B2-P does not register threshold_register", 'name: "threshold_register"' not in b2_p_js)
    check("B2-P does not intercept with gate", 'state.gateBlocks++' not in b2_p_js)
    check("B2-P keeps graph_add", 'name: "graph_add"' in b2_p_js)

    # Test B2-R: result-driven search explicitly excluded
    check("B2-R has search exclusion marker", 'R: Result-driven search explicitly excluded' in b2_r_js)

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
