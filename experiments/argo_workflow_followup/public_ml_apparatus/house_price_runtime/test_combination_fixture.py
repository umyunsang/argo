"""Mock-only tests for combination_fixture; no NativeHarness effects execute."""
from __future__ import annotations

from hashlib import sha256
import inspect
from io import BytesIO
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime import combination_fixture as fixture_module
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_fixture import (
    CombinationFixtureError,
    FixtureCloseResult,
    OwnedNativeHarness,
    SECOND_SOLUTION,
    _owned_handler,
    prepare_fixture,
)

RUN_IDS = (
    "00000000-0000-0000-0000-000000000101",
    "00000000-0000-0000-0000-000000000102",
)
EXPERIMENT_IDS = (
    "00000000-0000-0000-0000-000000000201",
    "00000000-0000-0000-0000-000000000202",
)
CONTEXT_ID = sha256(b"mock-combination-context").hexdigest()


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


class FakeStore:
    def __init__(self, bridge_state: Path) -> None:
        self.bindings: list[SimpleNamespace] = []
        self.bridge_state = bridge_state

    def read_bindings(self) -> list[SimpleNamespace]:
        return list(self.bindings)


class FakePort:
    def __init__(self, bridge: "FakeBridge") -> None:
        self.bridge = bridge

    def observe(self, binding: SimpleNamespace) -> SimpleNamespace:
        status = self.bridge.statuses[binding.run_id]
        return SimpleNamespace(
            run_id=binding.run_id,
            experiment_id=binding.experiment_id,
            native_commit=binding.native_commit,
            native_source_digest=binding.native_source_digest,
            native_source_size=1,
            status=status,
            cancel_requested=False,
        )


class FakeBridge:
    def __init__(self, harness: "FakeHarness", mode: str) -> None:
        self.harness = harness
        self.mode = mode
        self.actions: list[tuple[str, dict[str, object]]] = []
        self.statuses: dict[str, str] = {}
        self.solutions: dict[str, bytes] = {
            "solution.py": (harness.source / "solution.py").read_bytes(),
            "intent.json": (harness.source / "intent.json").read_bytes(),
            "research.md": (harness.source / "research.md").read_bytes(),
        }
        self.store = FakeStore(harness.bridge_state)
        self.port = FakePort(self)
        self.config = SimpleNamespace(context_rights=SimpleNamespace(
            schema_version="argo-house-price-a2-context-rights/v1",
            controller_context_id=CONTEXT_ID, context="initial",
            initial_context_id=CONTEXT_ID, checkpoint=None,
        ))

    def handle(self, request: object) -> dict[str, object]:
        if not isinstance(request, dict):
            return {"ok": False, "error": "INVALID_ARGUMENT"}
        action = request.get("action")
        arguments = request.get("arguments")
        if not isinstance(action, str) or not isinstance(arguments, dict):
            return {"ok": False, "error": "INVALID_ARGUMENT"}
        self.actions.append((action, dict(arguments)))
        if action == "write_solution":
            path = arguments.get("path")
            content = arguments.get("content")
            if not isinstance(path, str) or not isinstance(content, str):
                return {"ok": False, "error": "INVALID_ARGUMENT"}
            data = content.encode("utf-8")
            self.solutions[path] = data
            (self.harness.source / path).write_bytes(data)
            return {"ok": True, "result": {"path": path, "sha256": digest(data), "bytes": len(data)}}
        if action == "request_R1_run":
            ordinal = len(self.store.bindings)
            if self.mode == "request_error" and ordinal == 1:
                return {"ok": False, "error": "UNCERTAIN_NO_AUTOMATIC_RETRY"}
            run_id = RUN_IDS[0] if self.mode == "duplicate_ids" and ordinal == 1 else RUN_IDS[ordinal]
            experiment_id = EXPERIMENT_IDS[ordinal]
            if self.mode == "wrong_candidate_parent" and ordinal == 1:
                wrong_solution = b"print('self-consistent wrong candidate')\n"
                wrong_intent = json.dumps({
                    "schema_version": "argo-house-price-intent/v1", "phase": "dev",
                    "purpose": "synthetic combination second seed",
                    "solution_sha256": digest(wrong_solution),
                    "parent_run_id": "00000000-0000-0000-0000-000000000999",
                }, sort_keys=True, separators=(",", ":")).encode()
                self.solutions["solution.py"] = wrong_solution
                self.solutions["intent.json"] = wrong_intent
                (self.harness.source / "solution.py").write_bytes(wrong_solution)
                (self.harness.source / "intent.json").write_bytes(wrong_intent)
            solution_hash = digest(self.solutions["solution.py"])
            intent_hash = digest(self.solutions["intent.json"])
            binding = SimpleNamespace(
                run_id=run_id,
                experiment_id=experiment_id,
                phase="dev",
                solution_sha256=solution_hash,
                intent_sha256=intent_hash,
                native_commit=f"{ordinal + 1:040x}",
                native_source_digest=digest(f"source-{ordinal + 1}".encode()),
            )
            self.store.bindings.append(binding)
            self.statuses[run_id] = "RUNNING"
            attempts = self.harness.bridge_state / "attempts"
            bindings = self.harness.bridge_state / "bindings"
            (attempts / f"{ordinal + 1:02d}.json").write_text("{}")
            (bindings / f"{ordinal + 1:02d}.json").write_text("{}")
            (self.harness.trusted_state / f"admission-{ordinal + 1}.json").write_text("{}")
            return {"ok": True, "result": {
                "intent_sha256": intent_hash,
                "run_id": run_id,
                "experiment_id": experiment_id,
                "solution_sha256": solution_hash,
                "phase": "dev",
            }}
        if action == "read_dev_result":
            done = [item for item in self.store.bindings if self.statuses[item.run_id] == "DONE"]
            if self.mode == "no_eligibility" and len(self.store.bindings) == 2:
                done = done[:1]
            return {"ok": True, "result": {"results": [
                {"run_id": item.run_id, "solution_sha256": item.solution_sha256,
                 "valid": True, "mae": "0.000000", "rows": 292}
                for item in done
            ]}}
        if action == "read_public_result":
            return {"ok": True, "result": {
                "phase": "development",
                "dev_attempts": len(self.store.bindings),
                "final_attempts": 0,
                "remaining_dev_opportunities": 3 - len(self.store.bindings),
                "runs": [
                    {"intent_sha256": item.intent_sha256, "run_id": item.run_id,
                     "experiment_id": item.experiment_id, "solution_sha256": item.solution_sha256,
                     "phase": "dev", "status": self.statuses[item.run_id]}
                    for item in self.store.bindings
                ],
            }}
        if action == "read_solution" and arguments == {"path": "research.md"}:
            data = self.solutions["research.md"]
            return {"ok": True, "result": {
                "path": "research.md", "content": data.decode("utf-8"), "sha256": digest(data),
            }}
        return {"ok": False, "error": "TOOL_SURFACE"}

    def mark_done(self, binding: SimpleNamespace) -> None:
        if self.mode == "no_done" and len(self.store.bindings) == 2:
            return
        self.statuses[binding.run_id] = "DONE"


class FakeHarness:
    instances: list["FakeHarness"] = []
    mode = "ok"

    def __init__(self, base: Path, rows: int = 2) -> None:
        if rows != 292:
            raise AssertionError("rows must be 292")
        self.base = base
        self.repo = base / "repo"
        self.local_runs = base / "local-runs"
        self.snapshots = base / "source-snapshots"
        self.output = base / "output"
        self.bridge_state = base / "bridge-state"
        self.source = base / "source"
        self.trusted_state = base / "trusted-state"
        self.home = base / "home"
        for path in (
            self.repo, self.local_runs, self.snapshots, self.output, self.bridge_state,
            self.source, self.trusted_state, self.home,
        ):
            path.mkdir(mode=0o700)
        for name in ("attempts", "bindings", "receipts", "contexts"):
            (self.bridge_state / name).mkdir(mode=0o700)
        initial = b"print('native harness')\n"
        (self.source / "solution.py").write_bytes(initial)
        (self.source / "research.md").write_bytes(b"native research\n")
        (self.source / "intent.json").write_text(json.dumps({
            "schema_version": "argo-house-price-intent/v1", "phase": "dev",
            "purpose": "synthetic first", "solution_sha256": digest(initial),
            "parent_run_id": None,
        }, sort_keys=True, separators=(",", ":")))
        self.close_calls = 0
        self.mark_done_calls = 0
        self.close_result: FixtureCloseResult | None = None
        self._owned_server = object()
        self.bridge: FakeBridge | None = None
        FakeHarness.instances.append(self)

    def deployment(self) -> dict[str, object]:
        return {"schema_version": "argo-house-price-a2-bridge-deployment/v1", "production_enabled": True}

    def mark_done(self, observation: SimpleNamespace, binding: SimpleNamespace, phase: str):
        if phase != "dev" or observation.status != "RUNNING" or self.bridge is None:
            raise AssertionError("invalid mark_done")
        self.mark_done_calls += 1
        self.bridge.mark_done(binding)
        if self.bridge.mode == "final_source_mismatch" and len(self.bridge.store.bindings) == 2:
            (self.source / "solution.py").write_bytes(b"print('late wrong source')\n")
        output = self.output / binding.run_id
        output.mkdir(exist_ok=True)
        (output / "predictions.csv").write_text("Id,SalePrice\n1,10\n")

    def close(self) -> FixtureCloseResult:
        self.close_calls += 1
        if self.close_result is None:
            self.close_result = FixtureCloseResult(
                "argo-house-price-a2-fixture-close/v1", True, True, True,
                True, True, False, None, 0.0,
            )
        return self.close_result


class FakeSocket:
    def __init__(self, descriptor: int = 41) -> None:
        self.descriptor = descriptor

    def fileno(self) -> int:
        return self.descriptor


class FakeServeThread:
    def __init__(self, alive: bool = True, clock: "FakeClock | None" = None) -> None:
        self.alive = alive
        self.clock = clock
        self.join_calls: list[float | None] = []

    def is_alive(self) -> bool:
        return self.alive

    def join(self, timeout: float | None = None) -> None:
        self.join_calls.append(timeout)
        if self.alive and timeout is not None and self.clock is not None:
            self.clock.now += timeout


class FakeServer:
    def __init__(self, serve_thread: FakeServeThread, *, fail: bool = False,
                 close_socket: bool = True, stop_serve: bool = True) -> None:
        self.serve_thread = serve_thread
        self.fail = fail
        self.close_socket = close_socket
        self.stop_serve = stop_serve
        self.socket = FakeSocket()
        self.shutdown_calls = 0
        self.close_calls = 0

    def shutdown(self) -> None:
        self.shutdown_calls += 1
        if self.fail:
            raise RuntimeError("private close detail")
        if self.stop_serve:
            self.serve_thread.alive = False

    def server_close(self) -> None:
        self.close_calls += 1
        if self.close_socket:
            self.socket.descriptor = -1


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now


class FakeCleanupThread:
    def __init__(self, target, *, daemon: bool, clock: FakeClock,
                 execute: bool) -> None:
        self.target = target
        self.daemon = daemon
        self.clock = clock
        self.execute = execute
        self.alive = False
        self.start_calls = 0
        self.join_calls: list[float | None] = []

    def start(self) -> None:
        self.start_calls += 1
        if self.execute:
            self.target()
            self.alive = False
        else:
            self.alive = True

    def join(self, timeout: float | None = None) -> None:
        self.join_calls.append(timeout)
        if self.alive and timeout is not None:
            self.clock.now += timeout

    def is_alive(self) -> bool:
        return self.alive


def owned_harness_for_close(server: FakeServer, serve_thread: FakeServeThread) -> OwnedNativeHarness:
    harness = OwnedNativeHarness.__new__(OwnedNativeHarness)
    harness.server = server
    harness._owned_server = server
    harness._owned_serve_thread = serve_thread
    harness._owned_cleanup_thread = None
    harness._fixture_close_result = None
    return harness


class CombinationFixtureTest(unittest.TestCase):
    def setUp(self) -> None:
        FakeHarness.instances = []
        FakeHarness.mode = "ok"
        self.temporary = tempfile.TemporaryDirectory(prefix="combination-fixture-test-")
        self.parent = Path(self.temporary.name).resolve()
        self.parent.chmod(0o700)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def prepare(self, name: str = "fixture", mode: str = "ok"):
        FakeHarness.mode = mode
        def load(_path: Path, _sha256: str) -> FakeBridge:
            harness = FakeHarness.instances[-1]
            bridge = FakeBridge(harness, mode)
            harness.bridge = bridge
            return bridge
        with patch.object(fixture_module, "OwnedNativeHarness", FakeHarness), \
             patch.object(fixture_module, "load_bridge_from_config", side_effect=load):
            return prepare_fixture(self.parent / name)

    def test_success_returns_exact_owned_snapshot_and_idempotent_close(self) -> None:
        result = self.prepare()
        harness = FakeHarness.instances[0]
        self.assertEqual(result.harness, harness)
        self.assertEqual(result.verified_dev_run_ids, tuple(sorted(RUN_IDS)))
        self.assertEqual(result.context_id, CONTEXT_ID)
        self.assertEqual(result.research_sha256, digest(b"native research\n"))
        self.assertEqual(result.source_tree.root, str(result.source.path))
        self.assertEqual((result.source_tree.root_device, result.source_tree.root_inode),
                         (result.source.device, result.source.inode))
        self.assertEqual(result.trusted_state_tree.root, str(result.trusted_state.path))
        self.assertEqual((result.trusted_state_tree.root_device, result.trusted_state_tree.root_inode),
                         (result.trusted_state.device, result.trusted_state.inode))
        self.assertEqual(result.state_tree.root, str(result.bridge_state.path))
        self.assertEqual((result.state_tree.root_device, result.state_tree.root_inode),
                         (result.bridge_state.device, result.bridge_state.inode))
        self.assertEqual(result.source_tree.file_count, 3)
        config = result.bridge_config.path
        self.assertEqual(config.parent, self.parent / "fixture")
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        self.assertTrue(json.loads(config.read_bytes())["production_enabled"])
        first_close = result.close();second_close = result.close()
        self.assertIs(first_close, second_close)
        self.assertTrue(first_close.confirmed)
        self.assertEqual(harness.close_calls, 1)
        self.assertTrue((self.parent / "fixture").exists())

    def test_two_exact_dev_requests_use_current_second_hash_and_no_other_run_actions(self) -> None:
        self.prepare()
        bridge = FakeHarness.instances[0].bridge
        self.assertIsNotNone(bridge)
        actions = [action for action, _ in bridge.actions]
        self.assertEqual(actions.count("request_R1_run"), 2)
        self.assertEqual(actions.count("write_solution"), 2)
        self.assertNotIn("lock_final_artifact", actions)
        second_writes = [arguments for action, arguments in bridge.actions if action == "write_solution"]
        self.assertEqual(second_writes[0], {"path": "solution.py", "content": SECOND_SOLUTION.decode("utf-8")})
        intent = json.loads(second_writes[1]["content"])
        self.assertEqual(intent, {
            "schema_version": "argo-house-price-intent/v1", "phase": "dev",
            "purpose": "synthetic combination second seed",
            "solution_sha256": digest(SECOND_SOLUTION), "parent_run_id": RUN_IDS[0],
        })
        self.assertEqual(actions.count("read_dev_result"), 2)
        self.assertEqual(actions.count("read_public_result"), 2)
        self.assertEqual(actions.count("read_solution"), 1)

    def test_duplicate_ids_missing_done_or_missing_eligibility_close_once_and_preserve_base(self) -> None:
        for mode in ("duplicate_ids", "no_done", "no_eligibility"):
            with self.subTest(mode=mode):
                base = self.parent / mode
                with self.assertRaisesRegex(CombinationFixtureError, "^COMBINATION_FIXTURE_INVALID$"):
                    self.prepare(mode, mode)
                harness = FakeHarness.instances[-1]
                self.assertEqual(harness.close_calls, 1)
                self.assertTrue(base.exists())

    def test_self_consistent_wrong_second_candidate_and_parent_reject_before_second_mark(self) -> None:
        base = self.parent / "wrong-candidate-parent"
        with self.assertRaisesRegex(CombinationFixtureError, "^COMBINATION_FIXTURE_INVALID$"):
            self.prepare("wrong-candidate-parent", "wrong_candidate_parent")
        harness = FakeHarness.instances[-1]
        self.assertEqual(harness.mark_done_calls, 1)
        self.assertEqual(harness.close_calls, 1)
        self.assertTrue(base.exists())

    def test_final_source_mismatch_rejects_before_tree_return(self) -> None:
        base = self.parent / "final-source-mismatch"
        with self.assertRaisesRegex(CombinationFixtureError, "^COMBINATION_FIXTURE_INVALID$"):
            self.prepare("final-source-mismatch", "final_source_mismatch")
        harness = FakeHarness.instances[-1]
        self.assertEqual(harness.mark_done_calls, 2)
        self.assertEqual(harness.close_calls, 1)
        self.assertTrue(base.exists())

    def test_action_error_closes_once_without_deleting_partial_evidence(self) -> None:
        base = self.parent / "action-error"
        with self.assertRaisesRegex(CombinationFixtureError, "^COMBINATION_FIXTURE_INVALID$") as raised:
            self.prepare("action-error", "request_error")
        harness = FakeHarness.instances[-1]
        self.assertEqual(harness.close_calls, 1)
        self.assertIs(raised.exception.close_result, harness.close_result)
        self.assertTrue(raised.exception.close_result.confirmed)
        self.assertEqual(raised.exception.base.path, base)
        self.assertTrue(base.exists())
        self.assertTrue((base / "bridge-config.json").exists())

    def test_existing_nonprivate_and_nested_git_bases_are_rejected_before_constructor(self) -> None:
        existing = self.parent / "existing";existing.mkdir(mode=0o700)
        with self.assertRaises(CombinationFixtureError):self.prepare("existing")
        nonprivate = self.parent / "nonprivate";self.parent.chmod(0o755)
        with self.assertRaises(CombinationFixtureError):self.prepare("nonprivate")
        self.parent.chmod(0o700)
        git_parent = self.parent / "nested";git_parent.mkdir(mode=0o700);(git_parent / ".git").mkdir()
        with self.assertRaises(CombinationFixtureError):
            with patch.object(fixture_module, "OwnedNativeHarness", FakeHarness):
                prepare_fixture(git_parent / "fixture")
        for name in ("raw", "auth", "profile"):
            forbidden = self.parent / name;forbidden.mkdir(mode=0o700)
            with self.subTest(name=name),self.assertRaises(CombinationFixtureError):
                with patch.object(fixture_module, "OwnedNativeHarness", FakeHarness):
                    prepare_fixture(forbidden / "fixture")
        self.assertEqual(FakeHarness.instances, [])

    def test_owned_handler_matches_frozen_route_and_rejects_credentials_without_socket(self) -> None:
        native_source = inspect.getsource(OwnedNativeHarness.__mro__[1]._start_server)
        owned_source = inspect.getsource(_owned_handler)
        for text in ("Authorization", "Cookie", "/api/projects/", "Content-Length", 'json.dumps({"runs": runs}'):
            self.assertIn(text, native_source)
            self.assertIn(text, owned_source)
        handler_type = _owned_handler(self.parent / "missing-state.json", "project-1")

        def invoke(headers: dict[str, str], path: str):
            handler = handler_type.__new__(handler_type)
            handler.headers = headers
            handler.path = path
            handler.wfile = BytesIO()
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.do_GET()
            return handler

        for header in ("Authorization", "Cookie"):
            auth = invoke({header: "synthetic"}, "/api/projects/project-1/runs")
            with self.subTest(header=header):
                self.assertEqual(auth.send_response.call_args.args, (400,))
        wrong = invoke({}, "/api/projects/project-2/runs")
        self.assertEqual(wrong.send_response.call_args.args, (404,))
        success = invoke({}, "/api/projects/project-1/runs")
        self.assertEqual(success.send_response.call_args.args, (200,))
        self.assertEqual(success.wfile.getvalue(), b'{"runs":[]}')

    def test_owned_close_identity_mismatch_is_unconfirmed_without_cleanup_thread(self) -> None:
        clock = FakeClock();serve = FakeServeThread();owned = FakeServer(serve)
        harness = owned_harness_for_close(owned, serve)
        harness.server = FakeServer(serve)
        with patch.object(fixture_module.threading, "Thread") as thread_factory, \
             patch.object(fixture_module.time, "monotonic", side_effect=clock.monotonic):
            first = harness.close();second = harness.close()
        self.assertIs(first, second)
        self.assertFalse(first.confirmed)
        self.assertEqual(first.error, "CLOSE_IDENTITY_UNKNOWN")
        self.assertFalse(first.timed_out)
        thread_factory.assert_not_called()
        self.assertEqual(owned.shutdown_calls, 0)

    def test_owned_close_success_is_confirmed_bounded_and_cached(self) -> None:
        clock = FakeClock();serve = FakeServeThread();server = FakeServer(serve)
        harness = owned_harness_for_close(server, serve)
        cleanup_threads = []
        def factory(*, target, daemon):
            thread = FakeCleanupThread(target, daemon=daemon, clock=clock, execute=True)
            cleanup_threads.append(thread);return thread
        with patch.object(fixture_module.threading, "Thread", side_effect=factory), \
             patch.object(fixture_module.time, "monotonic", side_effect=clock.monotonic):
            first = harness.close();second = harness.close()
        self.assertIs(first, second)
        self.assertEqual(first, FixtureCloseResult(
            "argo-house-price-a2-fixture-close/v1", True, True, True,
            True, True, False, None, 0.0,
        ))
        self.assertEqual(len(cleanup_threads), 1)
        self.assertEqual(server.shutdown_calls, 1)
        self.assertEqual(server.close_calls, 1)

    def test_owned_close_timeout_is_unconfirmed_and_never_retried(self) -> None:
        clock = FakeClock();serve = FakeServeThread();server = FakeServer(serve)
        harness = owned_harness_for_close(server, serve)
        cleanup_threads = []
        def factory(*, target, daemon):
            thread = FakeCleanupThread(target, daemon=daemon, clock=clock, execute=False)
            cleanup_threads.append(thread);return thread
        with patch.object(fixture_module.threading, "Thread", side_effect=factory), \
             patch.object(fixture_module.time, "monotonic", side_effect=clock.monotonic):
            first = harness.close();second = harness.close()
        self.assertIs(first, second)
        self.assertFalse(first.confirmed)
        self.assertTrue(first.timed_out)
        self.assertEqual(first.error, "CLOSE_TIMEOUT")
        self.assertFalse(first.cleanup_thread_stopped)
        self.assertEqual(len(cleanup_threads), 1)
        self.assertEqual(server.shutdown_calls, 0)

    def test_owned_close_nonfinite_clock_never_manufactures_confirmation(self) -> None:
        serve = FakeServeThread();server = FakeServer(serve)
        harness = owned_harness_for_close(server, serve)
        with patch.object(fixture_module.threading, "Thread") as thread_factory, \
             patch.object(fixture_module.time, "monotonic", return_value=float("nan")):
            result = harness.close()
        self.assertFalse(result.confirmed)
        self.assertEqual(result.error, "CLOSE_IDENTITY_UNKNOWN")
        self.assertEqual(result.elapsed_seconds, 0.0)
        thread_factory.assert_not_called()

        clock = FakeClock();calls = 0;serve = FakeServeThread();server = FakeServer(serve)
        harness = owned_harness_for_close(server, serve)
        def clock_value():
            nonlocal calls
            calls += 1
            return 0.0 if calls <= 3 else float("nan")
        def factory(*, target, daemon):
            return FakeCleanupThread(target, daemon=daemon, clock=clock, execute=True)
        with patch.object(fixture_module.threading, "Thread", side_effect=factory), \
             patch.object(fixture_module.time, "monotonic", side_effect=clock_value):
            result = harness.close()
        self.assertFalse(result.confirmed)
        self.assertEqual(result.error, "CLOSE_IDENTITY_UNKNOWN")
        self.assertTrue(result.shutdown_completed)
        self.assertTrue(result.serve_thread_stopped)
        self.assertTrue(result.socket_closed)

    def test_external_confirmed_result_over_deadline_is_normalized_unconfirmed(self) -> None:
        supplied = FixtureCloseResult(
            "argo-house-price-a2-fixture-close/v1", True, True, True,
            True, True, False, None, 2.25,
        )
        harness = SimpleNamespace(close=Mock(return_value=supplied))
        result = fixture_module._close_harness(harness)
        self.assertFalse(result.confirmed)
        self.assertEqual(result.error, "CLOSE_IDENTITY_UNKNOWN")
        self.assertEqual(result.elapsed_seconds, 0.0)

    def test_owned_close_late_completed_join_is_cached_timeout_not_confirmation(self) -> None:
        class LateButCompletedThread:
            def __init__(self, target, *, daemon, clock):
                self.target = target;self.daemon = daemon;self.clock = clock;self.alive = True
            def start(self):
                return None
            def join(self, timeout=None):
                self.clock.now += (0.0 if timeout is None else timeout) + 0.25
                self.target();self.alive = False
            def is_alive(self):
                return self.alive
        clock = FakeClock();serve = FakeServeThread();server = FakeServer(serve)
        harness = owned_harness_for_close(server, serve);created = []
        def factory(*, target, daemon):
            thread = LateButCompletedThread(target, daemon=daemon, clock=clock)
            created.append(thread);return thread
        with patch.object(fixture_module.threading, "Thread", side_effect=factory), \
             patch.object(fixture_module.time, "monotonic", side_effect=clock.monotonic):
            first = harness.close();second = harness.close()
        self.assertIs(first, second)
        self.assertFalse(first.confirmed)
        self.assertTrue(first.timed_out)
        self.assertEqual(first.error, "CLOSE_TIMEOUT")
        self.assertEqual(first.elapsed_seconds, 2.25)
        self.assertEqual(len(created), 1)
        self.assertEqual(server.shutdown_calls, 1)

    def test_owned_close_alive_serve_thread_uses_remaining_deadline_and_times_out(self) -> None:
        clock = FakeClock();serve = FakeServeThread(clock=clock)
        server = FakeServer(serve, stop_serve=False)
        harness = owned_harness_for_close(server, serve)
        def factory(*, target, daemon):
            return FakeCleanupThread(target, daemon=daemon, clock=clock, execute=True)
        with patch.object(fixture_module.threading, "Thread", side_effect=factory), \
             patch.object(fixture_module.time, "monotonic", side_effect=clock.monotonic):
            result = harness.close()
        self.assertFalse(result.confirmed)
        self.assertTrue(result.shutdown_completed)
        self.assertFalse(result.serve_thread_stopped)
        self.assertTrue(result.socket_closed)
        self.assertTrue(result.cleanup_thread_stopped)
        self.assertTrue(result.timed_out)
        self.assertEqual(result.error, "CLOSE_TIMEOUT")
        self.assertEqual(clock.now, 2.0)

    def test_owned_close_exception_and_open_socket_never_infer_confirmation(self) -> None:
        for case in ("exception", "open_socket"):
            with self.subTest(case=case):
                clock = FakeClock();serve = FakeServeThread()
                server = FakeServer(serve, fail=case == "exception", close_socket=case != "open_socket")
                harness = owned_harness_for_close(server, serve)
                def factory(*, target, daemon):
                    return FakeCleanupThread(target, daemon=daemon, clock=clock, execute=True)
                with patch.object(fixture_module.threading, "Thread", side_effect=factory), \
                     patch.object(fixture_module.time, "monotonic", side_effect=clock.monotonic):
                    result = harness.close()
                self.assertFalse(result.confirmed)
                self.assertFalse(result.timed_out)
                self.assertEqual(result.error, "CLOSE_FAILED")
                self.assertTrue(result.cleanup_thread_stopped)

    def test_config_collision_closes_once_and_preserves_collision(self) -> None:
        class CollidingHarness(FakeHarness):
            def __init__(self, base: Path, rows: int = 2) -> None:
                super().__init__(base, rows)
                (base / "bridge-config.json").write_text("collision")
        base = self.parent / "collision"
        with patch.object(fixture_module, "OwnedNativeHarness", CollidingHarness):
            with self.assertRaises(CombinationFixtureError):prepare_fixture(base)
        harness = FakeHarness.instances[-1]
        self.assertEqual(harness.close_calls, 1)
        self.assertEqual((base / "bridge-config.json").read_text(), "collision")


if __name__ == "__main__":
    unittest.main(verbosity=2)
