"""Controller import fixtures; no scientific AAA or PI decision is produced."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.project_research import assessment_store
from experiments.project_research.contracts import make_contract
from experiments.project_research.review import CandidateSpec, DIMENSIONS, ReviewError, assess, build_blind_round, freeze_candidate, verify_freeze
from experiments.project_research.state import AdmissionError, Store


def sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class AssessmentStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="assessment-import-fixture-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        patcher = patch.object(assessment_store, "ROOT", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        (self.root / "control").mkdir()
        (self.root / "evaluator").mkdir()
        self.store = Store(self.root / "control" / "state.sqlite")
        self.store.append(make_contract("fixture-project", "wine", "P", False, "fixture-pool"))

    def round_fixture(self, name: str) -> tuple[Path, dict[str, object]]:
        candidates = []
        reproduction = {
            "kind": "independent_reproduction", "status": "PASS", "evidence_scope": "apparatus_only",
            "producer_session_ids": ["producer-session"], "reproducer_session_id": "independent-session",
            "execution_id": "fixture-execution", "exit_code": 0, "command": ["python3", "fixture.py"],
            "environment_sha256": sha("fixture environment"), "input_sha256": [sha("fixture input")],
            "output_sha256": [sha("fixture output")],
        }
        for index in range(2):
            workspace = self.root / "worker" / name / f"lane-{index}"
            workspace.mkdir(parents=True)
            (workspace / "report.md").write_text("Question: what is the residual?\nFixture evidence only.\n")
            (workspace / "reproduction.json").write_text(json.dumps(reproduction))
            candidates.append(CandidateSpec(f"source-{name}-{index}", f"team-{name}-{index}", workspace, ("report.md", "reproduction.json"), (f"researcher-{name}-{index}",), (f"engine-{name}-{index}",)))
        round_dir = self.root / "control" / "rounds" / name
        paths = build_blind_round(candidates, round_dir)
        packet = json.loads(Path(paths["packet"]).read_text())
        candidate = packet["candidates"][0]
        report = next(item for item in candidate["artifacts"] if item["file"].endswith(".md"))
        reproduction_artifact = next(item for item in candidate["artifacts"] if item["file"].endswith(".json"))
        evidence = [{"artifact_id": report["artifact_id"], "sha256": report["sha256"], "locator": "L2"}]
        assessment = {
            "round_id": packet["round_id"], "supervisor_session_id": packet["supervisor_session_id"],
            "candidate_id": candidate["candidate_id"], "layer": packet["layer"],
            "session_attestation": {"fresh_session": True, "received_only_packet": True, "previous_scores_received": False},
            "dimensions": {dimension: {"status": "PASS", "rationale": "Apparatus-only test evidence.", "evidence": copy.deepcopy(evidence)} for dimension in DIMENSIONS},
            "findings": [],
            "independent_reproduction_evidence": [{"artifact_id": reproduction_artifact["artifact_id"], "sha256": reproduction_artifact["sha256"], "locator": "L1"}],
        }
        return round_dir, assessment

    def freeze_fixture(self, name: str) -> tuple[Path, dict[str, object], Path]:
        round_dir, assessment = self.round_fixture(name)
        frozen = self.root / "control" / "freezes" / name
        freeze_candidate(round_dir, assessment, frozen)
        return round_dir, assessment, frozen

    def split(self) -> dict[str, object]:
        return {
            "split_id": "fixture-final", "split_sha256": sha("final fixture data"), "purpose": "final_evaluation",
            "evaluator_id": "independent-evaluator", "worker_access": False,
            "independent_from_development": True, "development_split_sha256": [sha("development fixture data")],
            "custody_evidence": ["Apparatus fixture only."], "independence_evidence": ["Apparatus fixture only."],
            "evidence_scope": "apparatus_only",
        }

    def assessment_records(self) -> list[dict]:
        return [record for record in self.store.snapshot()["records"] if record["type"] == "Assessment"]

    def test_validated_fixture_import_preserves_scope_and_pending_pi(self) -> None:
        round_dir, assessment = self.round_fixture("scope")
        assessment["pi_acceptance"] = "ACCEPTED"
        assessment["superiority"] = "SUPERIOR"
        imported = assessment_store.import_assessment("fixture-project", round_dir, assessment)
        self.assertEqual(imported["quality"], "UNASSESSED")
        self.assertEqual(imported["review_quality"], "APPARATUS_PASS")
        self.assertEqual(imported["evidence_scope"], "apparatus_only")
        self.assertEqual(imported["pi_acceptance"], "PENDING")
        self.assertEqual(imported["superiority"], "NOT_ASSESSED")
        self.assertEqual(imported["session_id"], assessment["supervisor_session_id"])
        self.assertEqual(len(self.assessment_records()), 1)

    def test_matching_freeze_import_is_immutable_and_idempotent(self) -> None:
        round_dir, assessment, frozen = self.freeze_fixture("matching")
        first = assessment_store.import_assessment("fixture-project", round_dir, assessment, freeze_dir=frozen)
        second = assessment_store.import_assessment("fixture-project", round_dir, assessment, freeze_dir=frozen)
        self.assertEqual(first, second)
        self.assertEqual(first["validation"]["identity"]["freeze_sha256"], verify_freeze(frozen)["freeze_sha256"])
        self.assertEqual(len(self.assessment_records()), 1)
        events = [item for item in self.store.snapshot()["events"] if item["event"] == "validated_assessment_import"]
        self.assertEqual(len(events), 1)

    def test_unresolved_review_imports_as_rework_without_a_freeze(self) -> None:
        round_dir, assessment = self.round_fixture("rework")
        assessment["dimensions"]["claim_scope"]["status"] = "UNCONFIRMED"
        result = assessment_store.import_assessment("fixture-project", round_dir, assessment)
        self.assertEqual(result["quality"], "REWORK")
        self.assertEqual(result["review_quality"], "NOT_AAA")
        self.assertIsNone(result["validation"]["identity"]["freeze_sha256"])
        self.assertEqual(result["pi_acceptance"], "PENDING")

    def test_invalid_or_changed_review_cannot_enter_store(self) -> None:
        round_dir, assessment = self.round_fixture("changed")
        invalid = copy.deepcopy(assessment)
        del invalid["dimensions"]["correctness"]
        with self.assertRaisesRegex(ReviewError, "all six"):
            assessment_store.import_assessment("fixture-project", round_dir, invalid)
        report = next((round_dir / "supervisor").rglob("*.md"))
        report.chmod(0o600)
        report.write_text("Changed reviewed evidence.\n")
        with self.assertRaisesRegex(ReviewError, "artifact changed"):
            assessment_store.import_assessment("fixture-project", round_dir, assessment)
        self.assertFalse(self.assessment_records())

    def test_rewritten_packet_is_rejected_even_when_json_is_equivalent(self) -> None:
        round_dir, assessment = self.round_fixture("packet")
        packet = round_dir / "supervisor" / "packet.json"
        packet.chmod(0o600)
        packet.write_text(packet.read_text() + " ")
        with self.assertRaisesRegex(ReviewError, "packet changed"):
            assessment_store.import_assessment("fixture-project", round_dir, assessment)
        self.assertFalse(self.assessment_records())

    def test_wrong_candidate_freeze_is_rejected(self) -> None:
        round_dir, assessment, _ = self.freeze_fixture("original")
        _, _, other = self.freeze_fixture("different")
        with self.assertRaisesRegex(ReviewError, "does not match"):
            assessment_store.import_assessment("fixture-project", round_dir, assessment, freeze_dir=other)
        self.assertFalse(self.assessment_records())

    def test_modified_frozen_artifact_is_rejected(self) -> None:
        round_dir, assessment, frozen = self.freeze_fixture("frozen")
        artifact = frozen / "artifacts" / "report.md"
        artifact.chmod(0o600)
        artifact.write_text("Changed after freeze.\n")
        with self.assertRaisesRegex(ReviewError, "frozen candidate artifact changed"):
            assessment_store.import_assessment("fixture-project", round_dir, assessment, freeze_dir=frozen)
        self.assertFalse(self.assessment_records())

    def test_research_aaa_cannot_be_imported_without_matching_freeze(self) -> None:
        round_dir, assessment = self.round_fixture("no-freeze")
        hypothetical = {**assess(assessment, round_dir / "supervisor"), "quality": "AAA", "evidence_scope": "development_research"}
        with patch.object(assessment_store, "assess", return_value=hypothetical):
            with self.assertRaisesRegex(ReviewError, "AAA import requires"):
                assessment_store.import_assessment("fixture-project", round_dir, assessment)
        self.assertFalse(self.assessment_records())

    def test_import_does_not_open_raw_terminal_assessment_bypass(self) -> None:
        round_dir, assessment = self.round_fixture("raw")
        imported = assessment_store.import_assessment("fixture-project", round_dir, assessment)
        for field, value in (("quality", "AAA"), ("pi_acceptance", "ACCEPTED"), ("superiority", "SUPERIOR")):
            forged = copy.deepcopy(imported)
            forged["id"] = "raw-" + field
            forged[field] = value
            with self.subTest(field=field), self.assertRaises(AdmissionError):
                self.store.append(forged)
        self.assertEqual(len(self.assessment_records()), 1)

    def test_unknown_project_and_worker_custody_cannot_import(self) -> None:
        round_dir, assessment = self.round_fixture("unknown")
        with self.assertRaisesRegex(AdmissionError, "unknown project"):
            assessment_store.import_assessment("different-project", round_dir, assessment)
        with self.assertRaisesRegex(ReviewError, "custody"):
            assessment_store.import_assessment("fixture-project", self.root / "worker" / "round", assessment)
        self.assertFalse(self.assessment_records())

    def test_fixed_single_and_batch_wrappers_share_consumed_split_history(self) -> None:
        _, _, first = self.freeze_fixture("single")
        _, _, second = self.freeze_fixture("batch-second")
        _, _, third = self.freeze_fixture("batch-third")
        reservation = assessment_store.reserve_final(first, self.split())
        self.assertFalse(reservation["execution_started"])
        registry = self.root / "control" / "evaluation-registry" / "final-evaluations.sqlite3"
        self.assertTrue(registry.is_file())
        split = self.split()
        split.update(results_revealed=False, candidate_conditions={verify_freeze(second)["freeze_sha256"]: "B", verify_freeze(third)["freeze_sha256"]: "P"})
        with self.assertRaisesRegex(ReviewError, "already consumed"):
            assessment_store.reserve_comparison([second, third], split)

    def test_comparison_wrapper_uses_fixed_registry_without_executing_evaluator(self) -> None:
        _, _, first = self.freeze_fixture("baseline")
        _, _, second = self.freeze_fixture("proposal")
        split = self.split()
        split.update(results_revealed=False, candidate_conditions={verify_freeze(first)["freeze_sha256"]: "B", verify_freeze(second)["freeze_sha256"]: "P"})
        result = assessment_store.reserve_comparison([first, second], split)
        self.assertEqual(result["status"], "APPARATUS_COMPARISON_RESERVATION")
        self.assertEqual(result["pi_acceptance"], "PENDING")
        self.assertTrue((self.root / "control" / "evaluation-registry" / "final-evaluations.sqlite3").is_file())
        with self.assertRaises(TypeError):
            assessment_store.reserve_comparison([first, second], split, registry_dir=self.root / "empty-registry")
        self.assertFalse((self.root / "empty-registry").exists())

    def test_registry_symlink_cannot_select_an_empty_worker_registry(self) -> None:
        _, _, frozen = self.freeze_fixture("symlink")
        replacement = self.root / "worker" / "empty-registry"
        replacement.mkdir(parents=True)
        (self.root / "control" / "evaluation-registry").symlink_to(replacement, target_is_directory=True)
        with self.assertRaisesRegex(ReviewError, "canonical"):
            assessment_store.reserve_final(frozen, self.split())
        self.assertFalse((replacement / "final-evaluations.sqlite3").exists())


if __name__ == "__main__":
    unittest.main()
