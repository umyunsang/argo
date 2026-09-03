#!/usr/bin/env python3
"""Tests for Study B harness extensions and manipulation gates."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXT_DIR = ROOT / "experiments/study_b/harness/extensions"
B0_EXT = EXT_DIR / "b0_tools.js"
B2_EXT = EXT_DIR / "b2_harness.js"

FAILURES: list[str] = []

def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)

def main() -> int:
    check("b0_tools.js exists", B0_EXT.is_file(), str(B0_EXT))
    check("b2_harness.js exists", B2_EXT.is_file(), str(B2_EXT))

    # Node syntax check
    r0 = subprocess.run(["node", "-c", str(B0_EXT)], capture_output=True, text=True)
    check("b0_tools.js has valid JavaScript syntax", r0.returncode == 0, r0.stderr[:200])

    r2 = subprocess.run(["node", "-c", str(B2_EXT)], capture_output=True, text=True)
    check("b2_harness.js has valid JavaScript syntax", r2.returncode == 0, r2.stderr[:200])

    # Content checks for B0
    b0_content = B0_EXT.read_text(encoding="utf-8")
    for tool in ["read", "write", "edit", "bash"]:
        check(f"b0 registers tool '{tool}'", f'name: "{tool}"' in b0_content)
    check("b0 logs to manipulation_log.json", "manipulation_log.json" in b0_content)

    # Content checks for B2
    b2_content = B2_EXT.read_text(encoding="utf-8")
    for tool in ["graph_add", "graph_query", "decision_record", "threshold_register", "loop_evaluate"]:
        check(f"b2 registers tool '{tool}'", f'name: "{tool}"' in b2_content)
    check("b2 intercepts tool_call for fail-closed gate", 'pi.on("tool_call"' in b2_content)
    check("b2 enforces 6-field decision check", 'requiredFields' in b2_content and 'falsifier' in b2_content)
    check("b2 blocks execution on missing threshold or decision", 'FAIL_CLOSED_GATE_BLOCKED' in b2_content)

    print(f"\n{len(FAILURES)} failing checks" if FAILURES else "\nAll extension checks passed.")
    return 1 if FAILURES else 0

if __name__ == "__main__":
    sys.exit(main())
