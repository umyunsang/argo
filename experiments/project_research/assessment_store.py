"""Controller-only review imports and final reservations at fixed private paths.

Worker and supervisor processes must not mount ROOT/control or ROOT/evaluator.
This module imports verified quality records; it never infers superiority or a
PI decision and does not execute any evaluator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .contracts import canonical, digest, utc_now, validate_record
from .review import (
    ReviewError,
    assess,
    reserve_comparison_batch,
    reserve_final_evaluation,
    verify_freeze,
    verify_round_packet,
)
from .state import AdmissionError, Store


ROOT = Path.home() / ".local/share/argo-project-research-20260909"


def _canonical_path(path: Path) -> Path:
    path = path.absolute()
    if any(part.is_symlink() for part in (path, *path.parents)) or path != path.resolve():
        raise ReviewError("controller paths must be canonical and contain no symlinks")
    return path


def _controller_path(path: Path) -> Path:
    path = _canonical_path(path)
    control = _canonical_path(ROOT / "control")
    evaluator = _canonical_path(ROOT / "evaluator")
    if not (path.is_relative_to(control) or path.is_relative_to(evaluator)):
        raise ReviewError("review imports require controller/evaluator custody outside worker outputs")
    return path


def _document(path: Path) -> dict[str, object]:
    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in items:
            if key in result:
                raise ReviewError("duplicate JSON keys are not admitted")
            result[key] = value
        return result

    try:
        document = json.loads(_controller_path(path).read_text(), object_pairs_hook=pairs)
        if not isinstance(document, dict):
            raise ReviewError("controller document must be an object")
        canonical(document)
        return document
    except (ValueError, UnicodeError) as exc:
        raise ReviewError("invalid controller JSON document") from exc


def _store() -> Store:
    path = _canonical_path(ROOT / "control" / "state.sqlite")
    if not path.is_file():
        raise AdmissionError("initialize the fixed programme store before importing assessments")
    return Store(path)


def import_assessment(
    project_id: str,
    round_dir: Path,
    assessment: dict[str, object],
    *,
    freeze_dir: Path | None = None,
) -> dict[str, object]:
    """Import a current validated judgment while retaining the four-record schema.

    Raw Store.append cannot promote final outcomes. This narrow path validates
    packet and artifact hashes, the review rubric, and an AAA candidate's freeze
    before one immutable database insertion. PI always remains PENDING.
    """
    if not isinstance(project_id, str) or not project_id.strip():
        raise ReviewError("project_id is required")
    round_dir = _controller_path(round_dir)
    private = verify_round_packet(round_dir)
    result = assess(assessment, round_dir / "supervisor")
    frozen = None
    if freeze_dir is not None:
        freeze_dir = _controller_path(freeze_dir)
        frozen = verify_freeze(freeze_dir)
        for key in ("round_id", "candidate_id", "assessment_sha256", "quality", "evidence_scope", "layer"):
            if frozen.get(key) != result.get(key):
                raise ReviewError("frozen candidate does not match the validated assessment")
        selection = _document(round_dir / "controller" / "selection.json")
        if frozen.get("packet_sha256") != private.get("packet_sha256") or selection.get("freeze_sha256") != frozen.get("freeze_sha256"):
            raise ReviewError("frozen candidate does not match the controller's selected packet")
    if result["quality"] == "AAA" and frozen is None:
        raise ReviewError("research AAA import requires its validated candidate freeze")
    quality = {"AAA": "AAA", "NOT_AAA": "REWORK", "APPARATUS_PASS": "UNASSESSED"}[str(result["quality"])]
    identity = {
        "project_id": project_id,
        "round_id": result["round_id"],
        "candidate_id": result["candidate_id"],
        "assessment_sha256": result["assessment_sha256"],
        "packet_sha256": private["packet_sha256"],
        "freeze_sha256": frozen["freeze_sha256"] if frozen else None,
    }
    record: dict[str, object] = {
        "type": "Assessment",
        "id": "assessment-" + digest(identity),
        "project_id": project_id,
        "created_at": utc_now(),
        "layer": result["layer"],
        "round_id": result["round_id"],
        "session_id": result["supervisor_session_id"],
        "candidate_id": result["candidate_id"],
        "findings": assessment["findings"],
        "quality": quality,
        "review_quality": result["quality"],
        "evidence_scope": result["evidence_scope"],
        "superiority": "NOT_ASSESSED",
        "pi_acceptance": "PENDING",
        "validation": {"identity": identity, "review_result": result, "round_dir": str(round_dir), "freeze_dir": str(freeze_dir) if freeze_dir else None},
        "review_input": assessment,
    }
    validate_record(record)
    store = _store()
    with store.transaction() as database:
        if not database.execute("SELECT 1 FROM projects WHERE id=?", (project_id,)).fetchone():
            raise AdmissionError("unknown project")
        # Recheck the packet at the persistence boundary, after all evidence reads.
        if verify_round_packet(round_dir).get("packet_sha256") != identity["packet_sha256"]:
            raise ReviewError("review packet changed before assessment persistence")
        existing = database.execute("SELECT sha, body FROM records WHERE id=?", (record["id"],)).fetchone()
        if existing:
            original = json.loads(existing["body"])
            if digest(original) != existing["sha"] or original.get("validation", {}).get("identity") != identity:
                raise AdmissionError("assessment import identity or stored record changed")
            return original
        database.execute("INSERT INTO records VALUES(?,?,?,?,?)", (record["id"], record["type"], project_id, digest(record), canonical(record)))
        database.execute("INSERT INTO events(at,body) VALUES(?,?)", (utc_now(), canonical({
            "event": "validated_assessment_import", "project_id": project_id,
            "record_id": record["id"], "quality": quality, "review_quality": result["quality"],
            "evidence_scope": result["evidence_scope"], "pi_acceptance": "PENDING",
        })))
    return record


def reserve_final(freeze_dir: Path, split_receipt: dict[str, object]) -> dict[str, object]:
    """Controller wrapper: callers cannot select an empty replacement registry."""
    return reserve_final_evaluation(
        _controller_path(freeze_dir), split_receipt,
        _canonical_path(ROOT / "control" / "evaluation-registry"),
    )


def reserve_comparison(freeze_dirs: Sequence[Path], split_receipt: dict[str, object]) -> dict[str, object]:
    """Reserve a fixed B/P or B/H/P batch in the same global evaluator registry."""
    return reserve_comparison_batch(
        [_controller_path(path) for path in freeze_dirs], split_receipt,
        _canonical_path(ROOT / "control" / "evaluation-registry"),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    importer = commands.add_parser("import-assessment")
    importer.add_argument("project_id")
    importer.add_argument("round_dir", type=Path)
    importer.add_argument("assessment", type=Path)
    importer.add_argument("--freeze-dir", type=Path)
    single = commands.add_parser("reserve-final")
    single.add_argument("freeze_dir", type=Path)
    single.add_argument("split_receipt", type=Path)
    batch = commands.add_parser("reserve-comparison")
    batch.add_argument("split_receipt", type=Path)
    batch.add_argument("freeze_dirs", nargs="+", type=Path)
    args = parser.parse_args(argv)
    if args.command == "import-assessment":
        result = import_assessment(args.project_id, args.round_dir, _document(args.assessment), freeze_dir=args.freeze_dir)
    elif args.command == "reserve-final":
        result = reserve_final(args.freeze_dir, _document(args.split_receipt))
    else:
        result = reserve_comparison(args.freeze_dirs, _document(args.split_receipt))
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
