"""Prepare one fresh private development episode; never launch or train anything."""
from __future__ import annotations

import argparse
import csv
import dataclasses
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import time
import uuid


REPOSITORY_ROOT = Path("/Users/um-yunsang/argo-paper-orx")
STUDY_ROOT = Path.home() / ".local/share/argo-study-20260909"
PROJECT_ID = "c9443332-b7f0-40db-9f5d-68b7cf4f4bff"
IMAGE = "sha256:a70ce9ad201eb7695c4d8e4e7085271cdb09092c173253b002424b9508f9fd8c"
FIXED_COMMAND = "/opt/homebrew/bin/python3 runner.py"
DEVELOPMENT_TASKS = {37: (37, 1), 146820: (40983, 2), 31: (31, 1), 146821: (40975, 3)}
PUBLIC_KEYS = ("target_column", "feature_columns", "numeric_columns", "categorical_columns", "class_mapping", "classes")
CODE_FILES = ("controller.ts", "model_meter.ts", "runner.py", "scientific_bridge.py", "candidate_entry.py", "scoring.py", "kernel_wrapper.py")


@dataclasses.dataclass(frozen=True)
class Anchor:
    name: str
    filename: str
    sha256: str
    start_line: int
    end_line: int


ANCHORS = (
    Anchor("Prime", "2608.23552v1.txt", "bb5da5a634794581a1f52dbf96daa164790a5fef78943dc4d1a3b14a252b9fa3", 131, 293),
    Anchor("HoH", "2609.01481v1.txt", "c639844f3eaad3ed6458cea9ac6286ac60dbcf17edee7e915fb6a052bdbe117a", 285, 430),
    Anchor("Scroll", "2608.21690v1.txt", "37f692dfb96e18d13964659c32778ab0d02d4a45fe0a77e7f3634b87985319af", 274, 352),
    Anchor("HarnessDev", "2609.01437v1.txt", "82459e9b1506b9ccb5c523b87f35d9ceb0794bde92919fa5b043900c9852f5ab", 200, 227),
    Anchor("RecEvolve", "2609.01622v1.txt", "4f6a738aac042779143d0aca7cf910b3e5436cdcc1640e6cb13faa6586369985", 180, 269),
)


@dataclasses.dataclass(frozen=True)
class Locations:
    study_root: Path
    custody_summary: Path
    corpus_root: Path
    auth_path: Path
    anchors: tuple[Anchor, ...] = ANCHORS


class PreparationError(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def safe_path(path: Path, *, exists: bool = True) -> Path:
    text = str(path)
    if not path.is_absolute() or any(char in text for char in (",", "\n", "\r", "\0")):
        raise PreparationError("INVALID_PATH")
    if path != path.resolve(strict=exists):
        raise PreparationError("NONCANONICAL_OR_SYMLINK_PATH")
    return path


def regular_bytes(path: Path, maximum: int) -> bytes:
    safe_path(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > maximum:
            raise PreparationError("INVALID_INPUT_FILE")
        data = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
        if len(data) > maximum or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise PreparationError("INPUT_CHANGED_DURING_READ")
    return data


def write_new(path: Path, data: bytes, *, mode: int = 0o400) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def default_locations() -> Locations:
    return Locations(
        STUDY_ROOT,
        REPOSITORY_ROOT / ".planning/2026-09-09-autonomous-execution/data-custody.json",
        REPOSITORY_ROOT / "paper/research/five-anchor-harness-20260908/sources",
        Path.home() / ".prime/agent/auth.json",
    )


def public_schema(metadata: dict) -> dict:
    if any(key not in metadata for key in PUBLIC_KEYS):
        raise PreparationError("PUBLIC_SCHEMA_MISSING")
    schema = {key: metadata[key] for key in PUBLIC_KEYS}
    for key in ("feature_columns", "numeric_columns", "categorical_columns", "class_mapping"):
        values = schema[key]
        if not isinstance(values, list) or any(not isinstance(value, str) or not value or "\0" in value for value in values) or len(values) != len(set(values)):
            raise PreparationError("PUBLIC_SCHEMA_INVALID")
    features = schema["feature_columns"]
    numeric = schema["numeric_columns"]
    categorical = schema["categorical_columns"]
    target = schema["target_column"]
    classes = schema["classes"]
    if (not features or not isinstance(target, str) or not target or target in features
            or set(numeric) & set(categorical) or set(numeric) | set(categorical) != set(features)
            or not isinstance(classes, list) or len(classes) < 2 or any(type(value) is not int for value in classes)
            or classes != list(range(len(schema["class_mapping"])))):
        raise PreparationError("PUBLIC_SCHEMA_INVALID")
    if any(name.lower() in {"rowid", "row_id", "__row_id", "row_identity"} for name in features):
        raise PreparationError("ROW_ID_COLUMN_FORBIDDEN")
    return schema


def validate_train(data: bytes, schema: dict, expected_rows: int) -> None:
    if type(expected_rows) is not int or expected_rows <= 0:
        raise PreparationError("INVALID_TRAIN_COUNT")
    reader = csv.reader(io.StringIO(data.decode("utf-8"), newline=""))
    expected = schema["feature_columns"] + [schema["target_column"]]
    if next(reader, None) != expected:
        raise PreparationError("TRAIN_HEADER_MISMATCH")
    count = 0
    for row in reader:
        if len(row) != len(expected) or not row[-1].isdecimal() or int(row[-1]) not in schema["classes"]:
            raise PreparationError("TRAIN_SCHEMA_MISMATCH")
        count += 1
    if count != expected_rows:
        raise PreparationError("TRAIN_COUNT_MISMATCH")


def task_brief(task_id: int, schema: dict) -> str:
    return f"""# Bounded classification task {task_id}

Improve one tabular classifier using inner_train.csv and the permitted development feedback. public.json defines feature order, numeric/categorical columns, target column and class mapping. The training CSV has exactly those feature columns followed by the supervised target {schema['target_column']!r}. Training labels are encoded as the integer classes in public.json. Empty CSV fields represent missing values; preserve categorical strings with keep_default_na=False and fit learned transforms on training rows only.

The host calls initialize before your first prompt and registers the RF100 starting candidate. Its first development observation consumes one of the twelve feedback opportunities. list_results identifies the default candidate and measured receipt. Do not repeat baseline initialization or invent its score. If you select no replacement, that registered default remains the final choice. No solution.py is required for initialization; create it in this workspace when proposing a change.

Candidate API in solution.py:

    def fit(train_X, train_y, frozen_config):
        # Return a fitted object with predict(X).
        ...

train_X is a pandas DataFrame with the declared feature order, numeric floats and categorical string columns; train_y is a NumPy integer vector. predict(X) must return exactly one finite integer class per input row, in input order, using only the classes in public.json. The fitted object must survive joblib serialization between separate fit and prediction containers. Define custom estimator classes in solution.py. All imports must be available in the frozen scientific image; network access is unavailable.

Use run_candidate(relative_source="solution.py", config={{...}}, hypothesis="...") to freeze your source and JSON configuration and obtain one admitted development receipt. The source defines the full fitting procedure; frozen_config is exactly the JSON dictionary you pass, not an implicit estimator search space. The scientific runtime provides candidate_entry.baseline_fit for the registered baseline; that module is available in the scientific container and need not be importable in this worker. Host tools execute scientific candidates through ORX. Local train-only analysis/CV remains within the same CPU budget. Source code and configuration, not a locally fitted pickle, are submitted to run_candidate.

list_results exposes permitted receipts. lock_candidate(candidate_id) explicitly selects one observed VALID candidate; use the returned c- identifier, not the harness name B0/R0. A failed admitted candidate consumes a slot. Identical requests reuse a receipt. UNKNOWN requires reconciliation and stops additional requests; do not retry an uncertain launch. At most twelve feedback vectors including baseline and one final refit are admitted. No development-label files, outer-training data, original row IDs, original source files or test features/labels are provided to this worker.

Your operational model budget is80000 normalized tokens including all child calls. Episode limits are90 wall minutes,120 CPU-core minutes,2 shared CPUs and8GiB shared memory. Reserve the final10 wall minutes and15 CPU-core minutes. read_corpus lists or reads the same immutable method excerpts for both conditions. Keep useful decision/experiment/source references in the workspace or native session artifacts. Native ipython preserves Python state; native rlm children share this budget. Obey the active policy prompt and stop or lock when further experiments are not justified. Final hidden evaluation is never fed back for further selection.
"""


def prepare_episode(*, episode_id: str, arm: str, candidate_id: str, task_id: int,
                    parent_experiment_id: str, code_root: Path,
                    locations: Locations | None = None, now: float | None = None) -> dict:
    locations = default_locations() if locations is None else locations
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", episode_id) or episode_id in {"custody", "source", "sources", "control", "test", "profile", "credentials"}:
        raise PreparationError("INVALID_EPISODE_ID")
    if arm not in {"B", "R"} or candidate_id != arm + "0":
        raise PreparationError("ARM_CANDIDATE_MISMATCH")
    if type(task_id) is not int or task_id not in DEVELOPMENT_TASKS:
        raise PreparationError("DEVELOPMENT_TASK_REQUIRED")
    try:
        if str(uuid.UUID(parent_experiment_id)) != parent_experiment_id:
            raise ValueError
    except (ValueError, AttributeError):
        raise PreparationError("INVALID_PARENT_EXPERIMENT_ID") from None
    code_root = safe_path(code_root)
    study_root = safe_path(locations.study_root)
    project_path = safe_path(study_root / "orx-project")
    if not code_root.is_dir() or not project_path.is_dir() or not study_root.is_dir():
        raise PreparationError("INPUT_DIRECTORY_REQUIRED")
    auth_path = safe_path(locations.auth_path)
    if not stat.S_ISREG(auth_path.stat().st_mode):
        raise PreparationError("AUTH_REFERENCE_NOT_FILE")
    summary_bytes = regular_bytes(locations.custody_summary, 2 * 1024 * 1024)
    summary = json.loads(summary_bytes)
    matching = [row for row in summary["tasks"] if row.get("task_id") == task_id]
    if len(matching) != 1 or matching[0].get("status") != "PREPARED":
        raise PreparationError("CUSTODY_NOT_PREPARED")
    custody = safe_path(study_root / "custody" / f"task_{task_id}")
    if matching[0]["custody_path"] != str(custody):
        raise PreparationError("CUSTODY_PATH_MISMATCH")
    metadata_path = custody / "metadata.json"
    metadata_bytes = regular_bytes(metadata_path, 1024 * 1024)
    if digest(metadata_bytes) != matching[0]["metadata_sha256"]:
        raise PreparationError("METADATA_HASH_MISMATCH")
    metadata = json.loads(metadata_bytes)
    if (metadata.get("task_id") != task_id or metadata.get("allocation") != "development"
            or (metadata.get("data_id"), metadata.get("data_version")) != DEVELOPMENT_TASKS[task_id]):
        raise PreparationError("METADATA_TASK_MISMATCH")
    schema = public_schema(metadata)
    train_bytes = regular_bytes(custody / "inner_train.csv", 16 * 1024 * 1024)
    if digest(train_bytes) != metadata["files_sha256"]["inner_train.csv"]:
        raise PreparationError("TRAIN_HASH_MISMATCH")
    validate_train(train_bytes, schema, metadata["row_counts"]["inner_train"])

    code_hashes = {name: digest(regular_bytes(code_root / name, 4 * 1024 * 1024)) for name in CODE_FILES}
    prompt_manifest_bytes = regular_bytes(code_root / "prompts/manifest.json", 65536)
    prompt_manifest = json.loads(prompt_manifest_bytes)
    prompts = {name: regular_bytes(code_root / "prompts" / name, 24000) for name in ("common.md", "B0.md", "R0.md")}
    for name, data in prompts.items():
        if digest(data) != prompt_manifest["files"][name] or not data.decode("utf-8").strip():
            raise PreparationError("PROMPT_HASH_MISMATCH")
        code_hashes["prompts/" + name] = digest(data)
    code_hashes["prompts/manifest.json"] = digest(prompt_manifest_bytes)

    corpus = {}
    corpus_evidence = {}
    if len(locations.anchors) != 5 or len({anchor.name for anchor in locations.anchors}) != 5:
        raise PreparationError("FIVE_ANCHORS_REQUIRED")
    for anchor in locations.anchors:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", anchor.name) or Path(anchor.filename).name != anchor.filename:
            raise PreparationError("INVALID_ANCHOR_PATH")
        source_path = locations.corpus_root / anchor.filename
        source = regular_bytes(source_path, 2 * 1024 * 1024)
        if digest(source) != anchor.sha256:
            raise PreparationError("CORPUS_SOURCE_HASH_MISMATCH")
        lines = source.decode("utf-8").splitlines(keepends=True)
        if not 1 <= anchor.start_line <= anchor.end_line <= len(lines):
            raise PreparationError("CORPUS_RANGE_INVALID")
        excerpt = (f"Method excerpt: {anchor.name}; retained {anchor.filename}; lines {anchor.start_line}-{anchor.end_line}.\n"
                   "This is a source method reference, not a claim that every mechanism is available in this episode.\n\n"
                   + "".join(lines[anchor.start_line - 1:anchor.end_line])).encode("utf-8")
        if not excerpt.strip() or len(excerpt) > 24000:
            raise PreparationError("CORPUS_EXCERPT_LIMIT")
        corpus[anchor.name] = excerpt
        corpus_evidence[anchor.name] = {"source_path": str(source_path), "source_sha256": digest(source),
                                       "start_line": anchor.start_line, "end_line": anchor.end_line,
                                       "excerpt_sha256": digest(excerpt), "bytes": len(excerpt)}

    started = time.time() if now is None else now
    if isinstance(started, bool) or not isinstance(started, (int, float)) or not math.isfinite(started) or started <= 0:
        raise PreparationError("INVALID_PREPARATION_TIME")
    episodes = safe_path(study_root / "episodes", exists=False)
    episodes.mkdir(mode=0o700, exist_ok=True)
    episode = safe_path(episodes / episode_id, exists=False)
    try:
        episode.mkdir(mode=0o700)
    except FileExistsError:
        raise PreparationError("EPISODE_EXISTS_REFUSE_OVERWRITE") from None
    workspace, artifacts, control = (episode / name for name in ("workspace", "artifacts", "control"))
    for path in (workspace, artifacts, control, control / "scientific", control / "corpus"):
        path.mkdir(mode=0o700)
    deadline = started + 5400
    kernel = {"image": IMAGE, "workspace": str(workspace), "artifact_root": str(artifacts), "control_dir": str(control),
              "deadline_epoch": deadline, "kernel_cpus": 0.5, "kernel_memory_bytes": 536870912,
              "episode_cpus": 2, "episode_memory_bytes": 8589934592, "max_cpu_seconds": 7200,
              "pids_limit": 128, "docker": "/opt/homebrew/bin/docker"}
    brief = task_brief(task_id, schema).encode("utf-8")
    write_new(workspace / "inner_train.csv", train_bytes)
    write_new(workspace / "public.json", json_bytes(schema))
    write_new(workspace / "TASK.md", brief)
    write_new(control / "common.md", prompts["common.md"])
    write_new(control / "policy.md", prompts[candidate_id + ".md"])
    write_new(control / "task-prompt.md", brief)
    for name, data in corpus.items():
        write_new(control / "corpus" / (name + ".txt"), data)
    kernel_path = control / "kernel.json"
    write_new(kernel_path, json_bytes(kernel))
    configuration = {
        "episode_id": episode_id, "arm": arm, "candidate_id": candidate_id, "task_id": task_id,
        "workspace": str(workspace), "private_artifact_dir": str(control / "scientific"),
        "kernel_config": str(kernel_path), "family_ledger": str(study_root / "ledgers" / (arm + ".json")),
        "auth_path": str(auth_path), "common_prompt": str(control / "common.md"),
        "policy_prompt": str(control / "policy.md"), "task_prompt": str(control / "task-prompt.md"),
        "corpus": {name: str(control / "corpus" / (name + ".txt")) for name in corpus},
        "model_id": "openai/gpt-5.6-sol", "token_limit": 80000, "family_limit": 1500000,
        "family_usd_limit": 45, "deadline_epoch": deadline, "custody_task_root": str(custody),
        "metadata": str(metadata_path), "projectId": PROJECT_ID, "projectPath": str(project_path),
        "image": IMAGE, "orx_executable": str(Path.home() / ".local/bin/orx"),
        "parent_experiment_id": parent_experiment_id, "feedback_limit": 12, "final_refit_limit": 1,
        "fixed_command": FIXED_COMMAND, "code_root": str(code_root), "code_sha256": code_hashes,
        "metadata_sha256": digest(metadata_bytes),
    }
    config_path = control / "episode.json"
    config_bytes = json_bytes(configuration)
    write_new(config_path, config_bytes)
    receipt = {
        "schema": "study-episode-preparation/v1", "status": "PREPARED_NOT_LAUNCHED", "episode_id": episode_id,
        "config_path": str(config_path), "config_sha256": digest(config_bytes), "kernel_sha256": digest(json_bytes(kernel)),
        "prepared_epoch": started, "deadline_epoch": deadline, "arm": arm, "candidate_id": candidate_id, "task_id": task_id,
        "code_root": str(code_root), "code_sha256": code_hashes, "code_manifest_sha256": digest(json_bytes(code_hashes)),
        "custody_summary_sha256": digest(summary_bytes), "metadata_path": str(metadata_path), "metadata_sha256": digest(metadata_bytes),
        "train_sha256": digest(train_bytes), "public_schema_sha256": digest(json_bytes(schema)), "task_prompt_sha256": digest(brief),
        "corpus": corpus_evidence, "public_mount_roots": [str(workspace), str(artifacts)],
        "initial_worker_files": ["TASK.md", "inner_train.csv", "public.json"], "auth_content_read": False,
        "scientific_runs": 0, "model_calls": 0, "orx_nodes_created": 0,
        "source_hash_guard": "Root rechecks prepared code/config hashes before committing the ORX episode spec.",
    }
    receipt_path = control / "preparation-receipt.json"
    write_new(receipt_path, json_bytes(receipt))
    return {"status": receipt["status"], "episode_id": episode_id, "config_path": str(config_path),
            "config_sha256": receipt["config_sha256"], "receipt_path": str(receipt_path),
            "receipt_sha256": digest(json_bytes(receipt)), "code_sha256": code_hashes}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--episode-id", required=True)
    prepare.add_argument("--arm", choices=("B", "R"), required=True)
    prepare.add_argument("--candidate-id", choices=("B0", "R0"), required=True)
    prepare.add_argument("--task-id", type=int, required=True)
    prepare.add_argument("--parent-experiment-id", required=True)
    prepare.add_argument("--code-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = prepare_episode(episode_id=args.episode_id, arm=args.arm, candidate_id=args.candidate_id,
                                 task_id=args.task_id, parent_experiment_id=args.parent_experiment_id, code_root=args.code_root)
    except PreparationError as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}))
        return 2
    except (OSError, ValueError, KeyError, TypeError):
        print(json.dumps({"status": "REJECTED", "reason": "INPUT_OR_PREPARATION_FAILURE"}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
