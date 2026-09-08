"""Failure-first synthetic controls for trusted_io; no ORX process is launched."""

from __future__ import annotations

import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import uuid

from source_closure import ClosureLimits, capture_tree

from trusted_io import (
    AdmissionState,
    DevResultReceipt,
    FinalArtifactBinding,
    FinalRefitIdentity,
    FinalRefitPhase,
    FinalSelectionBinding,
    Snapshot,
    SolutionName,
    TrustedIo,
    TrustedIoError,
    TrustedIoErrorCode,
    TrustedIoLimits,
)


def _limits() -> TrustedIoLimits:
    return TrustedIoLimits(
        max_name_bytes=64,
        max_file_bytes=1024,
        max_closure_bytes=2048,
        max_write_bytes=1024,
        max_state_bytes=16384,
        max_snapshot_count=5,
        max_snapshot_bytes=8192,
    )


def _write_fixture(source: Path, solution: str = "print('safe')\n", intent: str = '{"kind":"dev"}\n') -> None:
    source.mkdir()
    (source / "solution.py").write_text(solution)
    (source / "research.md").write_text("synthetic research\n")
    (source / "intent.json").write_text(intent)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _selection_binding(receipt_sha256: str) -> FinalSelectionBinding:
    return FinalSelectionBinding(
        selection_receipt_sha256=receipt_sha256,
        task_sha256=_digest("task"),
        environment_sha256=_digest("environment"),
        protocol_sha256=_digest("protocol"),
    )


def _final_identity(receipt_sha256: str) -> FinalRefitIdentity:
    return FinalRefitIdentity(
        phase=FinalRefitPhase.FINAL_REFIT,
        selection_receipt_sha256=receipt_sha256,
        execution_config_sha256=_digest("frozen-final-execution"),
        outer_training_manifest_sha256=_digest("outer-training-manifest"),
        hidden_features_manifest_sha256=_digest("hidden-features-manifest"),
    )


def _admission_worker(source: str, state: str, event: object, queue: object) -> None:
    # Spawned independent interpreter: this is a restart/process admission control.
    io = TrustedIo(source, state, _limits())
    snapshot = io.snapshot()
    event.wait(10)  # type: ignore[union-attr]
    try:
        admission = io.admit_intent(snapshot)
    except TrustedIoError as exc:
        queue.put(("admit-error", exc.code.value))  # type: ignore[union-attr]
    else:
        queue.put(("admit-ok", admission.state.value))  # type: ignore[union-attr]


def _select_worker(source: str, state: str, snapshot: object, event: object, queue: object) -> None:
    io = TrustedIo(source, state, _limits())
    event.wait(10)  # type: ignore[union-attr]
    receipt = DevResultReceipt(_digest("race-receipt"), snapshot.closure_sha256, snapshot.solution_sha256)  # type: ignore[union-attr]
    try:
        io.select_final_method(snapshot.closure_sha256, snapshot.solution_sha256, [receipt], _selection_binding(receipt.receipt_sha256))  # type: ignore[union-attr]
    except TrustedIoError as exc:
        queue.put(("select-error", exc.code.value))  # type: ignore[union-attr]
    else:
        queue.put(("select-ok", ""))  # type: ignore[union-attr]


def _write_worker(source: str, state: str, event: object, queue: object) -> None:
    io = TrustedIo(source, state, _limits())
    event.wait(10)  # type: ignore[union-attr]
    try:
        io.write_solution(SolutionName.SOLUTION, "print('raced write')\n")
    except TrustedIoError as exc:
        queue.put(("write-error", exc.code.value))  # type: ignore[union-attr]
    else:
        queue.put(("write-ok", ""))  # type: ignore[union-attr]


def _final_refit_worker(source: str, state: str, selection_receipt_sha256: str, event: object, queue: object) -> None:
    io = TrustedIo(source, state, _limits())
    event.wait(10)  # type: ignore[union-attr]
    try:
        admission = io.admit_final_refit(_final_identity(selection_receipt_sha256))
    except TrustedIoError as exc:
        queue.put(("final-error", exc.code.value))  # type: ignore[union-attr]
    else:
        queue.put(("final-ok", admission.state.value))  # type: ignore[union-attr]


class TrustedIoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        self.source = base / "source"
        self.state = base / "state"
        _write_fixture(self.source)
        self.io = TrustedIo(self.source, self.state, _limits())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def assert_code(self, code: TrustedIoErrorCode, call: object) -> None:
        with self.assertRaises(TrustedIoError) as caught:
            call()  # type: ignore[operator]
        self.assertEqual(caught.exception.code, code)

    def permitted_receipt(self, snapshot: object) -> DevResultReceipt:
        return DevResultReceipt(
            receipt_sha256=_digest("trusted-dev-receipt"),
            closure_sha256=snapshot.closure_sha256,  # type: ignore[union-attr]
            code_sha256=snapshot.solution_sha256,  # type: ignore[union-attr]
        )

    def selection_binding(self, snapshot: object) -> FinalSelectionBinding:
        return _selection_binding(self.permitted_receipt(snapshot).receipt_sha256)

    def select(self) -> object:
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        receipt = self.permitted_receipt(snapshot)
        return self.io.select_final_method(snapshot.closure_sha256, snapshot.solution_sha256, [receipt], _selection_binding(receipt.receipt_sha256))

    def admit_and_bind_final_refit(self, snapshot: object, run_id: str) -> None:
        receipt = self.permitted_receipt(snapshot)
        self.io.admit_final_refit(_final_identity(receipt.receipt_sha256))
        self.io.bind_final_refit(run_id)

    def test_t07_naive_prefix_control_and_flat_name_rejection(self) -> None:
        # Failing-first control: lexical prefix checking accepts an escaped sibling.
        escaped = self.source.parent / "source-escape" / "canary.txt"
        escaped.parent.mkdir()
        escaped.write_text("canary")
        naive_root = self.source.resolve()
        naive_candidate = (self.source / "../source-escape/canary.txt").resolve()
        self.assertTrue(str(naive_candidate).startswith(str(naive_root)))
        for value in ("../source-escape/canary.txt", "/tmp/canary", "solution.py\x00x", "soluti\u0456on.py", "other.py"):
            self.assert_code(TrustedIoErrorCode.INVALID_NAME, lambda value=value: self.io.read_solution(value))
        self.assertEqual(escaped.read_text(), "canary")

    def test_t07_symlink_hardlink_and_fifo_controls(self) -> None:
        outside = self.source.parent / "outside.txt"
        outside.write_text("host-sentinel")
        target = self.source / "solution.py"
        target.unlink()
        target.symlink_to(outside)
        self.assertEqual(target.read_text(), "host-sentinel")  # naive read control
        self.assert_code(TrustedIoErrorCode.UNSAFE_FILE, lambda: self.io.read_solution(SolutionName.SOLUTION))
        target.unlink()
        os.link(outside, target)
        self.assert_code(TrustedIoErrorCode.UNSAFE_FILE, lambda: self.io.read_solution(SolutionName.SOLUTION))
        target.unlink()
        os.mkfifo(target)
        self.assert_code(TrustedIoErrorCode.UNSAFE_FILE, lambda: self.io.read_solution(SolutionName.SOLUTION))

    def test_t07_descriptor_identity_detects_fixture_swap_during_read(self) -> None:
        original_read = os.read
        changed = False

        def mutate_after_open(fd: int, size: int) -> bytes:
            nonlocal changed
            if not changed:
                changed = True
                (self.source / "solution.py").write_text("fixture mutation after descriptor open\n")
            return original_read(fd, size)

        with mock.patch("trusted_io.os.read", side_effect=mutate_after_open):
            self.assert_code(TrustedIoErrorCode.UNSAFE_FILE, lambda: self.io.read_solution(SolutionName.SOLUTION))

    def test_t07_size_and_expected_hash_controls(self) -> None:
        self.io.write_solution(SolutionName.SOLUTION, "first\n")
        expected = self.io.read_solution(SolutionName.SOLUTION).sha256
        self.io.write_solution(SolutionName.SOLUTION, "second\n", expected)
        self.assert_code(
            TrustedIoErrorCode.HASH_MISMATCH,
            lambda: self.io.write_solution(SolutionName.SOLUTION, "third\n", expected),
        )
        self.assert_code(
            TrustedIoErrorCode.LIMIT_EXCEEDED,
            lambda: self.io.write_solution(SolutionName.SOLUTION, "x" * 1025),
        )
        small = TrustedIoLimits(64, 20, 30, 20, 4096, 5, 1024)
        limited_state = self.source.parent / "limited-state"
        limited = TrustedIo(self.source, limited_state, small)
        self.assert_code(TrustedIoErrorCode.LIMIT_EXCEEDED, limited.snapshot)

    def test_t07_write_rejects_existing_unsafe_target(self) -> None:
        outside = self.source.parent / "outside.txt"
        outside.write_text("host-sentinel")
        target = self.source / "solution.py"
        target.unlink()
        target.symlink_to(outside)
        self.assert_code(
            TrustedIoErrorCode.UNSAFE_FILE,
            lambda: self.io.write_solution(SolutionName.SOLUTION, "replacement\n"),
        )
        self.assertEqual(outside.read_text(), "host-sentinel")

    def test_t09_parallel_processes_admit_one_and_only_one(self) -> None:
        context = multiprocessing.get_context("spawn")
        event = context.Event()
        queue = context.Queue()
        processes = [
            context.Process(target=_admission_worker, args=(str(self.source), str(self.state), event, queue))
            for _ in range(2)
        ]
        for process in processes:
            process.start()
        event.set()
        results = [queue.get(timeout=15) for _ in processes]
        for process in processes:
            process.join(15)
            self.assertEqual(process.exitcode, 0)
        self.assertEqual(results.count(("admit-ok", AdmissionState.PENDING.value)), 1)
        errors = [result for result in results if result[0] == "admit-error"]
        self.assertEqual(len(errors), 1)
        self.assertIn(errors[0][1], {TrustedIoErrorCode.ADMISSION_UNCERTAIN.value, TrustedIoErrorCode.LOCK_UNAVAILABLE.value})

    def test_t09_reload_pending_admission_is_uncertain_not_retried(self) -> None:
        snapshot = self.io.snapshot()
        self.assertEqual(self.io.admit_intent(snapshot).state, AdmissionState.PENDING)
        reloaded = TrustedIo(self.source, self.state, _limits())
        self.assert_code(TrustedIoErrorCode.ADMISSION_UNCERTAIN, lambda: reloaded.admit_intent(reloaded.snapshot()))
        self.assertEqual(reloaded.admission(snapshot).state, AdmissionState.PENDING)
        self.assertEqual(reloaded.bind_admission(snapshot, str(uuid.uuid4())).state, AdmissionState.BOUND)
        self.assert_code(TrustedIoErrorCode.ADMISSION_EXISTS, lambda: reloaded.admit_intent(reloaded.snapshot()))

    def test_t09_distinct_immutable_closures_can_be_admitted(self) -> None:
        first = self.io.snapshot()
        self.io.admit_intent(first)
        self.io.write_solution(SolutionName.INTENT, '{"kind":"different-dev"}\n')
        second = self.io.snapshot()
        self.assertNotEqual(first.closure_sha256, second.closure_sha256)
        self.assertEqual(self.io.admit_intent(second).closure_sha256, second.closure_sha256)

    def test_t09_crash_stale_transaction_lock_fails_closed(self) -> None:
        lock = self.state / ".trusted-io.transaction.lock"
        lock.write_text("synthetic stale lock")
        self.assert_code(
            TrustedIoErrorCode.LOCK_UNAVAILABLE,
            lambda: self.io.write_solution(SolutionName.RESEARCH, "should not write\n"),
        )
        self.assertTrue(lock.exists())
        self.assertEqual(self.io.read_solution(SolutionName.RESEARCH).content, "synthetic research\n")

    def test_hpio001_historical_snapshot_is_private_and_selectable_after_final_intent(self) -> None:
        first = self.io.snapshot()
        self.io.admit_intent(first)
        self.io.write_solution(SolutionName.SOLUTION, "print('later candidate')\n")
        self.io.write_solution(SolutionName.INTENT, '{"kind":"later-dev"}\n')
        second = self.io.snapshot()
        self.io.admit_intent(second)
        self.io.write_solution(SolutionName.INTENT, '{"phase":"final_refit"}\n')
        receipt = self.permitted_receipt(first)
        selection = self.io.select_final_method(
            first.closure_sha256,
            first.solution_sha256,
            [receipt],
            _selection_binding(receipt.receipt_sha256),
        )
        self.assertNotEqual(first.closure_sha256, second.closure_sha256)
        self.assertEqual(selection.code_sha256, first.solution_sha256)
        self.assertEqual((self.state / "final-solution.py").read_bytes(), first.solution_bytes)
        stored = self.state / "snapshots" / first.closure_sha256
        self.assertEqual((stored / "solution.py").read_bytes(), first.solution_bytes)
        self.assertEqual((stored / "research.md").read_bytes(), first.research_bytes)
        self.assertEqual((stored / "intent.json").read_bytes(), first.intent_bytes)

    def test_hpio001_tampered_private_snapshot_cannot_be_selected(self) -> None:
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        receipt = self.permitted_receipt(snapshot)
        (self.state / "snapshots" / snapshot.closure_sha256 / "solution.py").write_text("tampered")
        self.assert_code(
            TrustedIoErrorCode.STATE_CORRUPT,
            lambda: self.io.select_final_method(
                snapshot.closure_sha256,
                snapshot.solution_sha256,
                [receipt],
                _selection_binding(receipt.receipt_sha256),
            ),
        )

    def test_hpio001_incomplete_private_snapshot_fails_closed_and_remains(self) -> None:
        snapshot = self.io.snapshot()
        incomplete = self.state / "snapshots" / snapshot.closure_sha256
        incomplete.mkdir(parents=True)
        (incomplete / "solution.py").write_bytes(snapshot.solution_bytes)
        self.assert_code(TrustedIoErrorCode.STATE_CORRUPT, lambda: self.io.admit_intent(snapshot))
        self.assertTrue(incomplete.exists())


    def test_t14_selection_requires_matching_permitted_receipt_and_freezes_writes(self) -> None:
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        wrong = DevResultReceipt(_digest("wrong"), snapshot.closure_sha256, _digest("different-code"))
        self.assert_code(
            TrustedIoErrorCode.RECEIPT_NOT_PERMITTED,
            lambda: self.io.select_final_method(snapshot.closure_sha256, snapshot.solution_sha256, [wrong], _selection_binding(wrong.receipt_sha256)),
        )
        selection = self.io.select_final_method(
            snapshot.closure_sha256,
            snapshot.solution_sha256,
            [self.permitted_receipt(snapshot)],
            self.selection_binding(snapshot),
        )
        self.assertEqual(selection.code_sha256, snapshot.solution_sha256)
        self.assertEqual(selection.task_sha256, _digest("task"))
        self.assertEqual(selection.environment_sha256, _digest("environment"))
        self.assertEqual(selection.protocol_sha256, _digest("protocol"))
        self.assert_code(
            TrustedIoErrorCode.FINALIZED,
            lambda: self.io.write_solution(SolutionName.SOLUTION, "print('post-lock')\n"),
        )
        self.assert_code(TrustedIoErrorCode.FINALIZED, lambda: self.io.admit_intent(snapshot))
        final_code = (self.state / "final-solution.py").read_bytes()
        self.assertEqual(hashlib.sha256(final_code).hexdigest(), snapshot.solution_sha256)
        self.assertEqual(final_code, snapshot.solution_bytes)

    def test_t14_parallel_select_write_cannot_mutate_selected_code(self) -> None:
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        context = multiprocessing.get_context("spawn")
        event = context.Event()
        queue = context.Queue()
        select = context.Process(target=_select_worker, args=(str(self.source), str(self.state), snapshot, event, queue))
        write = context.Process(target=_write_worker, args=(str(self.source), str(self.state), event, queue))
        select.start()
        write.start()
        event.set()
        results = [queue.get(timeout=15) for _ in range(2)]
        for process in (select, write):
            process.join(15)
            self.assertEqual(process.exitcode, 0)
        selected = [row for row in results if row[0].startswith("select-")]
        written = [row for row in results if row[0].startswith("write-")]
        self.assertEqual(len(selected), 1)
        self.assertEqual(len(written), 1)
        self.assertIn(selected[0], (("select-ok", ""), ("select-error", TrustedIoErrorCode.LOCK_UNAVAILABLE.value)))
        self.assertIn(written[0], (("write-ok", ""), ("write-error", TrustedIoErrorCode.LOCK_UNAVAILABLE.value),
                                  ("write-error", TrustedIoErrorCode.FINALIZED.value)))
        self.assertTrue(selected[0][0] == "select-ok" or written[0][0] == "write-ok")
        if selected[0][0] == "select-ok":
            self.assertEqual(self.io.final_selection().code_sha256, snapshot.solution_sha256)
            self.assertEqual((self.state / "final-solution.py").read_bytes(), snapshot.solution_bytes)
            self.assert_code(TrustedIoErrorCode.FINALIZED,
                             lambda: self.io.write_solution(SolutionName.SOLUTION, "post-selection write\n"))
        else:
            self.assert_code(TrustedIoErrorCode.SELECTION_NOT_FOUND, self.io.final_selection)
            self.assertFalse((self.state / "final-solution.py").exists())
        expected_active = b"print('raced write')\n" if written[0][0] == "write-ok" else snapshot.solution_bytes
        self.assertEqual((self.source / "solution.py").read_bytes(), expected_active)

    def test_t09_final_refit_is_one_fence_across_processes_and_restart(self) -> None:
        snapshot = self.io.snapshot()
        selection = self.select()
        context = multiprocessing.get_context("spawn")
        event = context.Event()
        queue = context.Queue()
        processes = [
            context.Process(
                target=_final_refit_worker,
                args=(str(self.source), str(self.state), selection.selection_receipt_sha256, event, queue),
            )
            for _ in range(2)
        ]
        for process in processes:
            process.start()
        event.set()
        results = [queue.get(timeout=15) for _ in processes]
        for process in processes:
            process.join(15)
            self.assertEqual(process.exitcode, 0)
        self.assertEqual(results.count(("final-ok", AdmissionState.PENDING.value)), 1)
        errors = [result for result in results if result[0] == "final-error"]
        self.assertEqual(len(errors), 1)
        self.assertIn(errors[0][1], {TrustedIoErrorCode.FINAL_REFIT_UNCERTAIN.value, TrustedIoErrorCode.LOCK_UNAVAILABLE.value})
        reloaded = TrustedIo(self.source, self.state, _limits())
        self.assertEqual(reloaded.final_refit_admission().state, AdmissionState.PENDING)
        self.assert_code(
            TrustedIoErrorCode.FINAL_REFIT_UNCERTAIN,
            lambda: reloaded.admit_final_refit(_final_identity(selection.selection_receipt_sha256)),
        )
        run_id = str(uuid.uuid4())
        self.assertEqual(reloaded.bind_final_refit(run_id).state, AdmissionState.BOUND)
        self.assert_code(
            TrustedIoErrorCode.FINAL_REFIT_EXISTS,
            lambda: reloaded.admit_final_refit(_final_identity(selection.selection_receipt_sha256)),
        )

    def test_t14_final_refit_requires_selection_binding_and_bound_run(self) -> None:
        snapshot = self.io.snapshot()
        selection = self.select()
        wrong_identity = _final_identity(_digest("wrong-selection-receipt"))
        self.assert_code(TrustedIoErrorCode.RECEIPT_NOT_PERMITTED, lambda: self.io.admit_final_refit(wrong_identity))
        invalid_phase = FinalRefitIdentity(
            phase="development",  # type: ignore[arg-type]
            selection_receipt_sha256=selection.selection_receipt_sha256,
            execution_config_sha256=_digest("frozen-final-execution"),
            outer_training_manifest_sha256=_digest("outer-training-manifest"),
            hidden_features_manifest_sha256=_digest("hidden-features-manifest"),
        )
        self.assert_code(TrustedIoErrorCode.INVALID_VALUE, lambda: self.io.admit_final_refit(invalid_phase))
        identity = _final_identity(selection.selection_receipt_sha256)
        self.assertEqual(self.io.admit_final_refit(identity).state, AdmissionState.PENDING)
        binding = FinalArtifactBinding(
            str(uuid.uuid4()), _digest("artifact"), _digest("task"), _digest("environment"), _digest("protocol")
        )
        self.assert_code(TrustedIoErrorCode.FINAL_REFIT_UNCERTAIN, lambda: self.io.lock_final_artifact(binding))
        run_id = str(uuid.uuid4())
        self.io.bind_final_refit(run_id)
        wrong_protocol = FinalArtifactBinding(run_id, _digest("artifact"), _digest("task"), _digest("environment"), _digest("other-protocol"))
        self.assert_code(TrustedIoErrorCode.RECEIPT_NOT_PERMITTED, lambda: self.io.lock_final_artifact(wrong_protocol))

    def test_t14_final_lock_binds_trusted_inputs_and_is_single_use(self) -> None:
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        self.io.select_final_method(
            snapshot.closure_sha256,
            snapshot.solution_sha256,
            [self.permitted_receipt(snapshot)],
            self.selection_binding(snapshot),
        )
        run_id = str(uuid.uuid4())
        self.admit_and_bind_final_refit(snapshot, run_id)
        binding = FinalArtifactBinding(
            run_id=run_id,
            artifact_sha256=_digest("artifact"),
            task_sha256=_digest("task"),
            environment_sha256=_digest("environment"),
            protocol_sha256=_digest("protocol"),
        )
        locked = self.io.lock_final_artifact(binding)
        self.assertEqual(locked.run_id, binding.run_id)
        self.assertEqual(locked.code_sha256, snapshot.solution_sha256)
        self.assertEqual(locked.outer_training_manifest_sha256, _digest("outer-training-manifest"))
        self.assertEqual(locked.hidden_features_manifest_sha256, _digest("hidden-features-manifest"))
        self.assertEqual(self.io.final_artifact_lock(), locked)
        self.assert_code(TrustedIoErrorCode.FINALIZED, lambda: self.io.lock_final_artifact(binding))
        self.assert_code(
            TrustedIoErrorCode.FINALIZED,
            lambda: self.io.write_solution(SolutionName.INTENT, '{"post":"lock"}'),
        )

    def test_t14_final_lock_detects_final_code_fixture_mutation(self) -> None:
        snapshot = self.io.snapshot()
        self.select()
        run_id = str(uuid.uuid4())
        self.admit_and_bind_final_refit(snapshot, run_id)
        (self.state / "final-solution.py").write_text("tampered")
        binding = FinalArtifactBinding(
            run_id, _digest("artifact"), _digest("task"), _digest("environment"), _digest("protocol")
        )
        self.assert_code(TrustedIoErrorCode.STATE_CORRUPT, lambda: self.io.lock_final_artifact(binding))

    def test_snapshot_identity_is_opened_bytes_not_intent_self_attestation(self) -> None:
        first = self.io.snapshot()
        declared = json.loads((self.source / "intent.json").read_text())
        declared["claimed_solution_hash"] = "0" * 64
        self.io.write_solution(SolutionName.INTENT, json.dumps(declared))
        second = self.io.snapshot()
        self.assertNotEqual(first.closure_sha256, second.closure_sha256)
        self.assertEqual(first.solution_sha256, second.solution_sha256)
        self.assertNotEqual(first.intent_sha256, second.intent_sha256)


    def test_hpio002_aggregate_cap_rejects_before_second_descriptor_read(self) -> None:
        source = self.source.parent / "aggregate-source"
        _write_fixture(source, solution="12345678", intent="12345678")
        (source / "research.md").write_text("12345678")
        limited = TrustedIo(source, self.source.parent / "aggregate-state", TrustedIoLimits(64, 10, 15, 10, 4096, 5, 1024))
        original_read = os.read
        calls: list[int] = []

        def counted_read(fd: int, size: int) -> bytes:
            value = original_read(fd, size)
            calls.append(len(value))
            return value

        with mock.patch("trusted_io.os.read", side_effect=counted_read):
            self.assert_code(TrustedIoErrorCode.LIMIT_EXCEEDED, limited.snapshot)
        self.assertEqual(calls, [8])

    def test_hpio005_forged_snapshot_fields_are_rederived_and_rejected(self) -> None:
        snapshot = self.io.snapshot()
        forged = Snapshot(
            closure_sha256=snapshot.closure_sha256,
            solution_sha256="0" * 64,
            research_sha256=snapshot.research_sha256,
            intent_sha256=snapshot.intent_sha256,
            solution_bytes=b"forged",
            research_bytes=snapshot.research_bytes,
            intent_bytes=snapshot.intent_bytes,
        )
        self.assert_code(TrustedIoErrorCode.INVALID_VALUE, lambda: self.io.admit_intent(forged))

    def test_hpio006_anchored_source_and_state_root_replacement_fail_closed(self) -> None:
        moved_source = self.source.parent / "moved-source"
        self.source.rename(moved_source)
        _write_fixture(self.source)
        self.assert_code(TrustedIoErrorCode.UNSAFE_FILE, self.io.snapshot)

        replacement_source = self.source.parent / "replacement-source"
        _write_fixture(replacement_source)
        replacement_state = self.source.parent / "replacement-state"
        stable = TrustedIo(replacement_source, replacement_state, _limits())
        stable_snapshot = stable.snapshot()
        moved_state = self.source.parent / "moved-state"
        replacement_state.rename(moved_state)
        replacement_state.mkdir()
        self.assert_code(TrustedIoErrorCode.UNSAFE_FILE, lambda: stable.admit_intent(stable_snapshot))

    def test_hpio004_final_identity_changes_with_stored_code_and_task(self) -> None:
        def admitted_identity(label: str) -> str:
            source = self.source.parent / f"identity-source-{label}"
            state = self.source.parent / f"identity-state-{label}"
            _write_fixture(source, solution=f"print('{label}')\n")
            io = TrustedIo(source, state, _limits())
            snapshot = io.snapshot()
            io.admit_intent(snapshot)
            receipt = DevResultReceipt(_digest("shared-receipt"), snapshot.closure_sha256, snapshot.solution_sha256)
            binding = FinalSelectionBinding(
                receipt.receipt_sha256,
                _digest(f"task-{label}"),
                _digest("environment"),
                _digest("protocol"),
            )
            io.select_final_method(snapshot.closure_sha256, snapshot.solution_sha256, [receipt], binding)
            identity = FinalRefitIdentity(
                FinalRefitPhase.FINAL_REFIT,
                receipt.receipt_sha256,
                _digest("execution"),
                _digest("outer"),
                _digest("hidden-features"),
            )
            return io.admit_final_refit(identity).execution_identity_sha256

        self.assertNotEqual(admitted_identity("a"), admitted_identity("b"))



    def test_hpiov2_final_lock_restart_rejects_each_duplicated_refit_field(self) -> None:
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        receipt = self.permitted_receipt(snapshot)
        self.io.select_final_method(snapshot.closure_sha256, snapshot.solution_sha256, [receipt], _selection_binding(receipt.receipt_sha256))
        run_id = str(uuid.uuid4())
        self.io.admit_final_refit(_final_identity(receipt.receipt_sha256))
        self.io.bind_final_refit(run_id)
        self.io.lock_final_artifact(FinalArtifactBinding(run_id, _digest("artifact"), _digest("task"), _digest("environment"), _digest("protocol")))
        state_path = self.state / "state.json"
        original = json.loads(state_path.read_text())
        for field in ("execution_config_sha256", "outer_training_manifest_sha256", "hidden_features_manifest_sha256"):
            tampered = json.loads(json.dumps(original))
            tampered["final_lock"][field] = _digest(f"tampered-{field}")
            state_path.write_text(json.dumps(tampered, sort_keys=True, separators=(",", ":")))
            reloaded = TrustedIo(self.source, self.state, _limits())
            self.assert_code(TrustedIoErrorCode.STATE_CORRUPT, reloaded.final_artifact_lock)
        state_path.write_text(json.dumps(original, sort_keys=True, separators=(",", ":")))

    def test_hpiov2_max_state_400_preflights_before_extra_store(self) -> None:
        capped = TrustedIoLimits(64, 1024, 2048, 1024, 400, 5, 8192)
        source = self.source.parent / "state-cap-source"
        state = self.source.parent / "state-cap-state"
        _write_fixture(source)
        io = TrustedIo(source, state, capped)
        accepted: list[Snapshot] = []
        failed: Snapshot | None = None
        for index in range(1, 7):
            io.write_solution(SolutionName.INTENT, json.dumps({"kind": f"candidate-{index}"}))
            candidate = io.snapshot()
            try:
                io.admit_intent(candidate)
            except TrustedIoError as exc:
                self.assertEqual(exc.code, TrustedIoErrorCode.LIMIT_EXCEEDED)
                failed = candidate
                break
            accepted.append(candidate)
        self.assertIsNotNone(failed)
        self.assertLess(len(accepted), capped.max_snapshot_count)
        stored = {item.name for item in (state / "snapshots").iterdir()}
        self.assertEqual(stored, {candidate.closure_sha256 for candidate in accepted})
        self.assertNotIn(failed.closure_sha256, stored)  # type: ignore[union-attr]


    def test_hpiov2_handled_mid_store_failure_cleans_only_created_temp(self) -> None:
        snapshot = self.io.snapshot()
        original_replace = self.io._replace_at
        failed = False

        def fail_research(directory_fd: int, target: str, content: bytes, limit: int | None = None) -> None:
            nonlocal failed
            if target == SolutionName.RESEARCH.value and not failed:
                failed = True
                raise TrustedIoError(TrustedIoErrorCode.UNSAFE_FILE)
            original_replace(directory_fd, target, content, limit)

        with mock.patch.object(self.io, "_replace_at", side_effect=fail_research):
            self.assert_code(TrustedIoErrorCode.UNSAFE_FILE, lambda: self.io.admit_intent(snapshot))
        snapshots = self.state / "snapshots"
        self.assertEqual(list(snapshots.iterdir()), [])
        self.assert_code(TrustedIoErrorCode.ADMISSION_NOT_FOUND, lambda: self.io.admission(snapshot))

    def test_hpiov2_known_incomplete_temp_counts_against_snapshot_caps(self) -> None:
        capped = TrustedIoLimits(64, 1024, 2048, 1024, 4096, 1, 8192)
        source = self.source.parent / "partial-source"
        state = self.source.parent / "partial-state"
        _write_fixture(source)
        io = TrustedIo(source, state, capped)
        partial = state / "snapshots" / (".snapshot-" + "a" * 32)
        partial.mkdir(parents=True)
        (partial / "solution.py").write_text("partial")
        snapshot = io.snapshot()
        self.assert_code(TrustedIoErrorCode.LIMIT_EXCEEDED, lambda: io.admit_intent(snapshot))
        self.assertTrue(partial.exists())
        self.assertFalse((state / "snapshots" / snapshot.closure_sha256).exists())



    def test_hpiov3_parent_fsync_failure_cleans_identified_temp_with_safe_enum(self) -> None:
        snapshot = self.io.snapshot()
        (self.state / "snapshots").mkdir()
        original_fsync = os.fsync
        calls = 0

        def fail_first_fsync(fd: int) -> None:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise OSError("synthetic parent fsync failure")
            original_fsync(fd)

        with mock.patch("trusted_io.os.fsync", side_effect=fail_first_fsync):
            self.assert_code(TrustedIoErrorCode.UNSAFE_FILE, lambda: self.io._store_snapshot(snapshot))
        self.assertEqual(list((self.state / "snapshots").iterdir()), [])
        self.assertFalse((self.state / "state.json").exists())

    def test_hpiov3_completed_temp_fsync_failure_cleans_identified_temp_with_safe_enum(self) -> None:
        snapshot = self.io.snapshot()
        (self.state / "snapshots").mkdir()
        original_fsync = os.fsync
        calls = 0

        def fail_completed_temp_fsync(fd: int) -> None:
            nonlocal calls
            calls += 1
            if calls == 10:
                raise OSError("synthetic completed-temp fsync failure")
            original_fsync(fd)

        with mock.patch("trusted_io.os.fsync", side_effect=fail_completed_temp_fsync):
            self.assert_code(TrustedIoErrorCode.UNSAFE_FILE, lambda: self.io._store_snapshot(snapshot))
        self.assertEqual(calls, 12)
        self.assertEqual(list((self.state / "snapshots").iterdir()), [])
        self.assertFalse((self.state / "state.json").exists())



    def observation_tree(self):
        return capture_tree(self.state.resolve(), ClosureLimits(256, 8388608, 2097152, 8, 1024))

    def observation_getters(self, snapshot):
        return (
            (lambda: self.io.admission(snapshot), TrustedIoErrorCode.ADMISSION_NOT_FOUND),
            (self.io.final_selection, TrustedIoErrorCode.SELECTION_NOT_FOUND),
            (self.io.final_refit_admission, TrustedIoErrorCode.FINAL_REFIT_NOT_FOUND),
            (self.io.final_artifact_lock, TrustedIoErrorCode.SELECTION_NOT_FOUND),
        )

    def test_read_snapshot_missing_getters_preserve_full_tree(self):
        snapshot = self.io.snapshot()
        for call, code in self.observation_getters(snapshot):
            with self.subTest(code=code):
                before = self.observation_tree()
                self.assert_code(code, call)
                self.assertEqual(self.observation_tree(), before)

    def test_read_snapshot_populated_getters_preserve_typed_state_and_tree(self):
        snapshot = self.io.snapshot()
        pending = self.io.admit_intent(snapshot)
        before = self.observation_tree()
        self.assertEqual(self.io.admission(snapshot), pending)
        self.assertEqual(self.observation_tree(), before)
        run_id = str(uuid.uuid4())
        admitted = self.io.bind_admission(snapshot, run_id)
        permitted = self.permitted_receipt(snapshot)
        selected = self.io.select_final_method(snapshot.closure_sha256, snapshot.solution_sha256,
                                               [permitted], self.selection_binding(snapshot))
        refit = self.io.admit_final_refit(_final_identity(permitted.receipt_sha256))
        before = self.observation_tree()
        self.assertEqual(self.io.final_refit_admission(), refit)
        self.assertEqual(self.observation_tree(), before)
        bound_refit = self.io.bind_final_refit(run_id)
        locked = self.io.lock_final_artifact(FinalArtifactBinding(
            run_id, _digest("artifact"), _digest("task"), _digest("environment"), _digest("protocol")))
        calls = (lambda: self.io.admission(snapshot), self.io.final_selection,
                 self.io.final_refit_admission, self.io.final_artifact_lock)
        for call, expected in zip(calls, (admitted, selected, bound_refit, locked)):
            before = self.observation_tree()
            self.assertEqual(call(), expected)
            self.assertEqual(self.observation_tree(), before)

    def test_read_snapshot_never_writes_or_fsyncs_even_when_value_missing(self):
        snapshot = self.io.snapshot()
        original_open = os.open
        def read_only(path, flags, *args, **kwargs):
            self.assertFalse(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            return original_open(path, flags, *args, **kwargs)
        with mock.patch("trusted_io.os.open", side_effect=read_only), \
             mock.patch("trusted_io.os.write", side_effect=AssertionError("write")), \
             mock.patch("trusted_io.os.fsync", side_effect=AssertionError("fsync")), \
             mock.patch("trusted_io.os.unlink", side_effect=AssertionError("unlink")):
            for call, code in self.observation_getters(snapshot):
                self.assert_code(code, call)

    def test_read_snapshot_any_preexisting_lock_entry_is_preserved(self):
        snapshot = self.io.snapshot()
        lock = self.state / ".trusted-io.transaction.lock"
        target = self.source.parent / "lock-target"
        target.write_bytes(b"untouched")
        for kind in ("regular", "symlink", "fifo", "directory"):
            with self.subTest(kind=kind):
                if kind == "regular": lock.write_bytes(b"stale-writer")
                elif kind == "symlink": lock.symlink_to(target)
                elif kind == "fifo": os.mkfifo(lock)
                else: lock.mkdir()
                before = lock.lstat()
                parent = self.state.stat()
                for call, _ in self.observation_getters(snapshot):
                    self.assert_code(TrustedIoErrorCode.LOCK_UNAVAILABLE, call)
                after = lock.lstat()
                self.assertEqual((after.st_dev, after.st_ino, after.st_mode, after.st_mtime_ns),
                                 (before.st_dev, before.st_ino, before.st_mode, before.st_mtime_ns))
                self.assertEqual(self.state.stat().st_mtime_ns, parent.st_mtime_ns)
                self.assertEqual(target.read_bytes(), b"untouched")
                if kind == "directory": lock.rmdir()
                else: lock.unlink()

    def test_read_snapshot_same_bytes_named_state_replacement_is_conflict(self):
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        state = self.state / "state.json"
        original = state.read_bytes()
        original_inode = state.stat().st_ino
        original_read = os.read
        changed = False
        def replace_during_read(fd, amount):
            nonlocal changed
            data = original_read(fd, amount)
            if not changed and os.fstat(fd).st_ino == original_inode:
                changed = True
                replacement = self.state / "replacement.json"
                replacement.write_bytes(original)
                os.replace(replacement, state)
            return data
        with mock.patch("trusted_io.os.read", side_effect=replace_during_read):
            self.assert_code(TrustedIoErrorCode.SNAPSHOT_CHANGED, lambda: self.io.admission(snapshot))
        self.assertTrue(changed)
        self.assertEqual(state.read_bytes(), original)

    def test_read_snapshot_state_root_replacement_is_conflict(self):
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        state = self.state / "state.json"
        original_inode = state.stat().st_ino
        original_read = os.read
        changed = False
        def replace_root(fd, amount):
            nonlocal changed
            data = original_read(fd, amount)
            if not changed and os.fstat(fd).st_ino == original_inode:
                changed = True
                self.state.rename(self.state.parent / "moved-state")
                self.state.mkdir()
            return data
        with mock.patch("trusted_io.os.read", side_effect=replace_root):
            self.assert_code(TrustedIoErrorCode.SNAPSHOT_CHANGED, lambda: self.io.admission(snapshot))
        self.assertTrue(changed)

    def test_read_snapshot_writer_lock_appearing_during_read_is_conflict(self):
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        state_inode = (self.state / "state.json").stat().st_ino
        lock = self.state / ".trusted-io.transaction.lock"
        original_read = os.read
        changed = False
        def add_writer_lock(fd, amount):
            nonlocal changed
            data = original_read(fd, amount)
            if not changed and os.fstat(fd).st_ino == state_inode:
                changed = True
                replacement = self.state / "writer-lock-temp"
                replacement.write_bytes(b"concurrent-writer")
                os.replace(replacement, lock)
            return data
        with mock.patch("trusted_io.os.read", side_effect=add_writer_lock):
            self.assert_code(TrustedIoErrorCode.SNAPSHOT_CHANGED, lambda: self.io.admission(snapshot))
        self.assertTrue(changed)
        self.assertEqual(lock.read_bytes(), b"concurrent-writer")

    def test_read_snapshot_corrupt_oversized_and_unsafe_state_do_not_mutate_root(self):
        target = self.source.parent / "state-target"
        target.write_bytes(b"{}")
        variants = (("corrupt", TrustedIoErrorCode.STATE_CORRUPT),
                    ("oversized", TrustedIoErrorCode.LIMIT_EXCEEDED),
                    ("symlink", TrustedIoErrorCode.UNSAFE_FILE),
                    ("hardlink", TrustedIoErrorCode.UNSAFE_FILE),
                    ("fifo", TrustedIoErrorCode.UNSAFE_FILE),
                    ("directory", TrustedIoErrorCode.UNSAFE_FILE))
        for kind, code in variants:
            with self.subTest(kind=kind):
                root = self.source.parent / ("unsafe-state-" + kind)
                local = TrustedIo(self.source, root, _limits())
                state = root / "state.json"
                if kind == "corrupt": state.write_bytes(b"not-json")
                elif kind == "oversized": state.write_bytes(b"x" * 16385)
                elif kind == "symlink": state.symlink_to(target)
                elif kind == "hardlink": os.link(target, state)
                elif kind == "fifo": os.mkfifo(state)
                else: state.mkdir()
                before = root.stat()
                self.assert_code(code, local.final_selection)
                after = root.stat()
                self.assertEqual((after.st_ino, after.st_mtime_ns, after.st_ctime_ns),
                                 (before.st_ino, before.st_mtime_ns, before.st_ctime_ns))
                self.assertFalse((root / ".trusted-io.transaction.lock").exists())


    def test_read_snapshot_canonical_empty_state_preserves_all_getters(self):
        state = {"version": 3, "admissions": {}, "final_selection": None,
                 "final_refit_admission": None, "final_lock": None}
        (self.state / "state.json").write_text(json.dumps(state))
        snapshot = self.io.snapshot()
        for call, code in self.observation_getters(snapshot):
            before = self.observation_tree()
            self.assert_code(code, call)
            self.assertEqual(self.observation_tree(), before)

    def test_read_snapshot_in_place_same_size_mutation_is_conflict(self):
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        path = self.state / "state.json"
        original = path.read_bytes()
        expected_inode = path.stat().st_ino
        original_read = os.read
        changed = False
        def mutate(fd, amount):
            nonlocal changed
            value = original_read(fd, amount)
            if not changed and os.fstat(fd).st_ino == expected_inode:
                changed = True
                path.write_bytes(b"x" * len(original))
            return value
        with mock.patch("trusted_io.os.read", side_effect=mutate):
            self.assert_code(TrustedIoErrorCode.SNAPSHOT_CHANGED, lambda: self.io.admission(snapshot))
        self.assertTrue(changed)
        self.assertEqual(path.read_bytes(), b"x" * len(original))

    def test_read_snapshot_transient_writer_lock_invalidates_interval(self):
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        state_inode = (self.state / "state.json").stat().st_ino
        original_read = os.read
        changed = False
        def transient_lock(fd, amount):
            nonlocal changed
            value = original_read(fd, amount)
            if not changed and os.fstat(fd).st_ino == state_inode:
                changed = True
                lock = self.state / ".trusted-io.transaction.lock"
                lock.write_bytes(b"concurrent writer")
                lock.unlink()
            return value
        with mock.patch("trusted_io.os.read", side_effect=transient_lock):
            self.assert_code(TrustedIoErrorCode.SNAPSHOT_CHANGED, lambda: self.io.admission(snapshot))
        self.assertTrue(changed)
        self.assertFalse((self.state / ".trusted-io.transaction.lock").exists())

    def test_read_snapshot_short_positive_reads_and_premature_eof(self):
        snapshot = self.io.snapshot()
        pending = self.io.admit_intent(snapshot)
        original_read = os.read
        before = self.observation_tree()
        with mock.patch("trusted_io.os.read", side_effect=lambda fd, size: original_read(fd, min(size, 3))):
            self.assertEqual(self.io.admission(snapshot), pending)
        self.assertEqual(self.observation_tree(), before)
        with mock.patch("trusted_io.os.read", return_value=b""):
            self.assert_code(TrustedIoErrorCode.SNAPSHOT_CHANGED, lambda: self.io.admission(snapshot))
        self.assertEqual(self.observation_tree(), before)

    def test_read_snapshot_initial_root_replacement_rejected_without_writes(self):
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        old = self.state.parent / "old-anchored-state"
        self.state.rename(old)
        self.state.mkdir()
        (self.state / "state.json").write_bytes((old / "state.json").read_bytes())
        before = capture_tree(self.state.resolve(), ClosureLimits(256, 8388608, 2097152, 8, 1024))
        for call, _ in self.observation_getters(snapshot):
            self.assert_code(TrustedIoErrorCode.UNSAFE_FILE, call)
        self.assertEqual(capture_tree(self.state.resolve(), ClosureLimits(256, 8388608, 2097152, 8, 1024)), before)

    def test_read_snapshot_state_deletion_during_read_is_conflict(self):
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        path = self.state / "state.json"
        expected_inode = path.stat().st_ino
        original_read = os.read
        changed = False
        def remove_after_read(fd, amount):
            nonlocal changed
            value = original_read(fd, amount)
            if not changed and os.fstat(fd).st_ino == expected_inode:
                changed = True
                path.unlink()
            return value
        with mock.patch("trusted_io.os.read", side_effect=remove_after_read):
            self.assert_code(TrustedIoErrorCode.SNAPSHOT_CHANGED, lambda: self.io.admission(snapshot))
        self.assertTrue(changed)
        self.assertFalse(path.exists())

    def test_read_snapshot_absent_state_appearing_after_capture_is_conflict(self):
        snapshot = self.io.snapshot()
        path = self.state / "state.json"
        original_stat = os.stat
        changed = False
        def create_after_absence(name, *args, **kwargs):
            nonlocal changed
            try:
                return original_stat(name, *args, **kwargs)
            except FileNotFoundError:
                if name == "state.json" and kwargs.get("dir_fd") is not None and not changed:
                    changed = True
                    path.write_text(json.dumps({"version": 3, "admissions": {}, "final_selection": None,
                        "final_refit_admission": None, "final_lock": None}))
                raise
        with mock.patch("trusted_io.os.stat", side_effect=create_after_absence):
            self.assert_code(TrustedIoErrorCode.SNAPSHOT_CHANGED, lambda: self.io.admission(snapshot))
        self.assertTrue(changed)
        self.assertTrue(path.exists())

    def test_read_snapshot_shared_decoder_preserves_transaction_semantics(self):
        snapshot = self.io.snapshot()
        self.io.admit_intent(snapshot)
        path = self.state / "state.json"
        valid_admission = path.read_bytes()
        selection = self.io.select_final_method(snapshot.closure_sha256, snapshot.solution_sha256,
            [self.permitted_receipt(snapshot)], self.selection_binding(snapshot))
        self.io.admit_final_refit(_final_identity(selection.selection_receipt_sha256))
        self.io.bind_final_refit(str(uuid.uuid4()))
        valid_refit = path.read_bytes()
        for data in (valid_admission, valid_refit):
            path.write_bytes(data)
            with self.io._transaction():
                transactional = self.io._read_state()
            before = self.observation_tree()
            self.assertEqual(self.io._read_state_snapshot(), transactional)
            self.assertEqual(self.observation_tree(), before)
        malformed = (b"bad-json", b"\xff", b"{}", json.dumps({"version": 2}).encode(),
                     valid_admission.replace(b'"final_lock":null', b'"final_lock":{}'))
        for data in malformed:
            with self.subTest(data=data[:40]):
                path.write_bytes(data)
                with self.io._transaction():
                    self.assert_code(TrustedIoErrorCode.STATE_CORRUPT, self.io._read_state)
                before = self.observation_tree()
                self.assert_code(TrustedIoErrorCode.STATE_CORRUPT, self.io.final_selection)
                self.assertEqual(self.observation_tree(), before)


    def test_t14_deterministic_writer_order_preserves_historical_selection(self):
        for order in ("write_then_select", "select_then_write", "writer_lock_overlap"):
            with self.subTest(order=order):
                source = self.source.parent / (order + "-source")
                state = self.state.parent / (order + "-state")
                _write_fixture(source)
                writer = TrustedIo(source, state, _limits())
                observer = TrustedIo(source, state, _limits())
                snapshot = writer.snapshot()
                writer.admit_intent(snapshot)
                receipt = self.permitted_receipt(snapshot)
                def select():
                    return observer.select_final_method(snapshot.closure_sha256, snapshot.solution_sha256,
                        [receipt], _selection_binding(receipt.receipt_sha256))
                if order == "write_then_select":
                    writer.write_solution(SolutionName.SOLUTION, "print('later active candidate')\n")
                    selected = select()
                    self.assertNotEqual(writer.read_solution(SolutionName.SOLUTION).sha256, selected.code_sha256)
                elif order == "select_then_write":
                    selected = select()
                    self.assert_code(TrustedIoErrorCode.FINALIZED,
                        lambda: writer.write_solution(SolutionName.SOLUTION, "forbidden later write\n"))
                else:
                    with writer._transaction():
                        self.assert_code(TrustedIoErrorCode.LOCK_UNAVAILABLE, select)
                        self.assert_code(TrustedIoErrorCode.LOCK_UNAVAILABLE,
                            lambda: observer.write_solution(SolutionName.SOLUTION, "overlap\n"))
                    self.assert_code(TrustedIoErrorCode.SELECTION_NOT_FOUND, observer.final_selection)
                    self.assertEqual(writer.snapshot(), snapshot)
                    continue
                self.assertEqual(selected.code_sha256, snapshot.solution_sha256)
                self.assertEqual((state / "final-solution.py").read_bytes(), snapshot.solution_bytes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
