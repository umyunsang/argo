"""Create immutable ORX nodes in a dedicated private repository, then attach."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from .contracts import digest, utc_now, write_new
from .orx_adapter import OrxAdapter
from .state import Store


FIXED_COMMAND = "/opt/homebrew/bin/python3 runner.py"
ROOT = Path.home() / ".local/share/argo-project-research-20260909"
SOURCE = Path(__file__).resolve().parent


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=True, timeout=30).stdout.strip()


def dispatch(spec: dict, title: str, *, candidate: bytes | None = None) -> dict:
    project = json.loads((ROOT / "control/orx-project.json").read_text())["project"]
    repository = Path(project["path"])
    if repository != ROOT / "orx-project" or git(repository, "remote"):
        raise ValueError("dedicated private ORX repository required")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,100}", title):
        raise ValueError("safe title required")
    lock_path = ROOT / "control/dispatch.lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(fd, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        adapter = OrxAdapter(project["id"], FIXED_COMMAND)
        request_id = digest({"spec": spec, "candidate_sha256": hashlib.sha256(candidate).hexdigest() if candidate is not None else None})
        request_dir = ROOT / "control/dispatches" / request_id
        if request_dir.exists():
            frozen_path = request_dir / "frozen.json"
            if not frozen_path.exists():
                raise RuntimeError("previous ORX node creation requires reconciliation; no automatic replacement")
            frozen = json.loads(frozen_path.read_text())
            if frozen["spec_digest"] != digest(spec):
                raise RuntimeError("frozen experiment identity changed")
            intent_path = request_dir / "launch.json"
            return {"intent_path": str(intent_path), **adapter.attach_or_run(frozen["experiment_id"], frozen["commit"], intent_path, permit_launch=True)}
        request_dir.mkdir(parents=True)
        write_new(request_dir / "request.json", {"at": utc_now(), "spec": spec, "title": title, "spec_digest": digest(spec)})
        parent_args = ["--parent", spec["parent_experiment_id"]] if spec.get("parent_experiment_id") else ["--baseline"]
        result = subprocess.run([adapter.executable, "--no-telemetry", "create-experiment", project["id"], "--title", title,
                                 "--description", spec.get("hypothesis", "Development baseline and first hypothesis"), *parent_args],
                                capture_output=True, text=True, timeout=30, check=True)
        (request_dir / "create-output.txt").write_text(result.stdout)
        fields = dict(re.findall(r"^  (id|branch): +(.+)$", result.stdout, re.MULTILINE))
        experiment_id, branch = fields["id"], fields["branch"]
        adapter.verify_experiment(experiment_id)
        worktree = ROOT / "control/worktrees" / request_id
        worktree.parent.mkdir(parents=True, exist_ok=True)
        git(repository, "worktree", "add", str(worktree), branch)
        files = {"runner.py": b"from experiments.project_research.runner import main\nraise SystemExit(main())\n",
                 "experiments/__init__.py": b"", "node-spec.json": (json.dumps(spec, indent=2, allow_nan=False) + "\n").encode()}
        for name in ("__init__.py", "contracts.py", "state.py", "runner.py", "container_task.py"):
            files["experiments/project_research/" + name] = (SOURCE / name).read_bytes()
        for path in (SOURCE / "domains").glob("*.py"):
            files["experiments/project_research/domains/" + path.name] = path.read_bytes()
        files["experiments/project_research/domains/requirements.txt"] = (SOURCE / "domains/requirements.txt").read_bytes()
        if candidate is not None:
            files["candidate.py"] = candidate
        for name, data in files.items():
            dest = worktree / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        git(worktree, "add", "--", *files)
        git(worktree, "-c", "user.name=Research Apparatus", "-c", "user.email=research@localhost", "commit", "-m", title)
        commit = git(worktree, "rev-parse", "HEAD")
        write_new(request_dir / "frozen.json", {"experiment_id": experiment_id, "commit": commit, "spec_digest": digest(spec), "worktree": str(worktree)})
        intent_path = request_dir / "launch.json"
        record = adapter.attach_or_run(experiment_id, commit, intent_path, permit_launch=True)
        Store(ROOT / "control/state.sqlite").event({"event": "orx_launch", "project_id": spec["project_id"], "team_id": spec.get("team_id"),
                                                     "domain": spec["domain"], "intent": str(intent_path), **record})
        return {"intent_path": str(intent_path), **record}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    print(json.dumps(dispatch(json.loads(args.spec.read_text()), args.title), indent=2))


if __name__ == "__main__":
    main()
