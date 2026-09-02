#!/usr/bin/env python3
"""Re-derive the deterministic quantities of a block from its retained artifacts.

Every score in the executed blocks was produced by instrument code that had not yet
been audited by mutation. This re-derives, from the retained artifacts alone and using
the committed instruments, the quantities that do not depend on a model call: canary
leaks, fabrication redlines, structural gaps, and per-episode candidate-span counts.
Judged verdicts are excluded because the judge is nondeterministic and cannot be
re-derived; that separation is reported rather than hidden.

    /usr/bin/python3 experiments/study_a/recheck_block.py <artifact-dir> <canary>
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from scoring import run_redlines, structural_gaps  # noqa: E402

EPISODE_RE = re.compile(r"^(?P<task>.+?)__(?P<cond>C\d\d)(?:__(?P<rep>r\d+))?\.design\.md$")


def episodes(directory: pathlib.Path) -> dict:
    found = {}
    for path in sorted(directory.iterdir()):
        m = EPISODE_RE.match(path.name)
        if not m:
            continue
        found[path.stem.removesuffix(".design")] = path
    return found


def recheck(directory: pathlib.Path, canary: str | None) -> dict:
    eps = episodes(directory)
    if not eps:
        # A recheck that finds nothing would otherwise report zero leaks and zero
        # redlines, which reads as a pass. It fails loudly instead.
        raise ValueError(f"no episode artifacts matched in {directory}")
    per = []
    for episode_id, path in eps.items():
        text = path.read_text(encoding="utf-8", errors="replace")
        per.append({
            "episode_id": episode_id,
            "bytes": path.stat().st_size,
            "redlines": run_redlines(text),
            "structural_gaps": structural_gaps(text),
            "canary_present": bool(canary) and canary in text,
        })
    return {
        "artifact_dir": str(directory),
        "episodes": len(per),
        "canary_leaks": sum(1 for p in per if p["canary_present"]),
        "fabrication_redlines_fired": sum(1 for p in per if p["redlines"]),
        "episodes_with_structural_gaps": sum(1 for p in per if p["structural_gaps"]),
        "per_episode": per,
        "excluded_from_recheck": ["judged element verdicts, which depend on a model call "
                                  "and cannot be re-derived deterministically"],
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: recheck_block.py <artifact-dir> [canary]", file=sys.stderr)
        return 2
    directory = pathlib.Path(sys.argv[1])
    if not directory.is_dir():
        print(f"no such directory: {directory}", file=sys.stderr)
        return 1
    canary = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        result = recheck(directory, canary)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
