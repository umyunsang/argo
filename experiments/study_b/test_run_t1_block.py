#!/usr/bin/env python3
"""Tests for T1' block driver."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_t1_block as R1B

F = []
def check(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (f" :: {d}" if not ok else ""))
    if not ok: F.append(n)

def main():
    check("tasks defined", len(R1B.TASKS) == 2)
    check("arms defined", R1B.ARMS == ["B0", "B1", "B2"])
    rem_s = R1B.check_auth_remaining_seconds()
    check("auth check returns positive seconds", rem_s > 0, str(rem_s))

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
