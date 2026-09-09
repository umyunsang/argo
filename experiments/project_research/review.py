"""Research review apparatus; permissions alone do not isolate same-user agents.

Only the supervisor directory is mounted into a new supervisor session. The
controller and evaluation registry belong to the external execution controller.
The module checks receipts and hashes, not scientific truth or OS isolation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import sqlite3
import sys
import unicodedata
from dataclasses import dataclass
from typing import Mapping, Sequence


DIMENSIONS = (
    "correctness",
    "reproducibility",
    "research_logic",
    "falsification_and_comparison",
    "evidence_and_accounting",
    "claim_scope",
)
SCOPES = {"apparatus_only", "development_research"}
METADATA_KEYS = {
    "author", "authors", "team", "teamid", "workerteam",
    "llmmodel", "createdby", "writtenby", "candidateid",
    "priorscore", "priorscores", "previousscore", "previousscores",
    "previousrating", "reviewhistory", "previousassessment", "priorassessment",
}
TEXT_SUFFIXES = {".txt", ".md", ".csv", ".tsv", ".json", ".py", ".r", ".sql", ".toml", ".yaml", ".yml", ".sh", ".js", ".ts"}
CODE_SUFFIXES = {".py", ".r", ".sql", ".sh", ".js", ".ts"}
HASH_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
SUSPECT_PATTERN = re.compile(
    r"(?i)(?:[\w.+-]+@[\w.-]+\.[a-z]{2,}|/Users/|/home/|[A-Z]:\\Users\\|"
    r"\b(?:gpt[-_]\d[\w.-]*|claude(?:[-_ ](?:opus|sonnet|haiku))?|codex|anthropic|openai)\b|"
    r"\b(?:team|worker)[-_ ]+[0-9]+\b|"
    r"\b(?:author|team(?:[_ -]id)?|worker[_ -]team|llm[_ -]model|"
    r"prior[_ -](?:score|rating)|previous[_ -](?:score|rating))\s*[:=])"
)
HEADER_PATTERN = re.compile(
    r"(?im)^\s*(?:[#;/*]+\s*)?(?:author(?:s)?|team(?:[_ -]id)?|model(?:[_ -]id)?|"
    r"llm[_ -]model|provider|created[_ -]by|written[_ -]by|"
    r"prior[_ -](?:score|rating)s?|previous[_ -](?:score|rating)s?)\s*[:=].*$"
)


class ReviewError(ValueError):
    """A review packet or transition does not satisfy its contract."""


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    team_id: str
    workspace: Path
    artifacts: tuple[str, ...]
    authors: tuple[str, ...]
    models: tuple[str, ...]


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ReviewError(f"{label} must be an object")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReviewError(f"{label} must be nonempty text")
    return value


def _texts(value: object, label: str) -> list[str]:
    if not isinstance(value, (list, tuple)) or not value:
        raise ReviewError(f"{label} must be a nonempty list")
    return [_text(item, label) for item in value]


def _hash(value: object, label: str) -> str:
    value = _text(value, label)
    if not HASH_PATTERN.fullmatch(value):
        raise ReviewError(f"{label} must be a SHA-256 digest")
    return value


def _no_symlinks(path: Path) -> Path:
    path = path.absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ReviewError("symlinks are not admitted in review paths")
    return path.resolve()


def _inside(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ReviewError("artifact paths must be relative without parent traversal")
    resolved = _no_symlinks(root / path)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ReviewError("artifact must be a regular file inside its workspace")
    if resolved.stat().st_nlink != 1:
        raise ReviewError("shared hard-linked artifacts are not admitted")
    return resolved


def _read_json(path: Path) -> dict[str, object]:
    try:
        return _mapping(_parse_json(_no_symlinks(path).read_text()), "JSON document")
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReviewError("invalid UTF-8 JSON document") from exc


def _parse_json(value: str) -> object:
    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, item in items:
            if key in result:
                raise ReviewError("duplicate JSON keys are not admitted")
            result[key] = item
        return result

    def reject_constant(value: str) -> None:
        raise ReviewError(f"non-finite JSON value {value} is not admitted")

    return json.loads(value, object_pairs_hook=pairs, parse_constant=reject_constant)


def _write_new(path: Path, value: object, mode: int = 0o600) -> None:
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode), "wb") as stream:
        stream.write(_json_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())


def _normal(value: str) -> str:
    return unicodedata.normalize("NFKC", value).casefold()


def _identity_pattern(tokens: Sequence[str]) -> re.Pattern[str]:
    terms = [re.escape(_normal(token)) for token in tokens]
    return re.compile(r"(?<!\w)(?:" + "|".join(sorted(set(terms), key=len, reverse=True)) + r")(?!\w)")


def _scrub_text(value: str, identities: re.Pattern[str], *, code: bool = False) -> str:
    if any(unicodedata.category(char) == "Cf" for char in value):
        raise ReviewError("invisible format characters require manual blind-packet review")
    if code:
        if HEADER_PATTERN.search(value) or identities.search(_normal(value)) or SUSPECT_PATTERN.search(_normal(value)):
            raise ReviewError("identity-bearing code must be submitted as a manually blinded copy")
        return value
    value = HEADER_PATTERN.sub("[REDACTED METADATA]", value)
    # Redact without changing case/normalization of the remaining scientific text.
    if identities.search(_normal(value)):
        if unicodedata.normalize("NFKC", value) != value:
            raise ReviewError("normalized identity match requires manual redaction")
        value = re.sub(identities.pattern, "[REDACTED]", value, flags=re.IGNORECASE)
    if identities.search(_normal(value)) or SUSPECT_PATTERN.search(_normal(value)):
        raise ReviewError("suspected residual identity or prior-score leakage")
    return value


def _scrub_json(value: object, identities: re.Pattern[str]) -> object:
    if isinstance(value, dict):
        cleaned: dict[str, object] = {}
        for key, item in value.items():
            normalized_key = re.sub(r"[^a-z0-9]", "", _normal(str(key)))
            if normalized_key in METADATA_KEYS:
                continue
            clean_key = _scrub_text(str(key), identities)
            if clean_key in cleaned:
                raise ReviewError("redaction causes a duplicate JSON key")
            cleaned[clean_key] = _scrub_json(item, identities)
        return cleaned
    if isinstance(value, list):
        return [_scrub_json(item, identities) for item in value]
    return _scrub_text(value, identities) if isinstance(value, str) else value


def _sanitize(data: bytes, suffix: str, identities: re.Pattern[str]) -> bytes:
    if suffix not in TEXT_SUFFIXES:
        raise ReviewError("unsupported binary/metadata-bearing artifact; submit a reviewed text export")
    try:
        value = data.decode("utf-8")
        if suffix == ".json":
            return _json_bytes(_scrub_json(_parse_json(value), identities))
        return _scrub_text(value, identities, code=suffix in CODE_SUFFIXES).encode()
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReviewError("artifact is not valid UTF-8 text/JSON") from exc


def build_blind_round(
    candidates: Sequence[CandidateSpec],
    output_dir: Path,
    *,
    layer: str = "research_operations",
    evidence_scope: str = "apparatus_only",
) -> dict[str, str]:
    """Create one fresh supervisor input for exactly two independently stored teams.

    The caller must start the named fresh session with ONLY supervisor_dir mounted.
    Development artifacts must be explicitly marked development_research; fixtures
    retain the default apparatus_only and never produce a research AAA decision.
    """
    if layer not in {"research_operations", "evaluated_harness"} or evidence_scope not in SCOPES:
        raise ReviewError("invalid layer or evidence scope")
    if len(candidates) != 2 or len({item.team_id for item in candidates}) != 2:
        raise ReviewError("a blind round requires exactly two distinct teams")
    if len({item.candidate_id for item in candidates}) != 2:
        raise ReviewError("candidate identities must be distinct")
    output_dir = _no_symlinks(output_dir)
    workspaces = [_no_symlinks(item.workspace) for item in candidates]
    if any(not path.is_dir() for path in workspaces):
        raise ReviewError("candidate workspace is absent")
    if any(left.is_relative_to(right) or right.is_relative_to(left) for left, right in [(workspaces[0], workspaces[1])]):
        raise ReviewError("independent teams must use disjoint workspaces")
    if any(output_dir.is_relative_to(path) or path.is_relative_to(output_dir) for path in workspaces):
        raise ReviewError("review output must be outside all producer workspaces")
    tokens: list[str] = []
    for item in candidates:
        tokens.extend([_text(item.candidate_id, "candidate_id"), _text(item.team_id, "team_id")])
        tokens.extend(_texts(item.authors, "authors"))
        tokens.extend(_texts(item.models, "models"))
        if not item.artifacts or len(set(item.artifacts)) != len(item.artifacts):
            raise ReviewError("explicit unique artifacts are required")
    identities = _identity_pattern(tokens)
    prepared: list[tuple[dict[str, object], dict[str, object], list[tuple[str, bytes]]]] = []
    for item, workspace in zip(candidates, workspaces):
        opaque = "candidate-" + secrets.token_hex(12)
        public_artifacts: list[dict[str, object]] = []
        private_artifacts: list[dict[str, object]] = []
        copies: list[tuple[str, bytes]] = []
        for relative in item.artifacts:
            source = _inside(workspace, relative)
            artifact_id = "artifact-" + secrets.token_hex(12)
            suffix = source.suffix.lower()
            raw = source.read_bytes()
            clean = _sanitize(raw, suffix, identities)
            public_file = f"{opaque}/{artifact_id}{suffix}"
            copies.append((public_file, clean))
            public_artifacts.append({"artifact_id": artifact_id, "file": public_file, "sha256": _sha(clean)})
            private_artifacts.append({"artifact_id": artifact_id, "source": relative, "source_sha256": _sha(raw), "public_sha256": _sha(clean), "redacted": clean != raw})
        prepared.append((
            {"candidate_id": opaque, "artifacts": public_artifacts},
            {"candidate_id": item.candidate_id, "team_id": item.team_id, "workspace": str(workspace), "authors": list(item.authors), "models": list(item.models), "artifacts": private_artifacts},
            copies,
        ))
    secrets.SystemRandom().shuffle(prepared)
    packet = {
        "schema_version": "project-research-blind-round/v1",
        "round_id": "round-" + secrets.token_hex(16),
        "supervisor_session_id": "supervisor-" + secrets.token_hex(16),
        "layer": layer,
        "evidence_scope": evidence_scope,
        "rubric": list(DIMENSIONS),
        "candidates": [item[0] for item in prepared],
        "session_policy": {"start_fresh": True, "input": "this_directory_only", "carryover": False},
        "anonymity_limit": "Methods may remain inferable. New sessions and redaction do not prove independent errors.",
    }
    output_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    supervisor = output_dir / "supervisor"
    controller = output_dir / "controller"
    supervisor.mkdir(mode=0o700)
    controller.mkdir(mode=0o700)
    for public, _, copies in prepared:
        (supervisor / str(public["candidate_id"])).mkdir(mode=0o700)
        for relative, content in copies:
            path = supervisor / relative
            path.write_bytes(content)
            path.chmod(0o444)
    _write_new(supervisor / "packet.json", packet, 0o444)
    _write_new(controller / "mapping.json", {
        "packet_sha256": _sha(_json_bytes(packet)),
        "round_id": packet["round_id"],
        "candidates": {str(public["candidate_id"]): private for public, private, _ in prepared},
    })
    return {"round_dir": str(output_dir), "supervisor_dir": str(supervisor), "controller_dir": str(controller), "packet": str(supervisor / "packet.json"), "supervisor_session_id": str(packet["supervisor_session_id"])}


def _packet_candidate(supervisor_dir: Path, candidate_id: str) -> tuple[dict[str, object], dict[str, dict[str, object]]]:
    supervisor_dir = _no_symlinks(supervisor_dir)
    packet = _read_json(supervisor_dir / "packet.json")
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 2:
        raise ReviewError("packet requires exactly two candidates")
    artifacts: dict[str, dict[str, object]] = {}
    candidate_ids: set[str] = set()
    artifact_ids: set[str] = set()
    expected_files = {"packet.json"}
    for raw in candidates:
        candidate = _mapping(raw, "candidate")
        identity = _text(candidate.get("candidate_id"), "candidate_id")
        if identity in candidate_ids or not re.fullmatch(r"candidate-[a-f0-9]{24}", identity):
            raise ReviewError("candidate IDs must be unique and opaque")
        candidate_ids.add(identity)
        items = candidate.get("artifacts")
        if not isinstance(items, list) or not items:
            raise ReviewError("candidate evidence is absent")
        for item in items:
            artifact = _mapping(item, "artifact")
            artifact_id = _text(artifact.get("artifact_id"), "artifact_id")
            if artifact_id in artifact_ids:
                raise ReviewError("duplicate artifact ID")
            artifact_ids.add(artifact_id)
            relative = _text(artifact.get("file"), "artifact file")
            if Path(relative).parent != Path(identity) or relative in expected_files:
                raise ReviewError("artifact must belong to its anonymous candidate")
            expected_files.add(relative)
            path = _inside(supervisor_dir, relative)
            if _sha(path.read_bytes()) != _hash(artifact.get("sha256"), "artifact sha256"):
                raise ReviewError("review artifact changed")
            if identity == candidate_id:
                artifacts[artifact_id] = artifact
    if candidate_id not in candidate_ids:
        raise ReviewError("assessment must identify exactly one current anonymous candidate")
    actual_files: set[str] = set()
    for path in supervisor_dir.rglob("*"):
        if path.is_symlink():
            raise ReviewError("unexpected symlink in supervisor input")
        relative = str(path.relative_to(supervisor_dir))
        if path.is_dir():
            if relative not in candidate_ids:
                raise ReviewError("unexpected directory in fresh supervisor input")
        else:
            actual_files.add(relative)
    if actual_files != expected_files:
        raise ReviewError("unexpected or missing file in fresh supervisor input")
    return packet, artifacts


def _evidence(value: object, artifacts: Mapping[str, dict[str, object]], supervisor_dir: Path) -> list[dict[str, object]]:
    if not isinstance(value, list) or not value:
        raise ReviewError("nonempty artifact evidence is required")
    result: list[dict[str, object]] = []
    for item in value:
        reference = _mapping(item, "evidence reference")
        identity = _text(reference.get("artifact_id"), "evidence artifact_id")
        artifact = artifacts.get(identity)
        if artifact is None or reference.get("sha256") != artifact["sha256"]:
            raise ReviewError("evidence must bind a current candidate artifact hash")
        locator = _text(reference.get("locator"), "evidence locator")
        path = _inside(supervisor_dir.resolve(), str(artifact["file"]))
        match = re.fullmatch(r"L([1-9][0-9]*)(?:-L([1-9][0-9]*))?", locator)
        if not match:
            raise ReviewError("evidence locator must be L<number> or L<number>-L<number>")
        start, end = int(match[1]), int(match[2] or match[1])
        if start > end or end > len(path.read_text().splitlines()):
            raise ReviewError("evidence line locator is outside its artifact")
        result.append(reference)
    return result


def _reproduction(value: object, artifacts: Mapping[str, dict[str, object]], supervisor_dir: Path, evidence_scope: str) -> None:
    references = _evidence(value, artifacts, supervisor_dir)
    for reference in references:
        artifact = artifacts[str(reference["artifact_id"])]
        path = supervisor_dir / str(artifact["file"])
        if path.suffix != ".json":
            continue
        receipt = _read_json(path)
        if receipt.get("kind") != "independent_reproduction" or receipt.get("status") != "PASS":
            continue
        if receipt.get("evidence_scope") != evidence_scope:
            raise ReviewError("fixture and research reproduction scopes cannot be mixed")
        producers = _texts(receipt.get("producer_session_ids"), "producer sessions")
        reproducer = _text(receipt.get("reproducer_session_id"), "reproducer session")
        if reproducer in producers or receipt.get("exit_code") != 0 or isinstance(receipt.get("exit_code"), bool):
            raise ReviewError("independent successful reproduction is required")
        _text(receipt.get("execution_id"), "reproduction execution_id")
        _texts(receipt.get("command"), "reproduction command")
        _hash(receipt.get("environment_sha256"), "reproduction environment")
        for key in ("input_sha256", "output_sha256"):
            for digest in _texts(receipt.get(key), key):
                _hash(digest, key)
        return
    raise ReviewError("independent reproduction execution receipt is absent")


def assess(assessment: dict[str, object], supervisor_dir: Path) -> dict[str, object]:
    """Validate one supervisor judgment; scientific truth remains the reviewer's duty."""
    candidate_id = _text(assessment.get("candidate_id"), "assessment candidate_id")
    packet, artifacts = _packet_candidate(supervisor_dir, candidate_id)
    for key in ("round_id", "supervisor_session_id", "layer"):
        if assessment.get(key) != packet.get(key):
            raise ReviewError(f"assessment {key} does not match its fresh round")
    if packet.get("evidence_scope") not in SCOPES or packet.get("rubric") != list(DIMENSIONS):
        raise ReviewError("packet scope or frozen rubric changed")
    session = _mapping(assessment.get("session_attestation"), "session attestation")
    if session.get("fresh_session") is not True or session.get("received_only_packet") is not True or session.get("previous_scores_received") is not False:
        raise ReviewError("supervisor must attest fresh packet-only input without previous scores")
    dimensions = _mapping(assessment.get("dimensions"), "quality dimensions")
    if set(dimensions) != set(DIMENSIONS):
        raise ReviewError("all six fixed quality dimensions are required")
    failures: list[str] = []
    for name in DIMENSIONS:
        dimension = _mapping(dimensions[name], name)
        if dimension.get("status") not in {"PASS", "FAIL", "UNCONFIRMED"}:
            raise ReviewError("invalid dimension status")
        _text(dimension.get("rationale"), "dimension rationale")
        if dimension["status"] == "PASS":
            _evidence(dimension.get("evidence"), artifacts, supervisor_dir)
        else:
            failures.append(name)
    findings = assessment.get("findings")
    if not isinstance(findings, list):
        raise ReviewError("findings must be an explicit list, including when empty")
    finding_ids: set[str] = set()
    unresolved: list[str] = []
    for raw in findings:
        finding = _mapping(raw, "finding")
        identity = _text(finding.get("finding_id"), "finding_id")
        if identity in finding_ids:
            raise ReviewError("finding IDs must be unique")
        finding_ids.add(identity)
        severity = finding.get("severity")
        if severity not in {"Critical", "Major", "Minor", "Style"}:
            raise ReviewError("invalid finding severity")
        for key in ("impact", "minimum_fix", "recheck"):
            _text(finding.get(key), key)
        _evidence(finding.get("evidence"), artifacts, supervisor_dir)
        resolution = finding.get("resolution")
        if resolution is not None:
            resolution = _mapping(resolution, "finding resolution")
            if resolution.get("status") not in {"FIXED", "REBUTTAL_ACCEPTED"}:
                raise ReviewError("unaccepted rebuttals do not resolve a finding")
            if resolution.get("reviewed_by_session_id") != packet["supervisor_session_id"]:
                raise ReviewError("resolution must be accepted by this fresh supervisor")
            _text(resolution.get("justification"), "resolution justification")
            _evidence(resolution.get("evidence"), artifacts, supervisor_dir)
            _evidence(resolution.get("recheck_evidence"), artifacts, supervisor_dir)
        elif severity in {"Critical", "Major"}:
            unresolved.append(identity)
    if not failures and not unresolved:
        _reproduction(assessment.get("independent_reproduction_evidence"), artifacts, supervisor_dir, str(packet["evidence_scope"]))
    passed = not failures and not unresolved
    scope = packet["evidence_scope"]
    return {
        "schema_version": "project-research-assessment/v1",
        "candidate_id": candidate_id,
        "round_id": packet["round_id"],
        "supervisor_session_id": packet["supervisor_session_id"],
        "layer": packet["layer"],
        "evidence_scope": scope,
        "quality": ("APPARATUS_PASS" if scope == "apparatus_only" else "AAA") if passed else "NOT_AAA",
        "failed_dimensions": failures,
        "unresolved_critical_major": unresolved,
        "superiority": "NOT_ASSESSED",
        "pi_acceptance": "PENDING",
        "assessment_sha256": _sha(_json_bytes(assessment)),
        "limitation": "Receipt linkage and reviewer attestation are checked; OS custody and scientific truth require independent evidence.",
    }


def verify_round_packet(round_dir: Path) -> dict[str, object]:
    """Bind the current supervisor packet to the private controller preparation."""
    round_dir = _no_symlinks(round_dir)
    supervisor = round_dir / "supervisor"
    private = _read_json(round_dir / "controller" / "mapping.json")
    if _sha((supervisor / "packet.json").read_bytes()) != private.get("packet_sha256"):
        raise ReviewError("supervisor packet changed since controller preparation")
    packet = _read_json(supervisor / "packet.json")
    if packet.get("round_id") != private.get("round_id"):
        raise ReviewError("controller and supervisor round identities differ")
    return private


def freeze_candidate(round_dir: Path, assessment: dict[str, object], destination: Path) -> dict[str, object]:
    """Snapshot an accepted candidate and stop that round; never tune this freeze."""
    round_dir = _no_symlinks(round_dir)
    destination = _no_symlinks(destination)
    supervisor = round_dir / "supervisor"
    private = verify_round_packet(round_dir)
    result = assess(assessment, supervisor)
    if result["quality"] not in {"AAA", "APPARATUS_PASS"}:
        raise ReviewError("unresolved quality failures prohibit candidate freeze")
    candidates = _mapping(private.get("candidates"), "controller mapping")
    candidate = _mapping(candidates.get(str(result["candidate_id"])), "controller candidate")
    workspaces = [Path(_text(_mapping(item, "candidate").get("workspace"), "workspace")) for item in candidates.values()]
    if destination.is_relative_to(round_dir) or any(destination.is_relative_to(path) or path.is_relative_to(destination) for path in workspaces):
        raise ReviewError("freeze destination must be outside producer and round directories")
    raw_artifacts = candidate.get("artifacts")
    if not isinstance(raw_artifacts, list) or not raw_artifacts:
        raise ReviewError("controller artifact manifest is absent")
    workspace = Path(str(candidate["workspace"]))
    copies: list[tuple[str, bytes]] = []
    manifest: list[dict[str, str]] = []
    for raw in raw_artifacts:
        artifact = _mapping(raw, "controller artifact")
        relative = _text(artifact.get("source"), "artifact source")
        data = _inside(workspace, relative).read_bytes()
        if _sha(data) != artifact.get("source_sha256"):
            raise ReviewError("candidate changed after blind review; a new review is required")
        copies.append((relative, data))
        manifest.append({"file": relative, "sha256": _sha(data)})
    receipt: dict[str, object] = {
        "schema_version": "project-research-freeze/v1",
        "freeze_id": "freeze-" + secrets.token_hex(16),
        "round_id": result["round_id"],
        "candidate_id": result["candidate_id"],
        "quality": result["quality"],
        "evidence_scope": result["evidence_scope"],
        "layer": result["layer"],
        "assessment_sha256": result["assessment_sha256"],
        "packet_sha256": private["packet_sha256"],
        "artifacts": manifest,
        "producer_workspaces": [str(path) for path in workspaces],
        "producer_identities": [str(item) for raw in candidates.values() for item in [_mapping(raw, "candidate").get("team_id"), *_texts(_mapping(raw, "candidate").get("authors"), "authors")]],
        "superiority": "NOT_ASSESSED",
        "pi_acceptance": "PENDING",
        "revision_policy": "This frozen candidate has one independent final evaluation. Revised candidates require new independent evaluation data.",
    }
    receipt["freeze_sha256"] = _sha(_json_bytes(receipt))
    selection_path = round_dir / "controller" / "selection.json"
    if selection_path.exists():
        raise ReviewError("this review round is already frozen")
    destination.mkdir(parents=True, exist_ok=False, mode=0o700)
    try:
        for relative, data in copies:
            target = destination / "artifacts" / relative
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            target.write_bytes(data)
            target.chmod(0o444)
        _write_new(destination / "assessment.json", assessment, 0o444)
        _write_new(destination / "freeze.json", receipt, 0o444)
        _write_new(selection_path, {"freeze_id": receipt["freeze_id"], "freeze_sha256": receipt["freeze_sha256"], "destination": str(destination)})
    except Exception:
        # Only this call's newly created destination is removed on failed commit.
        shutil.rmtree(destination)
        raise
    return receipt


def verify_freeze(freeze_dir: Path) -> dict[str, object]:
    freeze_dir = _no_symlinks(freeze_dir)
    receipt = _read_json(freeze_dir / "freeze.json")
    digest = receipt.pop("freeze_sha256", None)
    if _sha(_json_bytes(receipt)) != digest:
        raise ReviewError("freeze receipt changed")
    receipt["freeze_sha256"] = digest
    if receipt.get("evidence_scope") not in SCOPES or receipt.get("quality") != ("APPARATUS_PASS" if receipt.get("evidence_scope") == "apparatus_only" else "AAA"):
        raise ReviewError("freeze has no admissible quality judgment")
    if _sha((freeze_dir / "assessment.json").read_bytes()) != receipt.get("assessment_sha256"):
        raise ReviewError("frozen assessment changed")
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ReviewError("frozen artifacts are absent")
    expected: set[str] = set()
    for raw in artifacts:
        item = _mapping(raw, "frozen artifact")
        relative = _text(item.get("file"), "frozen artifact path")
        if relative in expected:
            raise ReviewError("duplicate frozen artifact")
        expected.add(relative)
        path = _inside(freeze_dir / "artifacts", relative)
        if _sha(path.read_bytes()) != item.get("sha256"):
            raise ReviewError("frozen candidate artifact changed")
    actual = {str(path.relative_to(freeze_dir / "artifacts")) for path in (freeze_dir / "artifacts").rglob("*") if not path.is_dir()}
    if actual != expected:
        raise ReviewError("frozen candidate file set changed")
    return receipt


def _validate_final_custody(freeze_dir: Path, freeze: dict[str, object], split_receipt: dict[str, object], registry_dir: Path) -> None:
    for workspace in _texts(freeze.get("producer_workspaces"), "producer workspaces"):
        path = Path(workspace)
        if registry_dir.is_relative_to(path) or path.is_relative_to(registry_dir):
            raise ReviewError("final registry must be external to producer workspaces")
    if registry_dir.is_relative_to(freeze_dir.resolve()) or freeze_dir.resolve().is_relative_to(registry_dir):
        raise ReviewError("registry and frozen candidate must be disjoint")
    split_id = _text(split_receipt.get("split_id"), "split_id")
    split_hash = _hash(split_receipt.get("split_sha256"), "split hash")
    evaluator = _text(split_receipt.get("evaluator_id"), "evaluator_id")
    if evaluator in _texts(freeze.get("producer_identities"), "producer identities"):
        raise ReviewError("the final evaluator must be independent of producer teams")
    if split_receipt.get("purpose") != "final_evaluation" or split_receipt.get("worker_access") is not False or split_receipt.get("independent_from_development") is not True:
        raise ReviewError("held-out evaluator custody and independence are required")
    development = [_hash(item, "development split hash") for item in _texts(split_receipt.get("development_split_sha256"), "development split hashes")]
    if split_hash in development:
        raise ReviewError("final data overlaps a development split")
    _texts(split_receipt.get("custody_evidence"), "custody evidence")
    _texts(split_receipt.get("independence_evidence"), "independence evidence")
    if split_receipt.get("evidence_scope") != freeze.get("evidence_scope"):
        raise ReviewError("fixture and research evidence scopes cannot be mixed")


def _evaluation_connection(registry_dir: Path) -> sqlite3.Connection:
    registry_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    database = _no_symlinks(registry_dir / "final-evaluations.sqlite3")
    connection = sqlite3.connect(database, timeout=10, isolation_level=None)
    try:
        database.chmod(0o600)
        connection.execute("CREATE TABLE IF NOT EXISTS reservations (reservation_id TEXT PRIMARY KEY, freeze_sha256 TEXT UNIQUE NOT NULL, split_id TEXT UNIQUE NOT NULL, split_sha256 TEXT UNIQUE NOT NULL, receipt_json TEXT NOT NULL)")
        connection.execute("CREATE TABLE IF NOT EXISTS comparison_batches (batch_id TEXT PRIMARY KEY, split_id TEXT UNIQUE NOT NULL, split_sha256 TEXT UNIQUE NOT NULL, receipt_json TEXT NOT NULL)")
        connection.execute("CREATE TABLE IF NOT EXISTS comparison_members (freeze_sha256 TEXT PRIMARY KEY, batch_id TEXT NOT NULL REFERENCES comparison_batches(batch_id), condition TEXT NOT NULL, UNIQUE(batch_id, condition))")
        return connection
    except BaseException:
        connection.close()
        raise


def _unused_final_resources(connection: sqlite3.Connection, freezes: Sequence[dict[str, object]], split_receipt: dict[str, object]) -> None:
    for table in ("reservations", "comparison_batches"):
        if connection.execute(f"SELECT 1 FROM {table} WHERE split_id=? OR split_sha256=?", (split_receipt["split_id"], split_receipt["split_sha256"])).fetchone():
            raise ReviewError("independent final split was already consumed; no later comparison members or revisions")
    for freeze in freezes:
        for table in ("reservations", "comparison_members"):
            if connection.execute(f"SELECT 1 FROM {table} WHERE freeze_sha256=?", (freeze["freeze_sha256"],)).fetchone():
                raise ReviewError("candidate was already consumed; preserve failed attempts")


def reserve_final_evaluation(freeze_dir: Path, split_receipt: dict[str, object], registry_dir: Path) -> dict[str, object]:
    """Consume one candidate/split across both individual and comparison use.

    This ledger operation does not execute an evaluator. The controller must
    retain the same registry across campaigns, including failures and retries.
    """
    freeze = verify_freeze(freeze_dir)
    registry_dir = _no_symlinks(registry_dir)
    _validate_final_custody(freeze_dir, freeze, split_receipt, registry_dir)
    connection = _evaluation_connection(registry_dir)
    try:
        reservation: dict[str, object] = {
            "schema_version": "project-research-final-reservation/v1",
            "reservation_id": "evaluation-" + secrets.token_hex(16),
            "freeze_sha256": freeze["freeze_sha256"],
            "split_id": split_receipt["split_id"],
            "split_sha256": split_receipt["split_sha256"],
            "evaluator_id": split_receipt["evaluator_id"],
            "split_receipt_sha256": _sha(_json_bytes(split_receipt)),
            "evidence_scope": freeze["evidence_scope"],
            "status": "APPARATUS_RESERVATION" if freeze["evidence_scope"] == "apparatus_only" else "FINAL_EVALUATION_RESERVED",
            "execution_started": False,
            "superiority": "NOT_ASSESSED",
            "pi_acceptance": "PENDING",
        }
        connection.execute("BEGIN IMMEDIATE")
        try:
            _unused_final_resources(connection, [freeze], split_receipt)
            connection.execute("INSERT INTO reservations VALUES (?, ?, ?, ?, ?)", (reservation["reservation_id"], freeze["freeze_sha256"], split_receipt["split_id"], split_receipt["split_sha256"], _json_bytes({"reservation": reservation, "split_custody_receipt": split_receipt}).decode()))
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise
        return reservation
    finally:
        connection.close()


def reserve_comparison_batch(freeze_dirs: Sequence[Path], split_receipt: dict[str, object], registry_dir: Path) -> dict[str, object]:
    """Freeze all B/P or B/H/P members before any final result is revealed.

    The split is consumed once by the whole batch. Every member is registered in
    that same transaction; later additions, revisions and single-use fallbacks
    cannot consume it again, even if an evaluation fails before returning data.
    """
    if len(freeze_dirs) not in {2, 3}:
        raise ReviewError("comparison requires exactly B/P or B/H/P frozen members")
    registry_dir = _no_symlinks(registry_dir)
    freezes = [verify_freeze(path) for path in freeze_dirs]
    hashes = [str(freeze["freeze_sha256"]) for freeze in freezes]
    if len(set(hashes)) != len(hashes):
        raise ReviewError("comparison members must be distinct frozen candidates")
    if split_receipt.get("results_revealed") is not False:
        raise ReviewError("comparison membership must be registered before results are revealed")
    conditions = _mapping(split_receipt.get("candidate_conditions"), "candidate conditions")
    expected = {"B", "P"} if len(freezes) == 2 else {"B", "H", "P"}
    if set(conditions) != set(hashes) or not all(isinstance(value, str) for value in conditions.values()) or set(conditions.values()) != expected:
        raise ReviewError("conditions must identify every B/P or B/H/P frozen member exactly once")
    if len({freeze["layer"] for freeze in freezes}) != 1:
        raise ReviewError("comparison members must belong to the same assessment layer")
    for path, freeze in zip(freeze_dirs, freezes):
        _validate_final_custody(path, freeze, split_receipt, registry_dir)
    members = sorted([
        {"freeze_id": freeze["freeze_id"], "freeze_sha256": freeze["freeze_sha256"], "candidate_id": freeze["candidate_id"], "condition": conditions[str(freeze["freeze_sha256"])]}
        for freeze in freezes
    ], key=lambda member: str(member["condition"]))
    reservation: dict[str, object] = {
        "schema_version": "project-research-comparison-reservation/v1",
        "batch_id": "comparison-" + secrets.token_hex(16),
        "split_id": split_receipt["split_id"],
        "split_sha256": split_receipt["split_sha256"],
        "evaluator_id": split_receipt["evaluator_id"],
        "split_receipt_sha256": _sha(_json_bytes(split_receipt)),
        "members": members,
        "membership_sha256": _sha(_json_bytes(members)),
        "membership_frozen": True,
        "results_revealed": False,
        "evidence_scope": freezes[0]["evidence_scope"],
        "status": "APPARATUS_COMPARISON_RESERVATION" if freezes[0]["evidence_scope"] == "apparatus_only" else "COMPARISON_EVALUATION_RESERVED",
        "execution_started": False,
        "superiority": "NOT_ASSESSED",
        "pi_acceptance": "PENDING",
    }
    connection = _evaluation_connection(registry_dir)
    try:
        connection.execute("BEGIN IMMEDIATE")
        try:
            _unused_final_resources(connection, freezes, split_receipt)
            connection.execute("INSERT INTO comparison_batches VALUES (?, ?, ?, ?)", (reservation["batch_id"], split_receipt["split_id"], split_receipt["split_sha256"], _json_bytes({"reservation": reservation, "split_custody_receipt": split_receipt}).decode()))
            connection.executemany("INSERT INTO comparison_members VALUES (?, ?, ?)", [(member["freeze_sha256"], reservation["batch_id"], member["condition"]) for member in members])
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise
        return reservation
    finally:
        connection.close()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    blind = subparsers.add_parser("blind")
    blind.add_argument("spec", type=Path)
    blind.add_argument("output", type=Path)
    judge = subparsers.add_parser("assess")
    judge.add_argument("assessment", type=Path)
    judge.add_argument("supervisor_dir", type=Path)
    freeze = subparsers.add_parser("freeze")
    freeze.add_argument("round_dir", type=Path)
    freeze.add_argument("assessment", type=Path)
    freeze.add_argument("destination", type=Path)
    reserve = subparsers.add_parser("reserve-final")
    reserve.add_argument("freeze_dir", type=Path)
    reserve.add_argument("split_receipt", type=Path)
    reserve.add_argument("registry_dir", type=Path)
    batch = subparsers.add_parser("reserve-comparison")
    batch.add_argument("split_receipt", type=Path)
    batch.add_argument("registry_dir", type=Path)
    batch.add_argument("freeze_dirs", type=Path, nargs="+")
    args = parser.parse_args(argv)
    try:
        if args.command == "blind":
            spec = _read_json(args.spec)
            raw = spec.get("candidates")
            if not isinstance(raw, list):
                raise ReviewError("candidate specifications must be a list")
            candidates = []
            for item in raw:
                item = _mapping(item, "candidate")
                candidates.append(CandidateSpec(_text(item.get("candidate_id"), "candidate_id"), _text(item.get("team_id"), "team_id"), Path(_text(item.get("workspace"), "workspace")), tuple(_texts(item.get("artifacts"), "artifacts")), tuple(_texts(item.get("authors"), "authors")), tuple(_texts(item.get("models"), "models"))))
            result = build_blind_round(candidates, args.output, layer=str(spec.get("layer", "research_operations")), evidence_scope=str(spec.get("evidence_scope", "apparatus_only")))
        elif args.command == "assess":
            result = assess(_read_json(args.assessment), args.supervisor_dir)
        elif args.command == "freeze":
            result = freeze_candidate(args.round_dir, _read_json(args.assessment), args.destination)
        elif args.command == "reserve-final":
            result = reserve_final_evaluation(args.freeze_dir, _read_json(args.split_receipt), args.registry_dir)
        else:
            result = reserve_comparison_batch(args.freeze_dirs, _read_json(args.split_receipt), args.registry_dir)
        print(_json_bytes(result).decode(), end="")
        return 0
    except (ReviewError, OSError, sqlite3.Error) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
