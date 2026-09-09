"""Apparatus-only fixtures: none of these results is research AAA or efficacy evidence."""

from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from review import (
    CandidateSpec,
    DIMENSIONS,
    ReviewError,
    assess,
    build_blind_round,
    freeze_candidate,
    main,
    reserve_comparison_batch,
    reserve_final_evaluation,
    verify_freeze,
)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class ReviewControlsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="research-review-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.candidates: list[CandidateSpec] = []
        for index in range(2):
            workspace = self.root / f"workspace-{index}"
            workspace.mkdir()
            (workspace / "report.md").write_text(
                f"Author: Researcher{index}\nTeam: unit-{index}\nModel: engine-{index}\n"
                "Previous score: AAB\nThe observed residual is below the stated tolerance.\n"
                f"Researcher{index} reran this development setting.\n"
            )
            (workspace / "solver.py").write_text("def residual(matrix, x, b):\n    return matrix @ x - b\n")
            (workspace / "reproduction.json").write_text(json.dumps({
                "kind": "independent_reproduction",
                "status": "PASS",
                "evidence_scope": "apparatus_only",
                "producer_session_ids": ["initial-session"],
                "reproducer_session_id": "isolated-rerun-session",
                "execution_id": "local-fixture-execution",
                "exit_code": 0,
                "command": ["python3", "solver.py"],
                "environment_sha256": digest("fixture environment"),
                "input_sha256": [digest("fixture input")],
                "output_sha256": [digest("fixture output")],
                "metadata": {"authors": [f"Researcher{index}"], "model_id": f"engine-{index}", "previous_score": "AAA"},
            }))
            self.candidates.append(CandidateSpec(f"source-candidate-{index}", f"unit-{index}", workspace, ("report.md", "solver.py", "reproduction.json"), (f"Researcher{index}",), (f"engine-{index}",)))
        self.round_dir = self.root / "review-round"

    def build(self) -> dict[str, str]:
        return build_blind_round(self.candidates, self.round_dir)

    def fixture_assessment(self) -> tuple[dict[str, object], Path]:
        paths = self.build()
        supervisor = Path(paths["supervisor_dir"])
        packet = json.loads((supervisor / "packet.json").read_text())
        candidate = packet["candidates"][0]
        artifacts = candidate["artifacts"]
        report = next(item for item in artifacts if item["file"].endswith(".md"))
        reproduction = next(item for item in artifacts if item["file"].endswith(".json"))
        evidence = [{"artifact_id": report["artifact_id"], "sha256": report["sha256"], "locator": "L5"}]
        assessment = {
            "candidate_id": candidate["candidate_id"],
            "round_id": packet["round_id"],
            "supervisor_session_id": packet["supervisor_session_id"],
            "layer": packet["layer"],
            "session_attestation": {"fresh_session": True, "received_only_packet": True, "previous_scores_received": False},
            "dimensions": {name: {"status": "PASS", "rationale": "Fixture exercising the validation contract only.", "evidence": copy.deepcopy(evidence)} for name in DIMENSIONS},
            "findings": [],
            "independent_reproduction_evidence": [{"artifact_id": reproduction["artifact_id"], "sha256": reproduction["sha256"], "locator": "L1"}],
        }
        return assessment, supervisor

    def finding(self, assessment: dict[str, object], severity: str = "Major") -> dict[str, object]:
        return {
            "finding_id": "finding-residual",
            "severity": severity,
            "evidence": copy.deepcopy(assessment["dimensions"]["correctness"]["evidence"]),
            "impact": "This boundary could invalidate the conclusion.",
            "minimum_fix": "Check the independent residual at this boundary.",
            "recheck": "Repeat the named boundary and inspect the residual receipt.",
        }

    def split(self) -> dict[str, object]:
        return {
            "split_id": "held-out-fixture-one",
            "split_sha256": digest("held out fixture"),
            "purpose": "final_evaluation",
            "evaluator_id": "external-fixture-evaluator",
            "worker_access": False,
            "independent_from_development": True,
            "development_split_sha256": [digest("development fixture")],
            "custody_evidence": ["Fixture only: evaluator volume is absent from worker mounts."],
            "independence_evidence": ["Fixture only: development/final group identifiers are disjoint."],
            "evidence_scope": "apparatus_only",
        }

    def frozen_fixture(self) -> Path:
        assessment, _ = self.fixture_assessment()
        destination = self.root / "frozen"
        result = freeze_candidate(self.round_dir, assessment, destination)
        self.assertEqual(result["quality"], "APPARATUS_PASS")
        return destination

    def frozen_members(self, count: int) -> list[Path]:
        members = []
        for index in range(count):
            self.round_dir = self.root / f"comparison-round-{index}"
            assessment, _ = self.fixture_assessment()
            destination = self.root / f"comparison-freeze-{index}"
            freeze_candidate(self.round_dir, assessment, destination)
            members.append(destination)
        return members

    def comparison_split(self, members: list[Path]) -> dict[str, object]:
        receipt = self.split()
        conditions = ("B", "P") if len(members) == 2 else ("B", "H", "P")
        receipt.update(results_revealed=False, candidate_conditions={
            verify_freeze(member)["freeze_sha256"]: condition
            for member, condition in zip(members, conditions)
        })
        return receipt

    def test_public_packet_excludes_metadata_and_private_mapping(self) -> None:
        paths = self.build()
        supervisor = Path(paths["supervisor_dir"])
        packet = json.loads((supervisor / "packet.json").read_text())
        public = "\n".join(path.read_text() for path in supervisor.rglob("*") if path.is_file())
        for identity in ("Researcher0", "Researcher1", "unit-0", "unit-1", "engine-0", "engine-1", "source-candidate-0", "source-candidate-1", str(self.root), "AAB", '"previous_score"', '"authors"'):
            self.assertNotIn(identity, public)
        self.assertNotIn("mapping.json", public)
        self.assertEqual(len(packet["candidates"]), 2)
        self.assertEqual((self.round_dir / "controller").stat().st_mode & 0o777, 0o700)
        for candidate in packet["candidates"]:
            self.assertRegex(candidate["candidate_id"], r"^candidate-[a-f0-9]{24}$")
            for artifact in candidate["artifacts"]:
                self.assertRegex(artifact["artifact_id"], r"^artifact-[a-f0-9]{24}$")
                path = supervisor / artifact["file"]
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), artifact["sha256"])
        self.assertIn("Methods may remain inferable", packet["anonymity_limit"])

    def test_round_sessions_and_opaque_ids_are_fresh(self) -> None:
        first = self.build()
        second = build_blind_round(self.candidates, self.root / "second-round")
        first_packet = json.loads(Path(first["packet"]).read_text())
        second_packet = json.loads(Path(second["packet"]).read_text())
        self.assertNotEqual(first["supervisor_session_id"], second["supervisor_session_id"])
        self.assertNotEqual(first_packet["round_id"], second_packet["round_id"])
        self.assertTrue({item["candidate_id"] for item in first_packet["candidates"]}.isdisjoint({item["candidate_id"] for item in second_packet["candidates"]}))

    def test_candidate_order_uses_randomization(self) -> None:
        with patch("review.secrets.SystemRandom") as random_class:
            random_class.return_value.shuffle.side_effect = lambda items: items.reverse()
            self.build()
            random_class.return_value.shuffle.assert_called_once()
        packet = json.loads((self.round_dir / "supervisor" / "packet.json").read_text())
        mapping = json.loads((self.round_dir / "controller" / "mapping.json").read_text())
        self.assertEqual(mapping["candidates"][packet["candidates"][0]["candidate_id"]]["team_id"], "unit-1")

    def test_unknown_identity_and_score_leakage_rejected_before_output(self) -> None:
        report = self.candidates[0].workspace / "report.md"
        for suspect in ("Contact hidden@example.org", "/Users/unknown/private", "previous_score = AAA", "Made with claude-opus", "team 99", "opaque\u200bauthor"):
            with self.subTest(suspect=suspect):
                report.write_text("Finding remains unconfirmed. " + suspect)
                with self.assertRaises(ReviewError):
                    self.build()
                self.assertFalse(self.round_dir.exists())

    def test_identity_bearing_code_rejected_without_altering_original(self) -> None:
        source = self.candidates[0].workspace / "solver.py"
        source.write_text("# Author: Researcher0\nvalue = 1\n")
        with self.assertRaisesRegex(ReviewError, "identity-bearing code"):
            self.build()
        self.assertEqual(source.read_text(), "# Author: Researcher0\nvalue = 1\n")

    def test_disjoint_workspaces_and_two_team_requirement(self) -> None:
        first = self.candidates[0]
        for candidates in ([first], [first, first], [first, CandidateSpec("other", "distinct", first.workspace, first.artifacts, ("other-person",), ("other-engine",))]):
            with self.assertRaises(ReviewError):
                build_blind_round(candidates, self.round_dir)

    def test_artifact_traversal_symlink_and_binary_are_rejected(self) -> None:
        first = self.candidates[0]
        (first.workspace / "linked.md").symlink_to(first.workspace / "report.md")
        (first.workspace / "binary.pdf").write_bytes(b"%PDF-test")
        for artifact in ("../workspace-1/report.md", "linked.md", "binary.pdf"):
            with self.subTest(artifact=artifact):
                malformed = CandidateSpec(first.candidate_id, first.team_id, first.workspace, (artifact,), first.authors, first.models)
                with self.assertRaises(ReviewError):
                    build_blind_round([malformed, self.candidates[1]], self.round_dir)

    def test_hard_linked_team_artifact_is_rejected(self) -> None:
        first = self.candidates[0]
        os.link(first.workspace / "report.md", self.candidates[1].workspace / "shared.md")
        with self.assertRaisesRegex(ReviewError, "hard-linked"):
            self.build()

    def test_json_duplicate_keys_and_nonfinite_values_are_rejected(self) -> None:
        source = self.candidates[0].workspace / "reproduction.json"
        for value in ('{"status":"FAIL","status":"PASS"}', '{"cost":NaN}'):
            source.write_text(value)
            with self.subTest(value=value), self.assertRaises(ReviewError):
                self.build()

    def test_scientific_model_configuration_survives_identity_redaction(self) -> None:
        source = self.candidates[0].workspace / "reproduction.json"
        receipt = json.loads(source.read_text())
        receipt["scientific_configuration"] = {"model": "HistGradientBoostingRegressor", "max_iter": 100}
        source.write_text(json.dumps(receipt))
        paths = self.build()
        copies = [json.loads(path.read_text()) for path in Path(paths["supervisor_dir"]).rglob("*.json") if path.name != "packet.json"]
        retained = [item["scientific_configuration"] for item in copies if "scientific_configuration" in item]
        self.assertEqual(retained, [{"model": "HistGradientBoostingRegressor", "max_iter": 100}])

    def test_fixtures_never_receive_research_aaa_superiority_or_pi_acceptance(self) -> None:
        assessment, supervisor = self.fixture_assessment()
        result = assess(assessment, supervisor)
        self.assertEqual(result["quality"], "APPARATUS_PASS")
        self.assertEqual(result["superiority"], "NOT_ASSESSED")
        self.assertEqual(result["pi_acceptance"], "PENDING")

    def test_critical_and_major_findings_block_all_dimension_pass(self) -> None:
        assessment, supervisor = self.fixture_assessment()
        for severity in ("Critical", "Major"):
            assessment["findings"] = [self.finding(assessment, severity)]
            result = assess(assessment, supervisor)
            self.assertEqual(result["quality"], "NOT_AAA")
            self.assertEqual(result["unresolved_critical_major"], ["finding-residual"])
        assessment["findings"] = [self.finding(assessment, "Style")]
        self.assertEqual(assess(assessment, supervisor)["quality"], "APPARATUS_PASS")

    def test_findings_require_evidence_impact_minimum_fix_and_recheck(self) -> None:
        assessment, supervisor = self.fixture_assessment()
        for missing in ("evidence", "impact", "minimum_fix", "recheck"):
            finding = self.finding(assessment)
            del finding[missing]
            assessment["findings"] = [finding]
            with self.subTest(missing=missing), self.assertRaises(ReviewError):
                assess(assessment, supervisor)

    def test_rebuttal_needs_current_reviewer_and_recheck_evidence(self) -> None:
        assessment, supervisor = self.fixture_assessment()
        finding = self.finding(assessment)
        finding["resolution"] = {"status": "REBUTTAL_ACCEPTED", "justification": "Independent evidence resolves the alleged error.", "reviewed_by_session_id": assessment["supervisor_session_id"], "evidence": finding["evidence"], "recheck_evidence": finding["evidence"]}
        assessment["findings"] = [finding]
        self.assertEqual(assess(assessment, supervisor)["quality"], "APPARATUS_PASS")
        finding["resolution"]["reviewed_by_session_id"] = "previous-supervisor"
        with self.assertRaisesRegex(ReviewError, "fresh supervisor"):
            assess(assessment, supervisor)
        finding["resolution"]["reviewed_by_session_id"] = assessment["supervisor_session_id"]
        del finding["resolution"]["recheck_evidence"]
        with self.assertRaises(ReviewError):
            assess(assessment, supervisor)

    def test_dimensions_cannot_be_missing_or_unconfirmed_for_pass(self) -> None:
        assessment, supervisor = self.fixture_assessment()
        assessment["dimensions"]["claim_scope"]["status"] = "UNCONFIRMED"
        self.assertEqual(assess(assessment, supervisor)["failed_dimensions"], ["claim_scope"])
        del assessment["dimensions"]["claim_scope"]
        with self.assertRaisesRegex(ReviewError, "all six"):
            assess(assessment, supervisor)

    def test_evidence_requires_current_hash_and_real_line_locator(self) -> None:
        assessment, supervisor = self.fixture_assessment()
        reference = assessment["dimensions"]["correctness"]["evidence"][0]
        old_hash = reference["sha256"]
        reference["sha256"] = digest("unrelated")
        with self.assertRaisesRegex(ReviewError, "current candidate artifact hash"):
            assess(assessment, supervisor)
        reference["sha256"] = old_hash
        for locator in ("L999999", "L5-L1", "report somewhere", "L0"):
            reference["locator"] = locator
            with self.assertRaises(ReviewError):
                assess(assessment, supervisor)

    def test_previous_session_and_score_carryover_rejected(self) -> None:
        assessment, supervisor = self.fixture_assessment()
        original = assessment["supervisor_session_id"]
        assessment["supervisor_session_id"] = "previous-session"
        with self.assertRaisesRegex(ReviewError, "fresh round"):
            assess(assessment, supervisor)
        assessment["supervisor_session_id"] = original
        assessment["session_attestation"]["previous_scores_received"] = True
        with self.assertRaisesRegex(ReviewError, "previous scores"):
            assess(assessment, supervisor)

    def test_extra_history_file_is_rejected_from_supervisor_input(self) -> None:
        assessment, supervisor = self.fixture_assessment()
        (supervisor / "previous-assessment.json").write_text('{"quality":"AAA"}')
        with self.assertRaisesRegex(ReviewError, "unexpected or missing"):
            assess(assessment, supervisor)

    def test_apparatus_reproduction_cannot_be_promoted_to_research(self) -> None:
        for candidate in self.candidates:
            path = candidate.workspace / "reproduction.json"
            receipt = json.loads(path.read_text())
            receipt["evidence_scope"] = "development_research"
            path.write_text(json.dumps(receipt))
        assessment, supervisor = self.fixture_assessment()
        with self.assertRaisesRegex(ReviewError, "reproduction scopes cannot be mixed"):
            assess(assessment, supervisor)

    def test_independent_execution_receipt_is_required(self) -> None:
        assessment, supervisor = self.fixture_assessment()
        assessment["independent_reproduction_evidence"] = assessment["dimensions"]["correctness"]["evidence"]
        with self.assertRaisesRegex(ReviewError, "execution receipt is absent"):
            assess(assessment, supervisor)

    def test_same_producer_session_cannot_supply_independent_reproduction(self) -> None:
        path = self.candidates[0].workspace / "reproduction.json"
        receipt = json.loads(path.read_text())
        receipt["reproducer_session_id"] = receipt["producer_session_ids"][0]
        for candidate in self.candidates:
            (candidate.workspace / "reproduction.json").write_text(json.dumps(receipt))
        assessment, supervisor = self.fixture_assessment()
        with self.assertRaisesRegex(ReviewError, "independent successful"):
            assess(assessment, supervisor)

    def test_public_artifact_change_is_detected(self) -> None:
        assessment, supervisor = self.fixture_assessment()
        report = next(supervisor.rglob("*.md"))
        report.chmod(0o600)
        report.write_text("Changed after packet construction")
        with self.assertRaisesRegex(ReviewError, "artifact changed"):
            assess(assessment, supervisor)

    def test_freeze_rejects_source_change_after_review(self) -> None:
        assessment, _ = self.fixture_assessment()
        for candidate in self.candidates:
            (candidate.workspace / "solver.py").write_text("Changed since review\n")
        with self.assertRaisesRegex(ReviewError, "changed after blind review"):
            freeze_candidate(self.round_dir, assessment, self.root / "frozen")
        self.assertFalse((self.root / "frozen").exists())

    def test_freeze_rejects_packet_change_and_second_candidate_selection(self) -> None:
        assessment, _ = self.fixture_assessment()
        destination = self.root / "frozen"
        freeze_candidate(self.round_dir, assessment, destination)
        with self.assertRaisesRegex(ReviewError, "already frozen"):
            freeze_candidate(self.round_dir, assessment, self.root / "second-freeze")
        packet = self.round_dir / "supervisor" / "packet.json"
        packet.chmod(0o600)
        packet.write_text(packet.read_text() + " ")
        with self.assertRaisesRegex(ReviewError, "packet changed"):
            freeze_candidate(self.round_dir, assessment, self.root / "third-freeze")

    def test_freeze_detects_modified_and_added_artifacts(self) -> None:
        destination = self.frozen_fixture()
        verify_freeze(destination)
        extra = destination / "artifacts" / "extra.py"
        extra.write_text("Unreviewed code")
        with self.assertRaisesRegex(ReviewError, "file set changed"):
            verify_freeze(destination)
        extra.unlink()
        source = destination / "artifacts" / "solver.py"
        source.chmod(0o600)
        source.write_text("Modified frozen candidate")
        with self.assertRaisesRegex(ReviewError, "artifact changed"):
            verify_freeze(destination)

    def test_final_reservation_is_one_use_and_does_not_claim_execution(self) -> None:
        destination = self.frozen_fixture()
        registry = self.root / "private-registry"
        result = reserve_final_evaluation(destination, self.split(), registry)
        self.assertEqual(result["status"], "APPARATUS_RESERVATION")
        self.assertFalse(result["execution_started"])
        self.assertEqual(result["pi_acceptance"], "PENDING")
        with self.assertRaisesRegex(ReviewError, "already consumed"):
            reserve_final_evaluation(destination, self.split(), registry)
        changed_split = self.split()
        changed_split["split_id"] = "another-held-out-fixture"
        changed_split["split_sha256"] = digest("different final fixture")
        with self.assertRaisesRegex(ReviewError, "already consumed"):
            reserve_final_evaluation(destination, changed_split, registry)
        with sqlite3.connect(registry / "final-evaluations.sqlite3") as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM reservations").fetchone()[0], 1)

    def test_final_split_cannot_be_reused_for_a_revised_candidate(self) -> None:
        first = self.frozen_fixture()
        registry = self.root / "private-registry"
        reserve_final_evaluation(first, self.split(), registry)
        self.round_dir = self.root / "revised-round"
        assessment, _ = self.fixture_assessment()
        second = self.root / "revised-freeze"
        freeze_candidate(self.round_dir, assessment, second)
        with self.assertRaisesRegex(ReviewError, "already consumed"):
            reserve_final_evaluation(second, self.split(), registry)
        disguised = self.split()
        disguised["split_id"] = "renamed-same-data"
        with self.assertRaisesRegex(ReviewError, "already consumed"):
            reserve_final_evaluation(second, disguised, registry)

    def test_final_split_custody_independence_and_scope_are_mandatory(self) -> None:
        destination = self.frozen_fixture()
        for field, value in (("worker_access", True), ("independent_from_development", False), ("purpose", "development"), ("custody_evidence", []), ("independence_evidence", []), ("evidence_scope", "development_research"), ("split_sha256", digest("development fixture")), ("evaluator_id", "unit-0")):
            malformed = self.split()
            malformed[field] = value
            with self.subTest(field=field), self.assertRaises(ReviewError):
                reserve_final_evaluation(destination, malformed, self.root / "registry")
        self.assertFalse((self.root / "registry").exists())

    def test_comparison_registers_all_three_frozen_conditions_on_one_split(self) -> None:
        members = self.frozen_members(3)
        registry = self.root / "registry"
        reservation = reserve_comparison_batch(members, self.comparison_split(members), registry)
        self.assertEqual(reservation["status"], "APPARATUS_COMPARISON_RESERVATION")
        self.assertEqual([member["condition"] for member in reservation["members"]], ["B", "H", "P"])
        self.assertTrue(reservation["membership_frozen"])
        self.assertFalse(reservation["execution_started"])
        self.assertFalse(reservation["results_revealed"])
        self.assertEqual(reservation["pi_acceptance"], "PENDING")
        with sqlite3.connect(registry / "final-evaluations.sqlite3") as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM comparison_batches").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM comparison_members").fetchone()[0], 3)
            stored = json.loads(connection.execute("SELECT receipt_json FROM comparison_batches").fetchone()[0])
        self.assertEqual(stored["reservation"]["members"], reservation["members"])

    def test_comparison_does_not_admit_late_or_revised_members(self) -> None:
        members = self.frozen_members(3)
        registry = self.root / "registry"
        reserve_comparison_batch(members[:2], self.comparison_split(members[:2]), registry)
        with self.assertRaisesRegex(ReviewError, "already consumed"):
            reserve_comparison_batch(members, self.comparison_split(members), registry)
        with self.assertRaisesRegex(ReviewError, "already consumed"):
            reserve_final_evaluation(members[2], self.split(), registry)
        with sqlite3.connect(registry / "final-evaluations.sqlite3") as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM comparison_members").fetchone()[0], 2)

    def test_prior_single_use_blocks_comparison_on_the_same_data(self) -> None:
        members = self.frozen_members(3)
        registry = self.root / "registry"
        reserve_final_evaluation(members[0], self.split(), registry)
        split = self.comparison_split(members[1:])
        split["split_id"] = "renamed-same-final-data"
        with self.assertRaisesRegex(ReviewError, "already consumed"):
            reserve_comparison_batch(members[1:], split, registry)
        with sqlite3.connect(registry / "final-evaluations.sqlite3") as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM comparison_batches").fetchone()[0], 0)

    def test_batch_candidate_cannot_reenter_a_single_evaluation(self) -> None:
        members = self.frozen_members(2)
        registry = self.root / "registry"
        reserve_comparison_batch(members, self.comparison_split(members), registry)
        fresh_split = self.split()
        fresh_split.update(split_id="fresh-data", split_sha256=digest("fresh final fixture"))
        with self.assertRaisesRegex(ReviewError, "candidate was already consumed"):
            reserve_final_evaluation(members[0], fresh_split, registry)

    def test_failed_batch_is_atomic_and_does_not_consume_available_members(self) -> None:
        members = self.frozen_members(3)
        registry = self.root / "registry"
        prior_split = self.split()
        prior_split.update(split_id="prior-final", split_sha256=digest("prior final fixture"))
        reserve_final_evaluation(members[0], prior_split, registry)
        with self.assertRaisesRegex(ReviewError, "candidate was already consumed"):
            reserve_comparison_batch([members[1], members[0]], self.comparison_split([members[1], members[0]]), registry)
        with sqlite3.connect(registry / "final-evaluations.sqlite3") as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM comparison_members").fetchone()[0], 0)
        accepted = reserve_comparison_batch(members[1:], self.comparison_split(members[1:]), registry)
        self.assertEqual(len(accepted["members"]), 2)

    def test_comparison_requires_unrevealed_complete_distinct_membership(self) -> None:
        members = self.frozen_members(2)
        malformed_conditions = {verify_freeze(members[0])["freeze_sha256"]: ["B"], verify_freeze(members[1])["freeze_sha256"]: "P"}
        for field, value in (("results_revealed", True), ("results_revealed", None), ("candidate_conditions", {}), ("candidate_conditions", malformed_conditions)):
            split = self.comparison_split(members)
            split[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ReviewError):
                reserve_comparison_batch(members, split, self.root / "registry")
        with self.assertRaisesRegex(ReviewError, "distinct"):
            reserve_comparison_batch([members[0], members[0]], self.comparison_split(members), self.root / "registry")
        self.assertFalse((self.root / "registry").exists())

    def test_concurrent_single_and_batch_cannot_both_consume_a_split(self) -> None:
        members = self.frozen_members(3)
        registry = self.root / "registry"

        def single():
            try:
                return reserve_final_evaluation(members[0], self.split(), registry)
            except ReviewError:
                return None

        def batch():
            try:
                return reserve_comparison_batch(members[1:], self.comparison_split(members[1:]), registry)
            except ReviewError:
                return None

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(single), executor.submit(batch)]
            outcomes = [future.result() for future in futures]
        self.assertEqual(sum(outcome is not None for outcome in outcomes), 1)
        with sqlite3.connect(registry / "final-evaluations.sqlite3") as connection:
            singles = connection.execute("SELECT COUNT(*) FROM reservations").fetchone()[0]
            batches = connection.execute("SELECT COUNT(*) FROM comparison_batches").fetchone()[0]
            self.assertEqual(singles + batches, 1)

    def test_controller_data_must_be_outside_worker_paths(self) -> None:
        with self.assertRaisesRegex(ReviewError, "outside all producer"):
            build_blind_round(self.candidates, self.candidates[0].workspace / "leaky-round")
        destination = self.frozen_fixture()
        with self.assertRaisesRegex(ReviewError, "external to producer"):
            reserve_final_evaluation(destination, self.split(), self.candidates[1].workspace / "leaky-registry")

    def test_cli_malformed_json_returns_rejected(self) -> None:
        invalid = self.root / "bad.json"
        invalid.write_text("{")
        with patch("sys.stderr"):
            self.assertEqual(main(["blind", str(invalid), str(self.round_dir)]), 2)


if __name__ == "__main__":
    unittest.main()
