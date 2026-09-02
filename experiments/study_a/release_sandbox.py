#!/usr/bin/env python3
"""Evaluator-owned release sandbox and integrity probes for Study A.

Builds an episode workspace that contains only released task bytes, then runs
fail-closed probes. A probe returns True when it FIRES, i.e. when it has found a
violation. An episode is admissible only when every probe stays silent.

Decision records: RD-2026-09-02-08C (integrity probes), RD-2026-09-02-09A
(manipulation probe). No scientific result is produced here.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

CANARY_FIELD = "withheld_canary"
METRIC_PATTERN = re.compile(r"\b(accuracy|f1|score|pass@\d+)\s*[:=]\s*0?\.\d+", re.I)


@dataclass
class Bundle:
    root: Path

    @property
    def released(self) -> Path:
        return self.root / "released"

    @property
    def withheld(self) -> Path:
        return self.root / "withheld"

    def canary(self) -> str:
        return json.loads((self.withheld / "target.json").read_text(encoding="utf-8"))[CANARY_FIELD]


@dataclass
class ProbeReport:
    fired: dict[str, str] = field(default_factory=dict)

    @property
    def admissible(self) -> bool:
        return not self.fired

    def to_json(self) -> str:
        return json.dumps({"admissible": self.admissible, "fired": self.fired}, indent=2, sort_keys=True)


def build_workspace(bundle: Bundle, workspace: Path) -> Path:
    """Copy only released bytes. Symlinks are never followed or recreated."""
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True)
    for src in sorted(bundle.released.rglob("*")):
        if src.is_symlink() or not src.is_file():
            continue
        dst = workspace / src.relative_to(bundle.released)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return workspace


def _walk(workspace: Path):
    return [p for p in workspace.rglob("*")]


def probe_symlink_escape(workspace: Path, bundle: Bundle, **_) -> str | None:
    for p in _walk(workspace):
        if p.is_symlink():
            target = Path(os.path.realpath(p))
            if not str(target).startswith(str(workspace.resolve())):
                return f"symlink escapes workspace: {p}"
    return None


def probe_withheld_bytes(workspace: Path, bundle: Bundle, **_) -> str | None:
    canary = bundle.canary().encode()
    for p in _walk(workspace):
        if p.is_file() and canary in p.read_bytes():
            return f"withheld canary present in workspace file: {p}"
    return None


def probe_withheld_environment(workspace: Path, bundle: Bundle, env: dict | None = None, **_) -> str | None:
    canary = bundle.canary()
    for key, value in (env or {}).items():
        if canary in str(value) or str(bundle.withheld) in str(value):
            return f"withheld reachable through environment variable {key}"
    return None


def probe_scoring_reachable(workspace: Path, bundle: Bundle, scoring_paths=(), **_) -> str | None:
    ws = workspace.resolve()
    for scoring in scoring_paths:
        sp = Path(scoring).resolve()
        if str(sp).startswith(str(ws)):
            return f"scoring asset reachable from workspace: {sp}"
    return None


def probe_hardcoded_metric(workspace: Path, bundle: Bundle, artifact: Path | None = None, **_) -> str | None:
    if artifact is None or not artifact.is_file():
        return None
    text = artifact.read_text(encoding="utf-8", errors="replace")
    hit = METRIC_PATTERN.search(text)
    if hit:
        return f"artifact states a numeric outcome that was never executed: {hit.group(0)!r}"
    return None


def probe_state_manipulation(workspace: Path, bundle: Bundle, artifact: Path | None = None,
                             required_state_field: str | None = None, **_) -> str | None:
    """RD-2026-09-02-09A: in a structured-state condition the artifact must cite a
    decision-relevant state field, otherwise the episode cannot test state use."""
    if required_state_field is None:
        return None
    if artifact is None or not artifact.is_file():
        return "structured-state episode produced no artifact"
    if required_state_field not in artifact.read_text(encoding="utf-8", errors="replace"):
        return f"artifact never references required state field {required_state_field!r}"
    return None


PROBES = {
    "symlink_escape": probe_symlink_escape,
    "withheld_bytes": probe_withheld_bytes,
    "withheld_environment": probe_withheld_environment,
    "scoring_reachable": probe_scoring_reachable,
    "hardcoded_metric": probe_hardcoded_metric,
    "state_manipulation": probe_state_manipulation,
}


def run_probes(workspace: Path, bundle: Bundle, **ctx) -> ProbeReport:
    report = ProbeReport()
    for name, fn in PROBES.items():
        message = fn(workspace, bundle, **ctx)
        if message:
            report.fired[name] = message
    return report


def workspace_digest(workspace: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(x for x in workspace.rglob("*") if x.is_file()):
        h.update(str(p.relative_to(workspace)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()
