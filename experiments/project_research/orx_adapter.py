"""Research-local ORX references and idempotent submission, without a scheduler.

ORX remains the owner of execution, status and logs. A durable submission intent
closes the checkpoint-to-launch gap: an ambiguous submission is reconciled,
never automatically repeated. Keep intent files outside worker mounts.
"""
from __future__ import annotations

import base64
import contextlib
from dataclasses import asdict, dataclass
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.parse
import urllib.request
import uuid


UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
STATES = {"starting", "running", "done", "failed", "cancelled"}
ACTIVE = {"starting", "running"}


class OrxError(RuntimeError):
    pass


@dataclass(frozen=True)
class RunReference:
    project_id: str
    experiment_id: str
    run_id: str
    commit_sha: str
    command: str
    status: str
    source_digest: str
    created_at_ms: int
    ended_at_ms: int | None


def _identifier(value: str) -> str:
    if not isinstance(value, str) or re.fullmatch(UUID, value) is None:
        raise OrxError("INVALID_ORX_ID")
    return value


def _write(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


@contextlib.contextmanager
def _locked(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.parent != path.parent.resolve() or path.is_symlink():
        raise OrxError("INTENT_PATH_NOT_CANONICAL")
    fd = os.open(path.with_suffix(path.suffix + ".lock"),
                 os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "r+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


class OrxAdapter:
    def __init__(self, project_id: str, fixed_command: str, *,
                 base_url: str = "http://127.0.0.1:4837",
                 executable: str = "/Users/um-yunsang/.local/bin/orx"):
        self.project_id = _identifier(project_id)
        if not fixed_command or any(c in fixed_command for c in "\n\r\0"):
            raise OrxError("INVALID_FIXED_COMMAND")
        parsed = urllib.parse.urlsplit(base_url)
        if (parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
                or parsed.username or parsed.password or parsed.path not in {"", "/"}
                or parsed.query or parsed.fragment or parsed.port is None):
            raise OrxError("LOOPBACK_ORX_URL_REQUIRED")
        if not Path(executable).is_absolute():
            raise OrxError("ABSOLUTE_ORX_EXECUTABLE_REQUIRED")
        self.fixed_command = fixed_command
        self.base_url = base_url.rstrip("/")
        self.executable = executable

    def _get(self, route: str) -> dict:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                raise OrxError("ORX_REDIRECT_REFUSED")
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        with opener.open(self.base_url + route, timeout=10) as response:
            raw = response.read(4 * 1024 * 1024 + 1)
        if len(raw) > 4 * 1024 * 1024:
            raise OrxError("ORX_RESPONSE_TOO_LARGE")
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise OrxError("ORX_RESPONSE_INVALID")
        return result

    def _launch(self, experiment_id: str) -> str:
        result = subprocess.run([self.executable, "--no-telemetry", "exp", "run",
                                 experiment_id, "--backend", "local"],
                                capture_output=True, text=True, timeout=30, check=False)
        if result.returncode != 0:
            raise OrxError("ORX_LAUNCH_UNCONFIRMED")
        match = re.search(r"^  run  (" + UUID + r")$", result.stdout, re.MULTILINE)
        if not match:
            raise OrxError("ORX_LAUNCH_RESPONSE_UNKNOWN")
        return match[1]

    def verify_experiment(self, experiment_id: str) -> dict:
        _identifier(experiment_id)
        experiments = self._get(f"/api/projects/{self.project_id}/experiments").get("experiments")
        if not isinstance(experiments, list):
            raise OrxError("ORX_EXPERIMENT_LIST_INVALID")
        matches = [value for value in experiments if isinstance(value, dict) and value.get("id") == experiment_id]
        if len(matches) != 1:
            raise OrxError("ORX_EXPERIMENT_NOT_UNIQUE")
        value = matches[0]
        if value.get("projectId") != self.project_id or value.get("runCommand") != self.fixed_command:
            raise OrxError("ORX_FIXED_CONTRACT_MISMATCH")
        return value

    def _verify_commit(self, experiment_id: str, expected: str) -> None:
        experiment = self.verify_experiment(experiment_id)
        projects = self._get("/api/projects").get("projects")
        if not isinstance(projects, list):
            raise OrxError("ORX_PROJECT_LIST_INVALID")
        matches = [value for value in projects if isinstance(value, dict) and value.get("id") == self.project_id]
        if len(matches) != 1:
            raise OrxError("ORX_PROJECT_NOT_UNIQUE")
        path = Path(matches[0].get("path", ""))
        branch = experiment.get("branchName")
        if (not path.is_absolute() or path != path.resolve() or not path.is_dir()
                or not isinstance(branch, str) or re.fullmatch(r"orx/[a-z0-9][a-z0-9./_-]*", branch) is None):
            raise OrxError("ORX_BRANCH_PATH_INVALID")
        result = subprocess.run(["git", "-C", str(path), "rev-parse", "--verify", f"refs/heads/{branch}^{{commit}}"],
                                capture_output=True, text=True, timeout=10, check=False)
        if result.returncode != 0 or result.stdout.strip() != expected:
            raise OrxError("ORX_BRANCH_COMMIT_CHANGED")

    def runs(self, experiment_id: str) -> list[RunReference]:
        self.verify_experiment(experiment_id)
        values = self._get(f"/api/projects/{self.project_id}/runs").get("runs")
        if not isinstance(values, list):
            raise OrxError("ORX_RUN_LIST_INVALID")
        references = []
        for value in values:
            if not isinstance(value, dict):
                raise OrxError("ORX_RUN_INVALID")
            if value.get("experimentId") != experiment_id:
                continue
            backend = value.get("backend", {})
            if (value.get("projectId") != self.project_id or value.get("command") != self.fixed_command
                    or value.get("status") not in STATES or not isinstance(backend, dict)
                    or backend.get("kind") != "local_job"
                    or re.fullmatch(r"[a-f0-9]{40}", str(value.get("commitSha"))) is None
                    or re.fullmatch(r"[a-f0-9]{64}", str(backend.get("sourceDigest"))) is None
                    or type(value.get("createdAt")) is not int
                    or (value.get("endedAt") is not None and type(value["endedAt"]) is not int)):
                raise OrxError("ORX_RUN_CONTRACT_MISMATCH")
            references.append(RunReference(self.project_id, experiment_id, _identifier(value["id"]),
                                           value["commitSha"], self.fixed_command, value["status"],
                                           backend["sourceDigest"], value["createdAt"], value.get("endedAt")))
        if len({ref.run_id for ref in references}) != len(references):
            raise OrxError("ORX_DUPLICATE_RUN_ID")
        return references

    def attach_or_run(self, experiment_id: str, commit_sha: str, intent_path: Path,
                      *, permit_launch: bool = False) -> dict:
        """Attach an exact run, or admit one new launch with explicit caller intent.

        Reuse the same intent_path after interruption. A pending launch with no
        authoritative matching run remains UNKNOWN. A rerun requires a distinct
        experiment/decision, never a new checkpoint filename for the same node.
        """
        _identifier(experiment_id)
        if re.fullmatch(r"[a-f0-9]{40}", commit_sha) is None or not intent_path.is_absolute():
            raise OrxError("INVALID_RUN_IDENTITY")
        identity = {"project_id": self.project_id, "experiment_id": experiment_id,
                    "commit_sha": commit_sha, "command": self.fixed_command}
        with _locked(intent_path):
            intent = json.loads(intent_path.read_text()) if intent_path.exists() else None
            if intent is not None and (not isinstance(intent, dict) or intent.get("identity") != identity
                                       or intent.get("schema") != "project-research-orx-intent/v1"):
                raise OrxError("CHECKPOINT_IDENTITY_CHANGED")
            references = self.runs(experiment_id)
            run_id = intent.get("run_id") if intent else None
            if any(ref.status in ACTIVE and ref.commit_sha != commit_sha for ref in references):
                raise OrxError("OTHER_COMMIT_STILL_ACTIVE")
            matches = [ref for ref in references if ref.commit_sha == commit_sha and (run_id is None or ref.run_id == run_id)]
            if len(matches) > 1:
                raise OrxError("AMBIGUOUS_RUN_HISTORY")
            if matches:
                reference = matches[0]
                record = {"schema": "project-research-orx-intent/v1", "identity": identity,
                          "state": "ATTACHED", "run_id": reference.run_id,
                          "reference": asdict(reference), "reconciled_at": time.time()}
                _write(intent_path, record)
                return record
            if intent is not None:
                return {**intent, "state": "UNKNOWN", "reason": "SUBMISSION_REQUIRES_RECONCILIATION"}
            if references:
                raise OrxError("EXPERIMENT_ALREADY_HAS_RUN_HISTORY")
            if not permit_launch:
                return {"identity": identity, "state": "NOT_SUBMITTED"}
            self._verify_commit(experiment_id, commit_sha)
            intent = {"schema": "project-research-orx-intent/v1", "identity": identity,
                      "state": "SUBMITTING", "run_id": None, "submitted_at": time.time()}
            _write(intent_path, intent)
            try:
                intent["run_id"] = self._launch(experiment_id)
                intent["state"] = "SUBMITTED"
            except (OrxError, OSError, subprocess.SubprocessError):
                intent["state"] = "UNKNOWN"
            _write(intent_path, intent)
            # Preserve the intent before the authoritative follow-up read.
            references = self.runs(experiment_id)
            matches = [ref for ref in references if ref.commit_sha == commit_sha
                       and (intent["run_id"] is None or ref.run_id == intent["run_id"])]
            if len(matches) == 1:
                intent.update(state="ATTACHED", run_id=matches[0].run_id,
                              reference=asdict(matches[0]), reconciled_at=time.time())
                _write(intent_path, intent)
            else:
                intent.update(state="UNKNOWN", reason="SUBMISSION_REQUIRES_RECONCILIATION")
                _write(intent_path, intent)
            return intent

    def logs(self, reference: RunReference, *, maximum_bytes: int = 8 * 1024 * 1024) -> bytes:
        """Read ORX-persisted output; a terminal status does not certify its claims."""
        if reference.project_id != self.project_id or maximum_bytes <= 0:
            raise OrxError("LOG_SCOPE_INVALID")
        matches = [ref for ref in self.runs(reference.experiment_id) if ref.run_id == reference.run_id]
        if (len(matches) != 1 or matches[0].commit_sha != reference.commit_sha
                or matches[0].source_digest != reference.source_digest):
            raise OrxError("LOG_RUN_IDENTITY_CHANGED")
        offset = 0
        chunks = []
        while True:
            value = self._get(f"/api/runs/{reference.run_id}/log?offset={offset}")
            if not isinstance(value.get("dataBase64"), str) or type(value.get("eof")) is not bool:
                raise OrxError("LOG_WINDOW_INVALID")
            data = base64.b64decode(value["dataBase64"], validate=True)
            if value.get("nextOffset") != offset + len(data) or offset + len(data) > maximum_bytes:
                raise OrxError("LOG_WINDOW_INVALID")
            chunks.append(data)
            offset += len(data)
            if value["eof"]:
                return b"".join(chunks)
            if not data:
                raise OrxError("LOG_WINDOW_STALLED")
