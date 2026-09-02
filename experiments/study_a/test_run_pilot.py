#!/usr/bin/env python3
"""Failing-first fixtures for the pilot episode builder.

The builder decides what each condition actually mounts, so a fault here would change
the treatment without changing the recorded design. These fixtures assert the factorial
contract directly: which condition mounts evidence, which mounts the scaffold, that the
prompt differs only by those two additions, and that a workspace digest is stable.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from run_pilot import BASE_PROMPT, CONDITIONS, REQUIRED_STATE_FIELD, SCAFFOLD, build_episode  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def make_bundle(root: pathlib.Path) -> pathlib.Path:
    bundle = root / "task"
    (bundle / "released").mkdir(parents=True)
    (bundle / "withheld").mkdir(parents=True)
    (bundle / "released" / "instructions.md").write_text("Design an experiment.\n", encoding="utf-8")
    (bundle / "released" / "evidence").mkdir()
    (bundle / "released" / "evidence" / "a.txt").write_text("evidence one\n", encoding="utf-8")
    (bundle / "released" / "evidence" / "b.txt").write_text("evidence two\n", encoding="utf-8")
    (bundle / "withheld" / "target.json").write_text(
        '{"withheld_canary": "ZZZ-CANARY", "elements": []}\n', encoding="utf-8")
    return bundle


def main() -> int:
    check("the factorial has exactly four conditions", len(CONDITIONS) == 4, str(sorted(CONDITIONS)))
    check("condition codes map to the two factors",
          CONDITIONS["C00"] == (False, False) and CONDITIONS["C11"] == (True, True)
          and CONDITIONS["C01"] == (False, True) and CONDITIONS["C10"] == (True, False),
          str(CONDITIONS))
    check("the required state field appears in the scaffold", REQUIRED_STATE_FIELD in SCAFFOLD)
    check("the scaffold asks for a falsifier", "falsifier" in SCAFFOLD)

    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        bundle = make_bundle(root)
        out = {}
        for cond in sorted(CONDITIONS):
            out[cond] = build_episode(
                {"episode_id": f"ep_{cond}", "task_id": "t", "condition": cond,
                 "task_bundle": str(bundle)}, root / "ws")

        for cond, (structured, retrieval) in CONDITIONS.items():
            ws = pathlib.Path(out[cond]["workspace"])
            has_evidence = (ws / "evidence").exists()
            has_state = (ws / "state.md").exists()
            check(f"{cond} mounts evidence only when retrieval is on", has_evidence == retrieval,
                  f"retrieval={retrieval} evidence={has_evidence}")
            check(f"{cond} mounts the scaffold only when structured state is on",
                  has_state == structured, f"structured={structured} state={has_state}")
            check(f"{cond} always mounts the instructions", (ws / "instructions.md").exists())
            check(f"{cond} never mounts withheld material",
                  not any(p.name == "target.json" for p in ws.rglob("*")))
            check(f"{cond} never leaks the canary into the workspace",
                  not any(p.is_file() and b"ZZZ-CANARY" in p.read_bytes() for p in ws.rglob("*")))
            check(f"{cond} reports evidence files only under retrieval",
                  bool(out[cond]["evidence_files"]) == retrieval)
            check(f"{cond} is admissible before launch", out[cond]["admissible"], 
                  str(out[cond]["prelaunch_probes"]))

        check("every condition starts from the same base prompt",
              all(o["prompt"].startswith(BASE_PROMPT) for o in out.values()))
        check("the minimal condition prompt is exactly the base prompt",
              out["C00"]["prompt"] == BASE_PROMPT)
        check("the full condition prompt is longer than the minimal one",
              len(out["C11"]["prompt"]) > len(out["C00"]["prompt"]))
        check("each condition produces a distinct prompt digest",
              len({o["prompt_sha256"] for o in out.values()}) == 4)
        check("conditions with the same factors share a workspace digest across builds",
              build_episode({"episode_id": "ep_C00", "task_id": "t", "condition": "C00",
                             "task_bundle": str(bundle)}, root / "ws")["workspace_digest"]
              == out["C00"]["workspace_digest"])
        check("the minimal and full workspaces differ",
              out["C00"]["workspace_digest"] != out["C11"]["workspace_digest"])
        check("the two factors are independent in the workspace",
              out["C10"]["workspace_digest"] != out["C01"]["workspace_digest"])

    print("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
