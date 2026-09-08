from __future__ import annotations

from dataclasses import asdict, replace
import json
import os
from pathlib import Path
import tempfile
from types import MethodType
import unittest
from unittest.mock import patch

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime import final_assessment as assessment
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime import bridge as bridge_module
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime import grading as grading_module
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime import phase_completion as completion
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.bridge import (
    Binding, FixedNativePort, NativeObservation,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import (
    FileBinding, grade_files,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_gate import decide_phase
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion import (
    CompletionFixture, binding, binding_dict, digest, directory,
)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


class SyntheticPort(FixedNativePort):
    def __init__(self, predictions: FileBinding, ids: FileBinding, final: Binding):
        self.predictions = predictions
        self.final = final
        self.config = type("PortConfig", (), {"final_inputs": {"ids": ids}, "final_rows": 292})()
        self.status = "DONE"

    def observe(self, value: Binding) -> NativeObservation:
        if value != self.final:
            raise ValueError("unexpected binding")
        return NativeObservation(value.run_id, value.experiment_id, value.native_commit,
                                 value.native_source_digest, 100, self.status, False)

    def final_artifact_binding(self, value: Binding, observation: NativeObservation) -> FileBinding:
        if value != self.final or observation.status != "DONE":
            raise ValueError("unexpected observation")
        return self.predictions


class AssessmentFixture:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.phase = CompletionFixture(self.root, context="continuation")
        self.data = self.root / "private-data"
        self.data.mkdir(mode=0o700)
        ids = [str(9000 + index) for index in range(292)]
        # Synthetic prices only. Absolute error is exactly 333333/1000000.
        predictions = "Id,SalePrice\n" + "".join(value + ",10\n" for value in ids)
        targets = "Id,SalePrice\n" + "".join(value + ",10.333333\n" for value in ids)
        self.prediction_path = self.data / "predictions.csv"
        self.id_path = self.data / "ids.json"
        self.target_path = self.data / "targets.csv"
        self.prediction_path.write_text(predictions)
        self.id_path.write_bytes(canonical(ids))
        self.target_path.write_text(targets)
        self.predictions = binding(self.prediction_path)
        self.ids = binding(self.id_path)
        self.targets = binding(self.target_path)
        task = {
            "schema_version": "argo-house-price-fixed-task/v1", "task_id": "mlagentbench-house-price",
            "counts": {"hidden": 292},
            "phase_input_files": {"trusted_final_assessment": {
                "ids": {"sha256": self.ids.sha256, "bytes": self.ids.bytes},
                "targets": {"sha256": self.targets.sha256, "bytes": self.targets.bytes}}},
        }
        self.task_path = self.root / "task.json"
        self.task_path.write_bytes(canonical(task))
        self.task = binding(self.task_path)
        self.phase.lock = replace(self.phase.lock, artifact_sha256=self.predictions.sha256,
                                  task_sha256=self.task.sha256)
        self.phase.bridge.config.task_sha256 = self.task.sha256
        self.phase.bridge.config.trusted_io.lock = self.phase.lock
        self.phase.public["result"]["runs"][-1]["artifact_sha256"] = self.predictions.sha256
        self.lock_path = self.phase.paths["bridge-state"] / "final-artifact-lock.json"
        self.lock_path.write_bytes(canonical(asdict(self.phase.lock)))
        outcome = json.loads(self.phase.outcome_path.read_bytes())
        outcome["view_sha256"]["public"] = digest(canonical(self.phase.public))
        outcome["final_lock_sha256"] = digest(self.lock_path.read_bytes())
        observation = completion._usage_observation(outcome["usage"])
        decision = decide_phase("continuation", self.phase.public, self.phase.dev,
                                self.phase.research, observation, self.phase.lock, 292)
        outcome["decision"] = asdict(decision)
        self.phase.outcome_path.write_bytes(canonical(outcome))
        self.final = Binding(
            "argo-house-price-native-binding/v1", 4, digest("final-intent"),
            self.phase.lock.closure_sha256, self.phase.lock.code_sha256, "final_refit",
            self.phase.final_id, self.phase.public["result"]["runs"][-1]["experiment_id"],
            "synthetic-final", "orx/synthetic-final", "a" * 40, digest("native-source"),
            self.phase.lock.execution_config_sha256, self.task.sha256,
            self.phase.lock.environment_sha256, self.phase.lock.protocol_sha256,
        )
        self.port = SyntheticPort(self.predictions, self.ids, self.final)
        self.phase.bridge.port = self.port
        self.phase.bridge._state = lambda: ([], [self.final])
        self.output = self.root / "trusted-final-assessment"
        self.output.mkdir(mode=0o700)
        published = self.phase.run()
        if published.disposition != "FINAL_COMPLETION_PUBLISHED":
            raise AssertionError("completion fixture did not publish: " + str(published))
        self.config = assessment.FinalAssessmentConfig(
            self.phase.config, published.publication, self.task, self.ids, self.targets, directory(self.output),
        )

    def run(self) -> assessment.FinalAssessmentResult:
        with patch.object(completion, "load_bridge_from_config", return_value=self.phase.bridge):
            return assessment.assess_final(self.config)


class FinalAssessmentTest(unittest.TestCase):
    def test_exact_mae_from_bound_artifact_after_complete_programme(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            result = fixture.run()
            self.assertEqual((result.disposition, result.reason), ("CANDIDATE_READY", "VERIFIED"))
            value = json.loads(result.publication.path.read_bytes())
            self.assertEqual(value["metric"], {"name": "original-unit MAE", "numerator": "333333", "denominator": "1000000", "rows": 292})
            self.assertEqual(value["final_completion"], binding_dict(fixture.config.final_completion))
            self.assertEqual(value["predictions"], binding_dict(fixture.predictions))
            self.assertEqual(sorted(p.name for p in fixture.output.iterdir()),
                             ["assessment-admission.json", "hidden-assessment-candidate.json"])
            self.assertNotIn("9000", result.publication.path.read_text())
            self.assertNotIn("10.333333", result.publication.path.read_text())

    def test_original_nonzero_or_noninteger_process_terminal_blocks_hidden_read(self):
        for code in (1, False, 0.0, None):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as temporary:
                fixture = AssessmentFixture(Path(temporary))
                path = fixture.phase.process_receipt_path
                value = json.loads(path.read_bytes()); value["returncode"] = code
                path.write_bytes(canonical(value))
                with patch.object(assessment, "grade_files", wraps=grade_files) as grader:
                    result = fixture.run()
                self.assertEqual(result.disposition, "NOT_ADMITTED")
                grader.assert_not_called()
                self.assertEqual(list(fixture.output.iterdir()), [])

    def test_completion_claim_rebinding_does_not_replace_original_rederivation(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            path = fixture.config.final_completion.path
            value = json.loads(path.read_bytes()); value["campaign_used_tokens"] = 0
            path.write_bytes(canonical(value))
            fixture.config = replace(fixture.config, final_completion=binding(path))
            result = fixture.run()
            self.assertEqual(result.disposition, "NOT_ADMITTED")
            self.assertEqual(list(fixture.output.iterdir()), [])

    def test_task_target_substitution_blocks_before_grading(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            path = fixture.data / "different-targets.csv"
            path.write_text("Id,SalePrice\n9000,1\n")
            fixture.config = replace(fixture.config, hidden_targets=binding(path))
            with patch.object(assessment, "grade_files", wraps=grade_files) as grader:
                result = fixture.run()
            self.assertEqual(result.disposition, "NOT_ADMITTED")
            grader.assert_not_called()

    def test_native_unknown_and_wrong_prediction_digest_block_before_grading(self):
        for mode in ("unknown", "artifact"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                fixture = AssessmentFixture(Path(temporary))
                if mode == "unknown":
                    fixture.port.status = "UNKNOWN"
                else:
                    path = fixture.data / "wrong.csv"; path.write_text("Id,SalePrice\n9000,11\n")
                    fixture.port.predictions = binding(path)
                with patch.object(assessment, "grade_files", wraps=grade_files) as grader:
                    result = fixture.run()
                self.assertEqual(result.disposition, "NOT_ADMITTED")
                grader.assert_not_called()

    def test_pending_or_completed_assessment_never_rescores(self):
        for mode in ("pending", "completed"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                fixture = AssessmentFixture(Path(temporary))
                if mode == "pending":
                    (fixture.output / "assessment-admission.json").write_bytes(b"{")
                else:
                    self.assertEqual(fixture.run().disposition, "CANDIDATE_READY")
                before = {p.name: p.read_bytes() for p in fixture.output.iterdir()}
                with patch.object(assessment, "grade_files", wraps=grade_files) as grader:
                    result = fixture.run()
                self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "ALREADY_ATTEMPTED"))
                grader.assert_not_called()
                self.assertEqual({p.name: p.read_bytes() for p in fixture.output.iterdir()}, before)

    def test_fixed_assessment_location_prevents_new_destination_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            other = fixture.root / "other"; other.mkdir(mode=0o700)
            fixture.config = replace(fixture.config, output_directory=directory(other))
            result = fixture.run()
            self.assertEqual(result.disposition, "NOT_ADMITTED")
            self.assertEqual(list(other.iterdir()), [])

    def test_hidden_data_same_size_mutation_after_admission_is_unknown_not_score(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            def mutate(*args, **kwargs):
                value = grade_files(*args, **kwargs)
                info = fixture.target_path.stat()
                data = fixture.target_path.read_bytes().replace(b"10.333333", b"20.333333", 1)
                fixture.target_path.write_bytes(data)
                os.utime(fixture.target_path, ns=(info.st_atime_ns, info.st_mtime_ns))
                return value
            with patch.object(assessment, "grade_files", side_effect=mutate):
                result = fixture.run()
            self.assertEqual(result.disposition, "UNKNOWN")
            self.assertIsNone(result.publication)
            self.assertTrue((fixture.output / "assessment-admission.json").exists())
            self.assertFalse((fixture.output / "hidden-assessment-candidate.json").exists())

    def test_late_process_evidence_mutation_suppresses_score_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            def mutate(*args, **kwargs):
                value = grade_files(*args, **kwargs)
                fixture.phase.process_receipt_path.write_bytes(b"{}")
                return value
            with patch.object(assessment, "grade_files", side_effect=mutate):
                result = fixture.run()
            self.assertEqual(result.disposition, "UNKNOWN")
            self.assertIsNone(result.publication)

    def test_symlink_reference_and_invalid_config_cannot_return_score(self):
        result = assessment.assess_final("wrong-config")
        self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "INVALID_INPUT"))
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            target = fixture.target_path.with_suffix(".original")
            fixture.target_path.rename(target); fixture.target_path.symlink_to(target)
            result = fixture.run()
            self.assertNotEqual(result.disposition, "CANDIDATE_READY")
            self.assertIsNone(result.publication)

    def test_base_exception_is_not_caught_and_fence_remains_consumed(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            with patch.object(assessment, "grade_files", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    fixture.run()
            self.assertTrue((fixture.output / "assessment-admission.json").exists())
            self.assertFalse((fixture.output / "hidden-assessment-candidate.json").exists())


    def test_short_publication_preserves_partial_fence_and_blocks_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            real_write = os.write
            calls = 0
            def interrupted(descriptor, payload):
                nonlocal calls
                calls += 1
                if calls == 1:
                    return real_write(descriptor, payload[:1])
                raise OSError("synthetic short write")
            with patch.object(assessment.os, "write", side_effect=interrupted):
                result = fixture.run()
            self.assertEqual(result.disposition, "UNKNOWN")
            self.assertIsNone(result.publication)
            self.assertEqual((fixture.output / "assessment-admission.json").read_bytes(), b"{")
            self.assertEqual(fixture.run().reason, "ALREADY_ATTEMPTED")

    def test_post_publication_evidence_mutation_cannot_leave_successful_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            real_publish = assessment._publish
            def mutate(descriptor, identity, name, data):
                value = real_publish(descriptor, identity, name, data)
                if name == "hidden-assessment-candidate.json":
                    fixture.phase.process_receipt_path.write_bytes(b"{}")
                return value
            with patch.object(assessment, "_publish", side_effect=mutate):
                result = fixture.run()
            self.assertEqual(result.disposition, "UNKNOWN")
            self.assertIsNone(result.publication)
            self.assertTrue((fixture.output / "hidden-assessment-candidate.json").exists())
            # A file with score fields is not acceptance without the original terminal/result.
            self.assertTrue((fixture.output / "assessment-admission.json").exists())

    def test_directory_replacement_after_grading_prevents_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            def replace_directory(*args, **kwargs):
                value = grade_files(*args, **kwargs)
                fixture.output.rename(fixture.output.with_name("held-output"))
                fixture.output.mkdir(mode=0o700)
                return value
            with patch.object(assessment, "grade_files", side_effect=replace_directory):
                result = fixture.run()
            self.assertEqual(result.disposition, "UNKNOWN")
            self.assertFalse((fixture.output / "hidden-assessment-candidate.json").exists())
            self.assertTrue((fixture.root / "held-output" / "assessment-admission.json").exists())

    def test_explicit_rebound_invalid_terminal_and_missing_usage_do_not_publish(self):
        for mode in ("false", "nonzero", "usage"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                fixture = AssessmentFixture(Path(temporary))
                if mode == "usage":
                    value = [json.loads(line) for line in fixture.phase.session_path.read_text().splitlines()]
                    del value[1]["message"]["responseId"]
                    fixture.phase.session_path.write_bytes(b"\n".join(canonical(item) for item in value) + b"\n")
                    phase = replace(fixture.config.phase, current_session=binding(fixture.phase.session_path))
                else:
                    path = fixture.phase.process_receipt_path
                    value = json.loads(path.read_bytes()); value["returncode"] = False if mode == "false" else 1
                    path.write_bytes(canonical(value))
                    phase = replace(fixture.config.phase, process_receipt=binding(path))
                fixture.config = replace(fixture.config, phase=phase)
                with patch.object(assessment, "grade_files", wraps=grade_files) as grader:
                    result = fixture.run()
                self.assertEqual(result.disposition, "NOT_ADMITTED")
                grader.assert_not_called()

    def test_scorer_reports_fewer_rows_than_fixed_task_is_not_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            def wrong_rows(*args, **kwargs):
                return replace(grade_files(*args, **kwargs), row_count=291)
            with patch.object(assessment, "grade_files", side_effect=wrong_rows):
                result = fixture.run()
            self.assertEqual(result.disposition, "UNKNOWN")
            self.assertIsNone(result.publication)


    def test_production_id_validation_is_prefence_but_hidden_target_read_is_postfence(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            events = []
            real_read = grading_module.read_bound
            real_publish = assessment._publish
            def runner_receipt(self, value, observation, require_success):
                return {"metric": None, "rows": 292}, self.predictions
            fixture.port._runner_receipt = MethodType(runner_receipt, fixture.port)
            fixture.port.final_artifact_binding = MethodType(FixedNativePort.final_artifact_binding, fixture.port)
            def observe_read(value, cap):
                if value == fixture.ids:
                    events.append("ids")
                elif value == fixture.targets:
                    events.append("targets")
                return real_read(value, cap)
            def observe_publish(descriptor, identity, name, data):
                value = real_publish(descriptor, identity, name, data)
                if name == "assessment-admission.json":
                    events.append("admission")
                return value
            with patch.object(bridge_module, "read_bound", side_effect=observe_read), patch.object(
                    grading_module, "read_bound", side_effect=observe_read), patch.object(
                    assessment, "_publish", side_effect=observe_publish):
                result = fixture.run()
            self.assertEqual(result.disposition, "CANDIDATE_READY")
            self.assertLess(events.index("ids"), events.index("admission"))
            self.assertLess(events.index("admission"), events.index("targets"))

    def test_candidate_is_explicitly_unaccepted_even_after_successful_grading(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AssessmentFixture(Path(temporary))
            result = fixture.run()
            self.assertEqual(result.disposition, "CANDIDATE_READY")
            self.assertEqual(result.publication.path.name, "hidden-assessment-candidate.json")
            self.assertEqual(json.loads(result.publication.path.read_bytes())["status"], "CANDIDATE_UNACCEPTED")
            self.assertFalse((fixture.output / "assessment-acceptance.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
