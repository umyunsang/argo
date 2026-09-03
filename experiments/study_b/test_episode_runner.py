#!/usr/bin/env python3
"""Tests for the usage parser. No model call; nothing here is an episode."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import episode_runner as ER

F = []
def check(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (f" :: {d}" if not ok else ""))
    if not ok: F.append(n)

def main():
    t1 = '{"model":"x","total_tokens": 45210, "cost": "$0.13"}'
    u = ER.parse_usage(t1)
    check("json-style usage is parsed", u["total_tokens"] == 45210 and u["cost_usd"] == 0.13, str(u))

    t2 = "Usage: total tokens: 38,112\nTotal cost: $0.0425"
    u = ER.parse_usage(t2)
    check("prose-style usage is parsed", u["total_tokens"] == 38112 and u["cost_usd"] == 0.0425, str(u))

    u = ER.parse_usage("no usage anywhere")
    check("a transcript without usage yields zero, not a guess",
          u["total_tokens"] == 0 and u["cost_usd"] == 0.0, str(u))

    u = ER.parse_usage("1705817 is not tokens; 12 tokens neither")
    check("implausible values are not counted as tokens", u["total_tokens"] == 0, str(u))

    t3 = "first call total_tokens: 10000\nsecond call total_tokens: 12000"
    u = ER.parse_usage(t3)
    check("multiple usage records are summed", u["total_tokens"] == 22000, str(u))

    # Tests for parse_manipulation_log
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        # Case 1: B0 violation with ipython
        (tdp / "manipulation_log.json").write_text(json.dumps([{"tool": "ipython"}, {"tool": "bash"}]))
        m0_bad = ER.parse_manipulation_log(tdp, "B0")
        check("B0 fails manipulation check when ipython is called",
              m0_bad["manipulation_check_passed"] is False and "violation" in m0_bad["manipulation_check_detail"])

        # Case 2: B0 valid with only primitive tools
        (tdp / "manipulation_log.json").write_text(json.dumps([{"tool": "read"}, {"tool": "bash"}, {"tool": "write"}]))
        m0_ok = ER.parse_manipulation_log(tdp, "B0")
        check("B0 passes manipulation check with primitive tools only",
              m0_ok["manipulation_check_passed"] is True)

        # Case 3: B2 violation when decision or threshold is missing
        (tdp / "manipulation_log.json").write_text(json.dumps([{"tool": "bash"}]))
        m2_bad = ER.parse_manipulation_log(tdp, "B2")
        check("B2 fails manipulation check without decision and threshold",
              m2_bad["manipulation_check_passed"] is False)

        # Case 4: B2 valid when decision and threshold registered
        (tdp / "manipulation_log.json").write_text(json.dumps([
            {"event": "decision_recorded"},
            {"event": "threshold_registered"},
            {"event": "graph_add"},
            {"tool": "ipython"}
        ]))
        m2_ok = ER.parse_manipulation_log(tdp, "B2")
        check("B2 passes manipulation check when decision and threshold are recorded",
              m2_ok["manipulation_check_passed"] is True and m2_ok["decisions_recorded"] == 1)

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
