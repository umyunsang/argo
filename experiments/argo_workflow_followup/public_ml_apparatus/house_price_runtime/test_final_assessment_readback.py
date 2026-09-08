from __future__ import annotations

from dataclasses import replace
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime import final_assessment as assessment
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime import final_assessment_readback as readback
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime import phase_completion as completion
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_final_assessment import (
    AssessmentFixture, canonical,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion import binding, binding_dict


def config_value(config):
    phase = config.phase
    return {
        "phase": {"context": phase.context, "initial_context_id": phase.initial_context_id,
            "controller_context_id": phase.controller_context_id, "next_context_id": phase.next_context_id,
            "gate_config": binding_dict(phase.gate_config), "process_config": binding_dict(phase.process_config),
            "process_receipt": binding_dict(phase.process_receipt), "current_session": binding_dict(phase.current_session),
            "current_session_id": phase.current_session_id,
            "completion_directory": {"path": str(phase.completion_directory.path),
                "device": phase.completion_directory.device, "inode": phase.completion_directory.inode}},
        **{name: binding_dict(getattr(config, name)) for name in
           ("final_completion", "task_manifest", "hidden_ids", "hidden_targets")},
        "output_directory": {"path": str(config.output_directory.path),
            "device": config.output_directory.device, "inode": config.output_directory.inode},
    }


class ReadbackFixture:
    def __init__(self, root):
        self.assessment = AssessmentFixture(root)
        self.config = self.assessment.config
        self.capture_dir = root / "original-outer"
        self.capture_dir.mkdir(mode=0o700)
        self.out = self.capture_dir / "stdout.log"
        self.err = self.capture_dir / "stderr.log"
        self.out.write_bytes(b""); self.err.write_bytes(b"")
        def capture(path):
            info = path.stat()
            return {"path": str(path), "device": info.st_dev, "inode": info.st_ino}
        self.launch_path = self.capture_dir / "launch.json"
        self.launch_path.write_bytes(canonical({
            "schema_version": "argo-house-price-assessment-outer-admission/v1",
            "config": config_value(self.config),
            "stdout": capture(self.out), "stderr": capture(self.err),
        }))
        self.launch = binding(self.launch_path)
        self.result = self.assessment.run()
        if self.result.disposition != "CANDIDATE_READY":
            raise AssertionError("invalid synthetic scorer setup")
        self.result_value = {"disposition": self.result.disposition, "reason": self.result.reason,
            "admission": binding_dict(self.result.admission), "publication": binding_dict(self.result.publication)}
        self.out.write_bytes(canonical(self.result_value) + b"\n")
        self.stdout, self.stderr = binding(self.out), binding(self.err)
        self.pid = 111111
        self.terminal_path = self.capture_dir / "terminal.json"
        self.terminal_value = {"schema_version": "argo-house-price-assessment-outer-terminal/v1",
            "launch": binding_dict(self.launch), "pid": self.pid, "returncode": 0,
            "terminal_complete": True, "stdout": binding_dict(self.stdout), "stderr": binding_dict(self.stderr)}
        self.terminal_path.write_bytes(canonical(self.terminal_value))
        self.terminal = binding(self.terminal_path)
        self.args = dict(launch=self.launch, terminal=self.terminal, stdout=self.stdout, stderr=self.stderr,
                         pid=self.pid, returncode=0, terminal_complete=True)

    def run(self, **overrides):
        with patch.object(completion, "load_bridge_from_config", return_value=self.assessment.phase.bridge):
            return readback.accept_assessment(self.config, **{**self.args, **overrides})


class AssessmentReadbackTest(unittest.TestCase):
    def test_original_success_result_publishes_acceptance_without_regrading(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = ReadbackFixture(Path(temporary).resolve())
            with patch.object(assessment, "grade_files", side_effect=AssertionError("must not regrade")):
                result = fixture.run()
            self.assertEqual((result.status, result.reason), ("PASS", "VERIFIED"))
            self.assertEqual(result.candidate, fixture.result.publication)
            value = json.loads(result.acceptance.path.read_bytes())
            self.assertEqual(value["candidate"], binding_dict(result.candidate))
            self.assertEqual(value["terminal"], binding_dict(fixture.terminal))
            self.assertNotIn("metric", value)
            self.assertEqual(json.loads(fixture.result.publication.path.read_bytes())["status"], "CANDIDATE_UNACCEPTED")

    def test_missing_unknown_nonzero_or_malformed_outer_exit_cannot_accept(self):
        for overrides, status in [({"terminal_complete": False}, "UNKNOWN"),
                                  ({"returncode": None}, "UNKNOWN"),
                                  ({"returncode": 1}, "NOT_ADMITTED"),
                                  ({"returncode": False}, "NOT_ADMITTED"),
                                  ({"returncode": 0.0}, "NOT_ADMITTED")]:
            with self.subTest(overrides=overrides), tempfile.TemporaryDirectory() as temporary:
                fixture = ReadbackFixture(Path(temporary).resolve())
                result = fixture.run(**overrides)
                self.assertEqual(result.status, status)
                self.assertIsNone(result.acceptance)
                self.assertFalse((fixture.assessment.output / "assessment-acceptance.json").exists())

    def test_missing_bound_terminal_is_unknown_even_with_true_boolean(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = ReadbackFixture(Path(temporary).resolve())
            fixture.terminal_path.unlink()
            result = fixture.run()
            self.assertEqual((result.status, result.reason), ("UNKNOWN", "TERMINAL_INCOMPLETE"))

    def test_mutated_capture_or_terminal_and_wrong_pid_cannot_accept(self):
        for mode in ("stdout", "terminal", "pid", "replaced"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                fixture = ReadbackFixture(Path(temporary).resolve())
                if mode == "stdout":
                    fixture.out.write_bytes(b"{}\n")
                elif mode == "terminal":
                    fixture.terminal_path.write_bytes(b"{}")
                elif mode == "replaced":
                    payload = fixture.out.read_bytes()
                    fixture.out.rename(fixture.out.with_suffix(".held"))
                    fixture.out.write_bytes(payload)
                    fixture.args["stdout"] = binding(fixture.out)
                    fixture.terminal_value["stdout"] = binding_dict(fixture.args["stdout"])
                    fixture.terminal_path.write_bytes(canonical(fixture.terminal_value))
                    fixture.args["terminal"] = binding(fixture.terminal_path)
                result = fixture.run(**({"pid": 222222} if mode == "pid" else {}))
                self.assertEqual(result.status, "NOT_ADMITTED")

    def test_candidate_file_cannot_override_unknown_returned_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = ReadbackFixture(Path(temporary).resolve())
            fixture.result_value.update(disposition="UNKNOWN", reason="ASSESSMENT_INCOMPLETE", publication=None)
            fixture.out.write_bytes(canonical(fixture.result_value)+b"\n")
            fixture.args["stdout"] = binding(fixture.out)
            fixture.terminal_value["stdout"] = binding_dict(fixture.args["stdout"])
            fixture.terminal_path.write_bytes(canonical(fixture.terminal_value))
            fixture.args["terminal"] = binding(fixture.terminal_path)
            result = fixture.run()
            self.assertEqual(result.status, "NOT_ADMITTED")
            self.assertTrue(fixture.result.publication.path.exists())
            self.assertIsNone(result.acceptance)

    def test_original_candidate_and_completion_mutation_cannot_accept(self):
        for mode in ("candidate", "completion", "targets"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                fixture = ReadbackFixture(Path(temporary).resolve())
                path = (fixture.result.publication.path if mode == "candidate" else
                        fixture.config.final_completion.path if mode == "completion" else
                        fixture.assessment.target_path)
                before = path.read_bytes(); info = path.stat()
                path.write_bytes(before[:-1]+(b"x" if before[-1:] != b"x" else b"y"))
                os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
                self.assertEqual(fixture.run().status, "NOT_ADMITTED")

    def test_repeated_acceptance_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = ReadbackFixture(Path(temporary).resolve())
            first = fixture.run(); self.assertEqual(first.status, "PASS")
            before = first.acceptance.path.read_bytes()
            second = fixture.run()
            self.assertEqual((second.status, second.reason), ("NOT_ADMITTED", "ALREADY_ASSESSED"))
            self.assertEqual(first.acceptance.path.read_bytes(), before)

    def test_foreign_launch_config_cannot_admit_same_score(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = ReadbackFixture(Path(temporary).resolve())
            foreign = replace(fixture.config, task_manifest=fixture.config.hidden_ids)
            with patch.object(completion, "load_bridge_from_config", return_value=fixture.assessment.phase.bridge):
                result = readback.accept_assessment(foreign, **fixture.args)
            self.assertEqual(result.status, "NOT_ADMITTED")


    def test_late_candidate_mutation_during_acceptance_cannot_return_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = ReadbackFixture(Path(temporary).resolve())
            real_publish = readback._publish
            def mutate(*args, **kwargs):
                value = real_publish(*args, **kwargs)
                fixture.result.publication.path.write_bytes(b"{}")
                return value
            with patch.object(readback, "_publish", side_effect=mutate):
                result = fixture.run()
            self.assertNotEqual(result.status, "PASS")
            self.assertIsNone(result.acceptance)

    def test_partial_acceptance_is_preserved_and_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = ReadbackFixture(Path(temporary).resolve())
            real_write = os.write
            calls = 0
            def partial(descriptor, data):
                nonlocal calls
                calls += 1
                if calls == 1:
                    return real_write(descriptor, data[:1])
                raise OSError("synthetic interrupted acceptance")
            with patch.object(readback.os, "write", side_effect=partial):
                first = fixture.run()
            self.assertNotEqual(first.status, "PASS")
            path = fixture.assessment.output / "assessment-acceptance.json"
            self.assertEqual(path.read_bytes(), b"{")
            self.assertEqual(fixture.run().reason, "ALREADY_ASSESSED")
            self.assertEqual(path.read_bytes(), b"{")

    def test_capture_disappearance_after_verification_is_unknown(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = ReadbackFixture(Path(temporary).resolve())
            real_publish = readback._publish
            def disappear(*args, **kwargs):
                value = real_publish(*args, **kwargs)
                fixture.out.unlink()
                return value
            with patch.object(readback, "_publish", side_effect=disappear):
                result = fixture.run()
            self.assertEqual(result.status, "UNKNOWN")
            self.assertIsNone(result.acceptance)


if __name__ == "__main__":
    unittest.main(verbosity=2)
