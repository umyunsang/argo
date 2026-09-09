"""Trusted study bridge. ORX owns runs; this file owns admission and custody.

No generated code or fitted pickle executes in this process. Caller-supplied
episode configuration must remain in the unmounted control directory.
"""
from __future__ import annotations

import argparse
import contextlib
import dataclasses
import fcntl
import hashlib
import json
import math
import os
import re
import signal
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from kernel_wrapper import load_config as load_kernel_config
from kernel_wrapper import remaining_cpu_seconds, release_resources, remaining_seconds, reserve_resources
from scoring import ContractError, canonical_config, canonical_json, content_sha256, file_sha256, read_prediction_json, score_private_labels

STUDY_ROOT = Path.home() / ".local/share/argo-study-20260909"
FIXED_COMMAND = "/opt/homebrew/bin/python3 runner.py"
UUID_PATTERN = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
BASELINE_SOURCE = b"from candidate_entry import baseline_fit\n\ndef fit(train_X, train_y, frozen_config):\n    return baseline_fit(train_X, train_y, frozen_config)\n"
RUNTIME_FILES = ("runner.py", "scientific_bridge.py", "candidate_entry.py", "scoring.py", "kernel_wrapper.py")
PUBLIC_KEYS = ("target_column", "feature_columns", "numeric_columns", "categorical_columns", "class_mapping", "classes")


class BridgeError(RuntimeError):
    pass


def safe_path(value: str, *, exists: bool = True) -> Path:
    path = Path(value)
    if not path.is_absolute() or any(char in value for char in (",", "\n", "\r", "\0")):
        raise BridgeError("INVALID_PATH")
    if path != path.resolve(strict=exists):
        raise BridgeError("NONCANONICAL_PATH")
    return path


def regular_bytes(path: Path, maximum: int) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > maximum:
            raise BridgeError("INVALID_ARTIFACT_FILE")
        data = stream.read(maximum + 1)
        if len(data) > maximum:
            raise BridgeError("ARTIFACT_TOO_LARGE")
        return data


def workspace_source(root: Path, relative: Path) -> bytes:
    """Traverse with directory descriptors so concurrent symlink swaps cannot escape."""
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in relative.parts[:-1]:
            next_directory = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = next_directory
        fd = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 262144:
                raise BridgeError("INVALID_SOURCE_FILE")
            data = stream.read(262145)
            if len(data) > 262144:
                raise BridgeError("SOURCE_TOO_LARGE")
            return data
    except OSError:
        raise BridgeError("SOURCE_UNAVAILABLE_OR_UNSAFE") from None
    finally:
        os.close(directory)


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex)
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(canonical_json(value) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


@dataclasses.dataclass(frozen=True)
class EpisodeConfig:
    workspace: Path
    custody_task_root: Path
    metadata: dict
    private_artifact_dir: Path
    kernel_config: Path
    projectId: str
    projectPath: Path
    image: str
    deadline_epoch: float
    orx_executable: str = str(Path.home() / ".local/bin/orx")
    parent_experiment_id: str | None = None
    feedback_limit: int = 12
    final_refit_limit: int = 1

    def to_json(self) -> dict:
        return {key: str(value) if isinstance(value, Path) else value for key, value in dataclasses.asdict(self).items()}


def load_episode_config(path: Path, *, study_root: Path = STUDY_ROOT) -> EpisodeConfig:
    path = safe_path(str(path))
    raw = json.loads(regular_bytes(path, 1024 * 1024))
    fields = {field.name for field in dataclasses.fields(EpisodeConfig)}
    selected = {key: value for key, value in raw.items() if key in fields}
    if isinstance(selected.get("metadata"), str):
        selected["metadata"] = json.loads(regular_bytes(safe_path(selected["metadata"]), 1024 * 1024))
    for key in ("workspace", "custody_task_root", "private_artifact_dir", "kernel_config", "projectPath"):
        selected[key] = safe_path(selected[key])
    cfg = EpisodeConfig(**selected)
    if not path.is_relative_to(cfg.workspace.parent / "control"):
        raise BridgeError("EPISODE_CONFIG_MUST_BE_PRIVATE")
    if not cfg.private_artifact_dir.is_relative_to(cfg.workspace.parent / "control"):
        raise BridgeError("ARTIFACT_CUSTODY_MUST_BE_PRIVATE")
    for directory in (cfg.workspace, cfg.custody_task_root, cfg.private_artifact_dir, cfg.projectPath):
        if not directory.is_relative_to(study_root.resolve()) or directory == study_root.resolve():
            raise BridgeError("OUTSIDE_DEDICATED_STUDY_ROOT")
    if cfg.projectPath.is_relative_to(cfg.workspace) or cfg.projectPath == cfg.workspace.parent:
        raise BridgeError("PUBLIC_PROJECT_REPOSITORY")
    if not re.fullmatch(UUID_PATTERN, cfg.projectId) or (cfg.parent_experiment_id and not re.fullmatch(UUID_PATTERN, cfg.parent_experiment_id)):
        raise BridgeError("INVALID_ORX_ID")
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", cfg.image):
        raise BridgeError("IMMUTABLE_IMAGE_REQUIRED")
    if not isinstance(cfg.deadline_epoch, (int, float)) or not math.isfinite(cfg.deadline_epoch):
        raise BridgeError("INVALID_DEADLINE")
    if cfg.feedback_limit != 12 or cfg.final_refit_limit != 1:
        raise BridgeError("STUDY_LIMITS_CHANGED")
    canonical_config(cfg.metadata)
    return cfg


@dataclasses.dataclass(frozen=True)
class CommandResult:
    code: int
    stdout: str
    stderr: str


def command(argv: list[str], *, cwd: Path, timeout: float = 30, maximum: int = 262144, new_session: bool = True) -> CommandResult:
    """Bound both output and time; never evaluate argv through a shell."""
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=new_session)
        deadline = time.monotonic() + max(0.1, timeout)
        try:
            while process.poll() is None:
                if time.monotonic() >= deadline or os.fstat(stdout.fileno()).st_size + os.fstat(stderr.fileno()).st_size > maximum:
                    raise BridgeError("COMMAND_UNCERTAIN")
                time.sleep(0.05)
            if os.fstat(stdout.fileno()).st_size + os.fstat(stderr.fileno()).st_size > maximum:
                raise BridgeError("COMMAND_OUTPUT_LIMIT")
            stdout.seek(0)
            stderr.seek(0)
            return CommandResult(process.returncode, stdout.read().decode("utf-8"), stderr.read().decode("utf-8"))
        finally:
            if process.poll() is None:
                if new_session:
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait(timeout=5)


def _fields(text: str) -> dict[str, str]:
    pairs = re.findall(r"^  (id|title|slug|branch|command|last run|commit): +(.+)$", text, re.MULTILINE)
    if len(pairs) != len({key for key, _ in pairs}):
        raise BridgeError("ORX_OUTPUT_UNRECOGNIZED")
    return dict(pairs)


def parse_created(text: str, title: str) -> tuple[str, str]:
    fields = _fields(text)
    if (not text.startswith(("✓ Created local baseline experiment\n", "✓ Created local child experiment\n"))
            or fields.get("title") != title or fields.get("command") != FIXED_COMMAND
            or not re.fullmatch(UUID_PATTERN, fields.get("id", ""))
            or not re.fullmatch(r"orx/[a-z0-9]+(?:-[a-z0-9]+)*", fields.get("branch", ""))):
        raise BridgeError("ORX_OUTPUT_UNRECOGNIZED")
    return fields["id"], fields["branch"]


def parse_status(text: str, experiment_id: str) -> dict:
    fields = _fields(text)
    if fields.get("id") != experiment_id or fields.get("command") != FIXED_COMMAND:
        raise BridgeError("ORX_IDENTITY_MISMATCH")
    if fields.get("last run") == "— (never run)":
        return {"branch": fields["branch"], "run_id": None}
    match = re.fullmatch(r"(" + UUID_PATTERN + r") \((starting|running|done|failed|cancelled), commit ([0-9a-f]{7}), ran .+, updated .+\)", fields.get("last run", ""))
    commit = fields.get("commit", "")
    if match is None or not re.fullmatch(r"[a-f0-9]{40}", commit) or not commit.startswith(match[3]):
        raise BridgeError("ORX_OUTPUT_UNRECOGNIZED")
    return {"branch": fields["branch"], "run_id": match[1], "status": match[2], "commit": commit}


class ORXBackend:
    def __init__(self, cfg: EpisodeConfig):
        self.cfg = cfg

    def call(self, args: list[str], *, timeout: float = 30, allow_failure: bool = False) -> CommandResult:
        result = command([self.cfg.orx_executable, *args, "--no-telemetry"], cwd=self.cfg.projectPath, timeout=timeout)
        if result.code and not allow_failure:
            raise BridgeError("ORX_OPERATION_UNCERTAIN")
        return result

    def git(self, args: list[str], cwd: Path | None = None) -> str:
        result = command(["git", *args], cwd=cwd or self.cfg.projectPath)
        if result.code:
            raise BridgeError("PRIVATE_GIT_OPERATION_FAILED")
        return result.stdout.strip()

    def run(self, spec: dict, source: bytes, event) -> dict:
        if self.git(["rev-parse", "--show-toplevel"]) != str(self.cfg.projectPath):
            raise BridgeError("WRONG_PRIVATE_REPOSITORY")
        if self.git(["remote"]):
            raise BridgeError("PRIVATE_REPOSITORY_HAS_REMOTE")
        if spec.get("parent_commit"):
            parent = parse_status(self.call(["exp", "status", spec["parent_experiment_id"]]).stdout, spec["parent_experiment_id"])
            if parent.get("commit") != spec["parent_commit"] or parent.get("status") not in {"done", "failed", "cancelled"}:
                raise BridgeError("OBSERVED_PARENT_CHANGED")
        title = "study-" + spec["kind"] + "-" + spec["intent_id"][:16]
        args = ["create-experiment", self.cfg.projectId, "--title", title, "--description", spec["hypothesis"]]
        if spec["parent_experiment_id"]:
            args += ["--parent", spec["parent_experiment_id"]]
        created = self.call(args)
        experiment_id, branch = parse_created(created.stdout, title)
        event({"experiment_id": experiment_id, "branch": branch, "phase": "CREATED"})
        observed = parse_status(self.call(["exp", "status", experiment_id]).stdout, experiment_id)
        if observed["run_id"] is not None or observed["branch"] != branch:
            raise BridgeError("ORX_NODE_ALREADY_RAN")
        if self.call(["runs", self.cfg.projectId, "--experiment", experiment_id]).stdout.strip() != "No runs found.":
            raise BridgeError("ORX_NODE_ALREADY_RAN")
        worktree = self.cfg.private_artifact_dir / ("worktree-" + spec["intent_id"])
        self.git(["worktree", "add", str(worktree), branch])
        if spec.get("parent_commit") and self.git(["rev-parse", "HEAD"], worktree) != spec["parent_commit"]:
            raise BridgeError("CHILD_PARENT_COMMIT_MISMATCH")
        if self.git(["status", "--porcelain", "--untracked-files=all"], worktree):
            raise BridgeError("PRIVATE_WORKTREE_DIRTY")
        spec = {**spec, "experiment_id": experiment_id}
        files = {name: (Path(__file__).parent / name).read_bytes() for name in RUNTIME_FILES}
        files.update({"solution.py": source, "config.json": (canonical_json(spec["config"]) + "\n").encode(),
                      "public.json": (canonical_json(spec["public_schema"]) + "\n").encode(),
                      "node-spec.json": (canonical_json(spec) + "\n").encode()})
        for name, data in files.items():
            (worktree / name).write_bytes(data)
        self.git(["add", "--", *files], worktree)
        self.git(["-c", "user.name=Study Apparatus", "-c", "user.email=study@localhost", "commit", "-m", title], worktree)
        commit = self.git(["rev-parse", "HEAD"], worktree)
        if self.git(["status", "--porcelain", "--untracked-files=all"], worktree):
            raise BridgeError("PRIVATE_WORKTREE_DIRTY")
        event({"commit": commit, "phase": "LAUNCH_INTENT", "spec_sha256": content_sha256(spec)})
        launch = self.call(["exp", "run", experiment_id, "--backend", "local"])
        matches = re.findall(r"^  run  (" + UUID_PATTERN + r")$", launch.stdout, re.MULTILINE)
        if len(matches) != 1:
            raise BridgeError("ORX_LAUNCH_UNCERTAIN")
        run_id = matches[0]
        event({"run_id": run_id, "phase": "RUNNING"})
        while True:
            status_text = self.call(["exp", "status", experiment_id]).stdout
            status = parse_status(status_text, experiment_id)
            if status.get("run_id") != run_id or status.get("commit") != commit or status["branch"] != branch:
                raise BridgeError("ORX_RUNNING_IDENTITY_MISMATCH")
            rows = self.call(["runs", self.cfg.projectId, "--experiment", experiment_id]).stdout
            pattern = re.escape(run_id) + r" {2,}(starting|running|done|failed|cancelled) {2,}" + re.escape(title) + r" {2,}" + commit[:7] + r" {2,}"
            row_states = re.findall(pattern, rows)
            with (self.cfg.private_artifact_dir / ("orx-observations-" + spec["intent_id"] + ".jsonl")).open("a") as stream:
                stream.write(canonical_json({"at": time.time(), "status": status, "run_list_states": row_states}) + "\n")
            if len(row_states) != 1:
                raise BridgeError("ORX_RUNS_DISAGREE")
            if status["status"] in {"done", "failed", "cancelled"} and row_states[0] == status["status"]:
                break
            remaining = self.cfg.deadline_epoch - time.time()
            if remaining <= 0:
                self.call(["exp", "cancel", experiment_id], allow_failure=True)
                raise BridgeError("ORX_DEADLINE_RECONCILIATION_REQUIRED")
            self.call(["exp", "wait", experiment_id, "--interval", "1", "--timeout", "2"], timeout=min(remaining + 2, 5), allow_failure=True)
        log_deadline = min(self.cfg.deadline_epoch, time.time() + 10)
        while True:
            logs = self.call(["logs", run_id, "--head", "--bytes", "65536"])
            window = re.fullmatch(r"\[local file\] bytes 0–([0-9]+) of ([0-9]+)\n", logs.stderr)
            lines = [line for line in logs.stdout.splitlines() if line.strip()]
            with (self.cfg.private_artifact_dir / ("orx-log-observations-" + spec["intent_id"] + ".jsonl")).open("a") as stream:
                stream.write(canonical_json({"at": time.time(), "line_count": len(lines), "stdout_bytes": len(logs.stdout.encode()), "stdout_sha256": hashlib.sha256(logs.stdout.encode()).hexdigest(), "window": logs.stderr}) + "\n")
            if window is None or window[1] != window[2]:
                raise BridgeError("ORX_LOG_INCOMPLETE")
            if len(logs.stdout.encode("utf-8")) not in {int(window[1]), int(window[1]) + 1}:
                raise BridgeError("ORX_LOG_LENGTH_MISMATCH")
            if not lines and window[2] == "0" and time.time() < log_deadline:
                time.sleep(0.2)
                continue
            if len(lines) != 1:
                raise BridgeError("ORX_LOG_NOT_SAFE_RECEIPT")
            break
        receipt = json.loads(lines[0])
        if receipt.get("spec_sha256") != content_sha256(spec) or receipt.get("intent_id") != spec["intent_id"]:
            raise BridgeError("ORX_RECEIPT_IDENTITY_MISMATCH")
        if status["status"] != "done" and receipt.get("status") != "UNKNOWN":
            raise BridgeError("ORX_STATUS_RECEIPT_DISAGREE")
        return {**receipt, "experiment_id": experiment_id, "run_id": run_id, "commit": commit}


class ScientificBridge:
    def __init__(self, cfg: EpisodeConfig, backend=None):
        self.cfg = cfg
        self.backend = backend or ORXBackend(cfg)
        self.state_path = cfg.private_artifact_dir / "bridge-state.json"

    @contextlib.contextmanager
    def state(self):
        fd = os.open(self.cfg.private_artifact_dir / "bridge.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "r+") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise BridgeError("SCIENTIFIC_TOOL_BUSY") from None
            value = json.loads(regular_bytes(self.state_path, 1024 * 1024)) if self.state_path.exists() else {
                "schema": "study-bridge-state/v1", "config_sha256": content_sha256(self.cfg.to_json()),
                "candidates": [], "default": None, "locked": None, "final_refits": 0, "halted": False,
            }
            if value["config_sha256"] != content_sha256(self.cfg.to_json()):
                raise BridgeError("EPISODE_CONFIG_CHANGED")
            yield value

    def save(self, state: dict) -> None:
        atomic_json(self.state_path, state)

    def initialize(self) -> dict:
        return self._candidate(BASELINE_SOURCE, canonical_config(self.cfg.metadata), "Establish the frozen RF100 starting artifact", None, baseline=True)

    def run_candidate(self, relative_source: str = "solution.py", config: dict | None = None,
                      hypothesis: str = "", parent_experiment_id: str | None = None) -> dict:
        relative = Path(relative_source)
        if relative.is_absolute() or ".." in relative.parts or relative.suffix != ".py":
            raise BridgeError("INVALID_RELATIVE_SOURCE")
        source = workspace_source(self.cfg.workspace, relative)
        return self._candidate(source, {} if config is None else config, hypothesis, parent_experiment_id, baseline=False)

    def _candidate(self, source: bytes, config: dict, hypothesis: str, parent: str | None, *, baseline: bool) -> dict:
        if not isinstance(config, dict) or len(canonical_json(config)) > 65536:
            raise BridgeError("INVALID_FROZEN_CONFIG")
        if not isinstance(hypothesis, str) or not hypothesis.strip() or len(hypothesis) > 4000 or "\0" in hypothesis:
            raise BridgeError("HYPOTHESIS_REQUIRED")
        public = {key: self.cfg.metadata[key] for key in PUBLIC_KEYS}
        hashes = {name: file_sha256(Path(__file__).parent / name) for name in RUNTIME_FILES}
        recipe = {"source_sha256": hashlib.sha256(source).hexdigest(), "config": config, "public_schema": public,
                  "seed": 20260909, "image": self.cfg.image, "runtime_sha256": hashes}
        request_id = content_sha256(recipe)
        with self.state() as state:
            previous = next((item for item in state["candidates"] if item["request_id"] == request_id), None)
            if previous:
                return previous.get("receipt", {"status": "UNKNOWN", "candidate_id": previous["candidate_id"], "reason": "RECONCILE_EXISTING_INTENT"})
            if state["halted"] or any(item["status"] == "PENDING" for item in state["candidates"]):
                raise BridgeError("UNKNOWN_RUN_REQUIRES_RECONCILIATION")
            if state["locked"]:
                raise BridgeError("FINAL_SELECTION_CLOSED")
            if not baseline and not state["default"]:
                raise BridgeError("BASELINE_REQUIRED")
            if len(state["candidates"]) >= 12:
                raise BridgeError("FEEDBACK_EXHAUSTED")
            if time.time() >= self.cfg.deadline_epoch - 600:
                raise BridgeError("FINAL_WALL_RESERVE")
            observed = [item for item in state["candidates"] if item["status"] in {"VALID", "AGENT_INVALID"}]
            if parent is None:
                parent = observed[-1].get("experiment_id") if observed else self.cfg.parent_experiment_id
            allowed = {item.get("experiment_id") for item in observed}
            if baseline:
                allowed.add(self.cfg.parent_experiment_id)
            if parent not in allowed and (parent is not None or state["candidates"]):
                raise BridgeError("PARENT_NOT_OBSERVED")
            candidate_id = "c-" + request_id[:20]
            intent_id = uuid.uuid4().hex
            directory = self.cfg.private_artifact_dir / candidate_id
            directory.mkdir(mode=0o700)
            (directory / "solution.py").write_bytes(source)
            atomic_json(directory / "recipe.json", recipe)
            item = {"candidate_id": candidate_id, "request_id": request_id, "intent_id": intent_id,
                    "status": "PENDING", "phase": "ADMITTED", "hypothesis": hypothesis, "parent_experiment_id": parent}
            state["candidates"].append(item)
            if baseline:
                state["default"] = candidate_id
            self.save(state)
            spec = {"schema": "study-node-spec/v1", "kind": "candidate", "candidate_id": candidate_id,
                    "intent_id": intent_id, "hypothesis": hypothesis, "parent_experiment_id": parent,
                    "parent_commit": next((ancestor.get("commit") for ancestor in observed if ancestor.get("experiment_id") == parent), None),
                    "episode": self.cfg.to_json(), **recipe}
            def event(update: dict) -> None:
                item.update(update)
                self.save(state)
            try:
                result = self.backend.run(spec, source, event)
                if result.get("status") not in {"VALID", "AGENT_INVALID", "UNKNOWN"}:
                    raise BridgeError("INVALID_RUN_RECEIPT")
                receipt = {key: result[key] for key in ("status", "balanced_accuracy", "experiment_id", "run_id", "commit", "reason") if key in result}
                receipt.update(candidate_id=candidate_id, feedback_slot=len(state["candidates"]), recipe_sha256=request_id)
                if receipt["status"] == "VALID" and (type(receipt.get("balanced_accuracy")) not in (int, float) or not 0 <= receipt["balanced_accuracy"] <= 1):
                    raise BridgeError("INVALID_SCORE_RECEIPT")
            except Exception as exc:
                receipt = {"status": "UNKNOWN", "candidate_id": candidate_id, "reason": "RUN_RECONCILIATION_REQUIRED", "feedback_slot": len(state["candidates"])}
                item["host_diagnostic"] = str(exc) if isinstance(exc, BridgeError) and re.fullmatch(r"[A-Z_]+", str(exc)) else "UNEXPECTED_HOST_ERROR"
            item.update(status=receipt["status"], receipt=receipt)
            if item["status"] == "UNKNOWN":
                state["halted"] = True
            self.save(state)
            return receipt

    def list_results(self) -> dict:
        with self.state() as state:
            return {"results": [item.get("receipt", {"status": "UNKNOWN", "candidate_id": item["candidate_id"]}) for item in state["candidates"]],
                    "feedback_used": len(state["candidates"]), "feedback_limit": 12, "default": state["default"],
                    "locked": state["locked"], "halted": state["halted"]}

    def read_candidate(self, candidate_id: str, kind: str = "source", offset: int = 0, length: int = 4000) -> dict:
        if kind not in {"source", "config"} or type(offset) is not int or offset < 0 or type(length) is not int or not 1 <= length <= 4000:
            raise BridgeError("INVALID_CANDIDATE_READ")
        with self.state() as state:
            item = next((row for row in state["candidates"] if row["candidate_id"] == candidate_id and row["status"] in {"VALID", "AGENT_INVALID"}), None)
            if item is None:
                raise BridgeError("CANDIDATE_NOT_OBSERVED")
            directory = self.cfg.private_artifact_dir / candidate_id
            recipe = json.loads(regular_bytes(directory / "recipe.json", 1048576))
            if content_sha256(recipe) != item["request_id"]:
                raise BridgeError("CANDIDATE_RECIPE_CHANGED")
            if kind == "source":
                data = regular_bytes(directory / "solution.py", 262144)
                if hashlib.sha256(data).hexdigest() != recipe["source_sha256"]:
                    raise BridgeError("CANDIDATE_SOURCE_CHANGED")
                text = data.decode("utf-8")
            else:
                text = canonical_json(recipe["config"])
            return {"candidate_id": candidate_id, "kind": kind, "offset": offset, "total_characters": len(text),
                    "text": text[offset:offset + length], "source_sha256": recipe["source_sha256"],
                    "recipe_sha256": item["request_id"]}

    def lock_candidate(self, candidate_id: str) -> dict:
        with self.state() as state:
            if state["halted"]:
                raise BridgeError("UNKNOWN_RUN_REQUIRES_RECONCILIATION")
            if state["locked"] is not None:
                if state["locked"] != candidate_id:
                    raise BridgeError("FINAL_SELECTION_CLOSED")
                return {"status": "FINAL_LOCKED", "candidate_id": candidate_id}
            selected = next((item for item in state["candidates"] if item["candidate_id"] == candidate_id and item["status"] == "VALID"), None)
            if selected is None:
                raise BridgeError("UNVERIFIED_FINAL_CANDIDATE")
            state["locked"] = candidate_id
            self.save(state)
            return {"status": "FINAL_LOCKED", "candidate_id": candidate_id}

    def finalize(self) -> dict:
        with self.state() as state:
            if state["halted"]:
                raise BridgeError("UNKNOWN_RUN_REQUIRES_RECONCILIATION")
            if state["final_refits"]:
                return {"status": "FINAL_WITHHELD", "candidate_id": state["locked"]}
            state["locked"] = state["locked"] or state["default"]
            item = next((item for item in state["candidates"] if item["candidate_id"] == state["locked"]), None)
            if item is None:
                raise BridgeError("NO_DEFAULT_CANDIDATE")
            state["final_refits"] = 1
            state["final_intent_id"] = uuid.uuid4().hex
            self.save(state)
            directory = self.cfg.private_artifact_dir / item["candidate_id"]
            recipe = json.loads(regular_bytes(directory / "recipe.json", 1048576))
            source = regular_bytes(directory / "solution.py", 262144)
            if content_sha256(recipe) != item["request_id"] or hashlib.sha256(source).hexdigest() != recipe["source_sha256"]:
                state["halted"] = True
                self.save(state)
                raise BridgeError("LOCKED_RECIPE_CHANGED")
            spec = {"schema": "study-node-spec/v1", "kind": "final", "candidate_id": item["candidate_id"],
                    "intent_id": state["final_intent_id"], "hypothesis": "Refit the locked recipe once on outer train", "parent_experiment_id": item.get("experiment_id"),
                    "parent_commit": item.get("commit"),
                    "episode": self.cfg.to_json(), **recipe}
            def event(update: dict) -> None:
                state.setdefault("final_lifecycle", {}).update(update)
                self.save(state)
            try:
                receipt = self.backend.run(spec, source, event)
            except Exception:
                receipt = {"status": "UNKNOWN", "reason": "FINAL_RUN_RECONCILIATION_REQUIRED"}
            atomic_json(self.cfg.private_artifact_dir / "final-private-receipt.json", receipt)
            state["final_status"] = receipt.get("status", "UNKNOWN")
            state["halted"] = state["final_status"] == "UNKNOWN"
            self.save(state)
            return {"status": "FINAL_WITHHELD", "candidate_id": state["locked"]}


def docker_argv(kernel, name: str, app: Path, output: Path, inputs: dict[str, Path], stage: str) -> list[str]:
    if stage not in {"fit", "predict"} or set(inputs) != ({"train.csv"} if stage == "fit" else {"features.csv", "model.joblib"}):
        raise BridgeError("INVALID_SANDBOX_INPUTS")
    args = [kernel.docker, "run", "--rm", "--init", "--name", name, "--network", "none", "--read-only",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--user", f"{os.getuid()}:{os.getgid()}",
            "--cpus", "1.5", "--memory", "4294967296", "--memory-swap", "4294967296", "--pids-limit", str(kernel.pids_limit),
            "--ulimit", "fsize=536870912:536870912", "--ulimit", "nofile=256:256",
            "--stop-timeout", "1", "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=268435456,mode=1777", "--workdir", "/app",
            "--env", "HOME=/tmp", "--env", "PYTHONDONTWRITEBYTECODE=1", "--env", "OPENBLAS_NUM_THREADS=1",
            "--env", "OMP_NUM_THREADS=1", "--env", "MKL_NUM_THREADS=1", "--entrypoint", "python"]
    for source, target, readonly in [(app, "/app", True), (output, "/output", False)] + [(value, "/data/" + key, True) for key, value in sorted(inputs.items())]:
        safe_path(str(source))
        args += ["--mount", f"type=bind,src={source},dst={target}" + (",readonly" if readonly else "")]
    return args + [kernel.image, "/app/candidate_entry.py", stage]


def run_sandbox(kernel_path: Path, app: Path, output: Path, inputs: dict[str, Path], stage: str, *, final: bool) -> None:
    cfg = load_kernel_config(kernel_path)
    if not final and (cfg.deadline_epoch - time.time() <= 600 or remaining_cpu_seconds(cfg) <= 900):
        raise BridgeError("FINAL_RESERVE_REACHED")
    name = "argo-fit-" + uuid.uuid4().hex
    try:
        lease = reserve_resources(cfg, name, 1.5, 4 * 1024**3, kind="fit")
    except RuntimeError:
        raise BridgeError("CANDIDATE_RESOURCE_ADMISSION_DENIED") from None
    record = cfg.control_dir / (name + ".json")
    atomic_json(record, {"container": name, "wrapper_pid": os.getpid(), "lease": lease})
    watcher = subprocess.Popen([sys.executable, str(Path(__file__).parent / "kernel_wrapper.py"), "--watchdog", str(kernel_path), str(os.getpid()), name, lease],
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    process = None
    reason = "completed"
    try:
        process = subprocess.Popen(docker_argv(cfg, name, app, output, inputs, stage), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        atomic_json(record, {"container": name, "wrapper_pid": os.getpid(), "docker_cli_pid": process.pid, "lease": lease})
        while process.poll() is None:
            output_files = list(output.iterdir())
            output_stats = []
            for path in output_files:
                with contextlib.suppress(FileNotFoundError):
                    output_stats.append(path.lstat())
            if any(not stat.S_ISREG(info.st_mode) for info in output_stats):
                raise BridgeError("INVALID_ARTIFACT_FILE")
            if len(output_files) > 8 or sum(info.st_size for info in output_stats) > 536870912:
                reason = "output_limit"
                raise BridgeError("ARTIFACT_TOO_LARGE")
            if remaining_seconds(cfg) <= 0 or (not final and (cfg.deadline_epoch - time.time() <= 600 or remaining_cpu_seconds(cfg) <= 900)):
                reason = "budget"
                raise BridgeError("CANDIDATE_BUDGET_EXHAUSTED")
            time.sleep(0.1)
        if process.returncode:
            reason = "candidate_failure"
            raise BridgeError("CANDIDATE_EXECUTION_FAILED")
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        command([cfg.docker, "rm", "--force", name], cwd=app, timeout=10)
        listing = command([cfg.docker, "container", "ls", "--all", "--quiet", "--filter", f"name=^/{name}$"], cwd=app, timeout=10)
        confirmed = listing.code == 0 and not listing.stdout.strip()
        atomic_json(cfg.control_dir / (name + ".completion.json"), {"container_removed": confirmed, "reason": reason, "lease": lease})
        if confirmed:
            release_resources(cfg, lease, reason=reason)
            watcher.terminate()
            watcher.wait(timeout=5)
        else:
            raise BridgeError("CONTAINER_CLEANUP_UNKNOWN")


def execute_spec(snapshot: Path, sandbox=run_sandbox) -> dict:
    spec = json.loads(regular_bytes(snapshot / "node-spec.json", 2 * 1024 * 1024))
    identity = {"schema": "study-run-receipt/v1", "spec_sha256": content_sha256(spec), "intent_id": spec.get("intent_id"), "kind": spec.get("kind")}
    if spec.get("kind") == "episode":
        try:
            expected_files = set(RUNTIME_FILES) | {"controller.ts", "model_meter.ts"}
            if not isinstance(spec.get("runtime_sha256"), dict) or set(spec["runtime_sha256"]) != expected_files:
                raise BridgeError("EPISODE_RUNTIME_MANIFEST_INCOMPLETE")
            for name in sorted(expected_files):
                runtime_path = safe_path(str(snapshot / name))
                if hashlib.sha256(regular_bytes(runtime_path, 1048576)).hexdigest() != spec["runtime_sha256"][name]:
                    raise BridgeError("EPISODE_RUNTIME_CHANGED")
            config_path = safe_path(spec["episode_config"])
            config_bytes = regular_bytes(config_path, 1048576)
            if hashlib.sha256(config_bytes).hexdigest() != spec.get("episode_config_sha256"):
                raise BridgeError("EPISODE_CONFIG_CHANGED")
            cfg = load_episode_config(config_path)
            if regular_bytes(config_path, 1048576) != config_bytes:
                raise BridgeError("EPISODE_CONFIG_CHANGED")
            result = command(["/opt/homebrew/bin/node", str(snapshot / "controller.ts"), str(config_path)], cwd=snapshot,
                             timeout=max(1, cfg.deadline_epoch - time.time() + 30), maximum=1048576, new_session=False)
            summary = json.loads(result.stdout)
            if result.code or not isinstance(summary, dict) or summary.get("schema") != "study-episode-summary/v1":
                raise ValueError
        except BridgeError as exc:
            return {**identity, "status": "UNKNOWN", "reason": str(exc)}
        except (KeyError, OSError, TypeError):
            return {**identity, "status": "UNKNOWN", "reason": "EPISODE_AUTHENTICATION_FAILED"}
        except ValueError:
            return {**identity, "status": "UNKNOWN", "reason": "EPISODE_SUMMARY_UNAVAILABLE"}
        status = summary.get("status")
        status = status if status in ("VALID", "AGENT_INVALID") else "UNKNOWN"
        return {**identity, "status": status, "episode_summary": summary}
    try:
        if spec.get("kind") not in {"candidate", "final"}:
            raise BridgeError("UNKNOWN_SPEC_KIND")
        for name in RUNTIME_FILES:
            if file_sha256(snapshot / name) != spec["runtime_sha256"][name]:
                raise BridgeError("RUNTIME_CHANGED")
        if hashlib.sha256(regular_bytes(snapshot / "solution.py", 262144)).hexdigest() != spec["source_sha256"]:
            raise BridgeError("SOURCE_CHANGED")
        if json.loads(regular_bytes(snapshot / "config.json", 65536)) != spec["config"]:
            raise BridgeError("CONFIG_CHANGED")
        cfg_raw = spec["episode"]
        kernel_path = safe_path(cfg_raw["kernel_config"])
        kernel = load_kernel_config(kernel_path)
        if kernel.image != spec["image"] or kernel.deadline_epoch != cfg_raw["deadline_epoch"]:
            raise BridgeError("EPISODE_RUNTIME_CHANGED")
        if kernel.max_cpu_seconds > 7200 or kernel.deadline_epoch > time.time() + 5400:
            raise BridgeError("EPISODE_BUDGET_EXCEEDS_DESIGN")
        private = safe_path(cfg_raw["private_artifact_dir"])
        if not private.is_relative_to(kernel.control_dir):
            raise BridgeError("PUBLIC_OUTPUT_DIRECTORY")
        custody = safe_path(cfg_raw["custody_task_root"])
        output = private / ("run-" + spec["intent_id"])
        output.mkdir(mode=0o700)
        app = output / "app"
        app.mkdir(mode=0o700)
        for name in ("candidate_entry.py", "solution.py", "config.json", "public.json"):
            (app / name).write_bytes(regular_bytes(snapshot / name, 1024 * 1024))
        if json.loads((app / "public.json").read_text()) != spec["public_schema"]:
            raise BridgeError("PUBLIC_SCHEMA_CHANGED")
        fit_output = output / "fit"
        predict_output = output / "predict"
        fit_output.mkdir(mode=0o700)
        predict_output.mkdir(mode=0o700)
        final = spec["kind"] == "final"
        train = custody / ("outer_train.csv" if final else "inner_train.csv")
        features_path = custody / ("test_X.csv" if final else "dev_X.csv")
        labels = custody / ("test_y.csv" if final else "dev_y.csv")
        for path in (train, features_path, labels):
            if file_sha256(path) != cfg_raw["metadata"]["files_sha256"][path.name]:
                raise BridgeError("CUSTODY_INPUT_CHANGED")
        sandbox(kernel_path, app, fit_output, {"train.csv": train}, "fit", final=final)
        try:
            regular_bytes(fit_output / "model.joblib", 512 * 1024 * 1024)
        except OSError:
            raise BridgeError("INVALID_ARTIFACT_FILE") from None
        sandbox(kernel_path, app, predict_output, {"model.joblib": fit_output / "model.joblib", "features.csv": features_path}, "predict", final=final)
        try:
            prediction_bytes = regular_bytes(predict_output / "predictions.json", 1024 * 1024)
        except OSError:
            raise BridgeError("INVALID_ARTIFACT_FILE") from None
        expected_rows = cfg_raw["metadata"]["row_counts"]["test" if final else "dev"]
        predicted = read_prediction_json(predict_output / "predictions.json", expected_rows, spec["public_schema"]["classes"])
        score = score_private_labels(predicted, labels, expected_rows=expected_rows, classes=spec["public_schema"]["classes"], target_column=spec["public_schema"]["target_column"])
        return {**identity, **score, "candidate_id": spec["candidate_id"], "source_sha256": spec["source_sha256"],
                "config_sha256": content_sha256(spec["config"]), "prediction_sha256": hashlib.sha256(prediction_bytes).hexdigest(),
                "fitted_sha256": file_sha256(fit_output / "model.joblib"), "image": spec["image"]}
    except BridgeError as exc:
        agent_errors = {"CANDIDATE_EXECUTION_FAILED", "CANDIDATE_BUDGET_EXHAUSTED", "CANDIDATE_RESOURCE_ADMISSION_DENIED", "FINAL_RESERVE_REACHED", "INVALID_ARTIFACT_FILE", "ARTIFACT_TOO_LARGE"}
        return {**identity, "status": "AGENT_INVALID" if str(exc) in agent_errors else "UNKNOWN", "reason": str(exc)}
    except ContractError:
        return {**identity, "status": "AGENT_INVALID", "reason": "INVALID_PREDICTION_VECTOR"}
    except Exception:
        return {**identity, "status": "UNKNOWN", "reason": "TRUSTED_RUN_FAILURE"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode-config", type=Path, required=True)
    parser.add_argument("action", choices=("initialize", "run_candidate", "list_results", "read_candidate", "lock_candidate", "finalize"))
    args = parser.parse_args()
    raw = sys.stdin.buffer.read(65537)
    try:
        if len(raw) > 65536:
            raise BridgeError("ARGUMENTS_TOO_LARGE")
        arguments = json.loads(raw or b"{}")
        if not isinstance(arguments, dict):
            raise BridgeError("INVALID_ARGUMENTS")
        bridge = ScientificBridge(load_episode_config(args.episode_config))
        result = getattr(bridge, args.action)(**arguments)
    except BridgeError as exc:
        result = {"status": "REJECTED", "reason": str(exc)}
    except Exception:
        result = {"status": "UNKNOWN", "reason": "TRUSTED_BRIDGE_FAILURE"}
    print(canonical_json(result), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
