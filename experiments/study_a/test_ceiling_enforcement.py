#!/usr/bin/env python3
"""Failing-first fixtures for post-hoc ceiling enforcement."""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ceiling_enforcement import enforce, measured_quantities  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def usage(total=1000, inp=10, out=90, calls=3):
    return {"tokens": {"input": inp, "output": out, "totalTokens": total}, "api_calls": calls}


def main() -> int:
    m = measured_quantities(usage())
    check("marginal is input plus output", m["marginal_tokens"] == 100, str(m))
    check("total is reported separately", m["total_tokens"] == 1000)
    check("marginal is not the total", m["marginal_tokens"] != m["total_tokens"])
    check("wallclock is None when not supplied", m["wallclock_seconds"] is None)

    check("no ceilings means admission is undefined, not granted",
          enforce(usage(), {})["admissible"] is False)
    check("an unmeasured quantity is refused rather than guessed",
          enforce(usage(), {"gpu_hours": 5})["admissible"] is False)
    check("the refusal names the offending quantity",
          "gpu_hours" in enforce(usage(), {"gpu_hours": 5})["reason"])

    ok = enforce(usage(), {"total_tokens": 2000, "api_calls": 5})
    check("within every ceiling is admissible", ok["admissible"] is True, str(ok))
    check("no violations recorded when admissible", ok["violations"] == [])

    over = enforce(usage(total=5000), {"total_tokens": 2000})
    check("exceeding a ceiling is inadmissible", over["admissible"] is False)
    check("the overage is reported", over["violations"][0]["exceeded_by"] == 3000, str(over))

    edge = enforce(usage(calls=12), {"api_calls": 12})
    check("equal to the ceiling is not exceeding it", edge["admissible"] is True, str(edge))

    split = enforce(usage(total=5000, inp=10, out=90), {"marginal_tokens": 2000})
    check("a marginal ceiling ignores re-sent context", split["admissible"] is True, str(split))
    check("the same episode fails a total ceiling of the same size",
          enforce(usage(total=5000, inp=10, out=90), {"total_tokens": 2000})["admissible"] is False)

    missing = enforce(usage(), {"wallclock_seconds": 900})
    check("an unmeasured wallclock is a violation, not a pass",
          missing["admissible"] is False and missing["violations"][0]["measured"] is None,
          str(missing))

    check("measured values are returned for reporting",
          enforce(usage(), {"api_calls": 5})["measured"]["api_calls"] == 3)

    print("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
