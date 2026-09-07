#!/usr/bin/env python3
"""Fixed POSIX limit applicator for the A2 one-shot controller process."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import stat
import sys

KNOWN_SYSTEM_PATH = "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin"
PRODUCTION_ENV_KEYS = frozenset({
    "PRIME_AGENT_CODING_AGENT_DIR",
    "PRIME_AGENT_KERNEL_PYTHON",
    "PRIME_AGENT_TELEMETRY",
    "PATH",
    "TMPDIR",
    "LANG",
    "LC_ALL",
    "TZ",
})
SYNTHETIC_ENV_KEYS = frozenset({
    "PATH",
    "ARGO_A2_SYNTHETIC_ACTION",
    "ARGO_A2_SYNTHETIC_VALUE",
})


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def _nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be nonnegative")
    return parsed


@dataclass(frozen=True)
class _VerifiedFile:
    path: Path
    descriptor: int
    stat_identity: tuple[int, int, int, int, int, int, int]
    sha256: str
    max_bytes: int


def _stat_identity(info: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (
        info.st_dev,
        info.st_ino,
        stat.S_IMODE(info.st_mode),
        info.st_uid,
        info.st_nlink,
        info.st_size,
        info.st_mtime_ns,
    )


def _sha256(source: Path | int, max_bytes: int | None = None) -> str:
    digest = hashlib.sha256()
    total = 0
    if isinstance(source, int):
        os.lseek(source, 0, os.SEEK_SET)
        while True:
            read_size = 1024 * 1024
            if max_bytes is not None:
                read_size = min(read_size, max_bytes + 1 - total)
            block = os.read(source, read_size)
            if not block:
                break
            total += len(block)
            if max_bytes is not None and total > max_bytes:
                raise ValueError("file_hash_bound_exceeded")
            digest.update(block)
        return digest.hexdigest()
    with source.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            total += len(block)
            if max_bytes is not None and total > max_bytes:
                raise ValueError("file_hash_bound_exceeded")
            digest.update(block)
    return digest.hexdigest()


def _verify_file(
    raw_path: str,
    expected_device: int,
    expected_inode: int,
    expected_size: int,
    expected_sha256: str,
    *,
    executable: bool,
    expected_mode: int | None = None,
    expected_uid: int | None = None,
    expected_mtime_ns_max: int | None = None,
    max_bytes: int | None = None,
) -> _VerifiedFile:
    path = Path(raw_path)
    if not path.is_absolute() or "\x00" in raw_path:
        raise ValueError("invalid_absolute_file")
    resolved = path.resolve(strict=True)
    if str(resolved) != raw_path:
        raise ValueError("noncanonical_file")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(resolved, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ValueError("invalid_regular_file")
        if executable and not (stat.S_IMODE(before.st_mode) & 0o111):
            raise ValueError("not_executable")
        if max_bytes is not None and before.st_size > max_bytes:
            raise ValueError("file_size_bound_exceeded")
        if (before.st_dev, before.st_ino, before.st_size) != (
            expected_device,
            expected_inode,
            expected_size,
        ):
            raise ValueError("file_identity_changed")
        if expected_mode is not None and stat.S_IMODE(before.st_mode) != expected_mode:
            raise ValueError("file_mode_changed")
        if expected_uid is not None and before.st_uid != expected_uid:
            raise ValueError("file_owner_changed")
        if expected_mtime_ns_max is not None and before.st_mtime_ns > expected_mtime_ns_max:
            raise ValueError("file_mtime_changed")
        effective_bound = max_bytes if max_bytes is not None else expected_size
        digest = _sha256(descriptor, effective_bound)
        after = os.fstat(descriptor)
        path_after = os.stat(resolved, follow_symlinks=False)
        identity = _stat_identity(before)
        if (
            _stat_identity(after) != identity
            or _stat_identity(path_after) != identity
            or resolved.resolve(strict=True) != resolved
        ):
            raise ValueError("file_changed_during_verification")
        if digest != expected_sha256:
            raise ValueError("file_hash_changed")
        return _VerifiedFile(
            path=resolved,
            descriptor=descriptor,
            stat_identity=identity,
            sha256=digest,
            max_bytes=max_bytes if max_bytes is not None else expected_size,
        )
    except Exception:
        os.close(descriptor)
        raise


def _revalidate_verified_file(verified: _VerifiedFile) -> None:
    descriptor_info = os.fstat(verified.descriptor)
    path_info = os.stat(verified.path, follow_symlinks=False)
    if (
        _stat_identity(descriptor_info) != verified.stat_identity
        or _stat_identity(path_info) != verified.stat_identity
        or verified.path.resolve(strict=True) != verified.path
        or descriptor_info.st_size > verified.max_bytes
        or _sha256(verified.descriptor, verified.max_bytes) != verified.sha256
    ):
        raise ValueError("verified_file_changed_before_exec")


def _verify_directory(raw_path: str, expected_device: int, expected_inode: int) -> Path:
    path = Path(raw_path)
    if not path.is_absolute() or "\x00" in raw_path:
        raise ValueError("invalid_absolute_directory")
    resolved = path.resolve(strict=True)
    if str(resolved) != raw_path:
        raise ValueError("noncanonical_directory")
    info = os.stat(resolved, follow_symlinks=False)
    if not stat.S_ISDIR(info.st_mode):
        raise ValueError("invalid_directory")
    if (info.st_dev, info.st_ino) != (expected_device, expected_inode):
        raise ValueError("directory_identity_changed")
    return resolved


def _file_identity(path: Path, max_bytes: int = 256 * 1024 * 1024) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    if resolved != path:
        path = resolved
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size > max_bytes
        ):
            raise ValueError("interpreter_file_invalid")
        digest = _sha256(descriptor, max_bytes)
        after = os.fstat(descriptor)
        path_after = os.stat(path, follow_symlinks=False)
        if (
            _stat_identity(after) != _stat_identity(before)
            or _stat_identity(path_after) != _stat_identity(before)
            or path.resolve(strict=True) != path
        ):
            raise ValueError("interpreter_file_changed")
    finally:
        os.close(descriptor)
    return {
        "resolved_path": str(path),
        "path_kind": "regular_file",
        "device": before.st_dev,
        "inode": before.st_ino,
        "mode": stat.S_IMODE(before.st_mode),
        "uid": before.st_uid,
        "size": before.st_size,
        "mtime_ns_max": before.st_mtime_ns,
        "sha256": digest,
    }


def _symlink_chain(path: Path) -> list[dict[str, object]]:
    current = path
    chain: list[dict[str, object]] = []
    seen: set[tuple[int, int]] = set()
    for _ in range(40):
        parts = current.parts
        prefix = Path(parts[0])
        followed = False
        for index, component in enumerate(parts[1:], start=1):
            prefix = prefix / component
            info = os.lstat(prefix)
            if not stat.S_ISLNK(info.st_mode):
                continue
            key = (info.st_dev, info.st_ino)
            if key in seen:
                raise ValueError("interpreter_symlink_loop")
            seen.add(key)
            target_text = os.readlink(prefix)
            chain.append({
                "path": str(prefix),
                "device": info.st_dev,
                "inode": info.st_ino,
                "mode": stat.S_IMODE(info.st_mode),
                "uid": info.st_uid,
                "link_target": target_text,
            })
            target = Path(target_text)
            if not target.is_absolute():
                target = prefix.parent / target
            current = Path(os.path.normpath(str(target.joinpath(*parts[index + 1:]))))
            followed = True
            break
        if not followed:
            return chain
    raise ValueError("interpreter_symlink_depth")


def _verify_interpreter(identity_json: str) -> None:
    expected = json.loads(identity_json)
    if not isinstance(expected, dict):
        raise ValueError("interpreter_identity_invalid")
    invocation_text = expected.get("invocation_path")
    config_text = expected.get("pyvenv_cfg_path")
    if not isinstance(invocation_text, str) or not isinstance(config_text, str):
        raise ValueError("interpreter_identity_invalid")
    invocation = Path(invocation_text)
    config_path = Path(config_text)
    if not invocation.is_absolute() or not config_path.is_absolute():
        raise ValueError("interpreter_identity_invalid")
    actual = {
        "invocation_path": str(invocation),
        "symlink_chain": _symlink_chain(invocation),
        "resolved_target": _file_identity(invocation),
        "pyvenv_cfg_path": str(config_path.resolve(strict=True)),
        "pyvenv_cfg": _file_identity(config_path, 65536),
    }
    if actual != expected:
        raise ValueError("interpreter_identity_changed")
    if sys.executable != invocation_text:
        raise ValueError("interpreter_invocation_changed")


def _verify_process_exec(identity_json: str) -> None:
    expected = json.loads(identity_json)
    if not isinstance(expected, dict) or _file_identity(Path(__file__), 1024 * 1024) != expected:
        raise ValueError("process_exec_identity_changed")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--interpreter-identity-json", required=True)
    parser.add_argument("--process-exec-identity-json", required=True)
    parser.add_argument("--cpu-seconds", required=True, type=_positive_int)
    parser.add_argument("--file-size-bytes", required=True, type=_positive_int)
    parser.add_argument("--v8-old-space-mib", required=True, type=_positive_int)
    for name in ("node", "frontend", "deployment"):
        parser.add_argument(f"--{name}-path", required=True)
        parser.add_argument(f"--{name}-device", required=True, type=_positive_int)
        parser.add_argument(f"--{name}-inode", required=True, type=_positive_int)
        parser.add_argument(f"--{name}-size", required=True, type=_positive_int)
        parser.add_argument(f"--{name}-mode", required=True, type=_positive_int)
        parser.add_argument(f"--{name}-uid", required=True, type=_nonnegative_int)
        parser.add_argument(f"--{name}-mtime-ns-max", required=True, type=_positive_int)
        parser.add_argument(f"--{name}-sha256", required=True)
    parser.add_argument("--artifact-root", required=True)
    parser.add_argument("--artifact-root-device", required=True, type=_positive_int)
    parser.add_argument("--artifact-root-inode", required=True, type=_positive_int)
    parser.add_argument("--synthetic-test-context", action="store_true")
    return parser


def _validated_environment(synthetic: bool, artifact_root: Path) -> dict[str, str]:
    allowed = SYNTHETIC_ENV_KEYS if synthetic else PRODUCTION_ENV_KEYS
    result = {key: value for key, value in os.environ.items() if key in allowed}
    if set(result) != allowed:
        if synthetic and set(result) in (
            {"PATH", "ARGO_A2_SYNTHETIC_ACTION"},
            set(SYNTHETIC_ENV_KEYS),
        ):
            pass
        else:
            raise ValueError("environment_key_set_mismatch")
    if result.get("PATH") != KNOWN_SYSTEM_PATH:
        raise ValueError("path_value_mismatch")
    if not synthetic:
        fixed = {
            "PRIME_AGENT_TELEMETRY": "0",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "TZ": "UTC",
        }
        if any(result.get(key) != value for key, value in fixed.items()):
            raise ValueError("environment_value_mismatch")
        for key in ("PRIME_AGENT_CODING_AGENT_DIR", "PRIME_AGENT_KERNEL_PYTHON"):
            value = result[key]
            if not value or not Path(value).is_absolute() or "\x00" in value:
                raise ValueError("environment_path_invalid")
        expected_tmp = f"{artifact_root}/tmp/"
        if result.get("TMPDIR") != expected_tmp:
            raise ValueError("temporary_directory_mismatch")
        tmp_path = artifact_root / "tmp"
        info = os.stat(tmp_path, follow_symlinks=False)
        if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o700:
            raise ValueError("temporary_directory_invalid")
        with os.scandir(tmp_path) as entries:
            if next(entries, None) is not None:
                raise ValueError("temporary_directory_not_empty")
    return result


def build_target_argv(
    node: Path,
    frontend: Path,
    deployment: Path,
    artifact_root: Path,
    v8_old_space_mib: int,
    synthetic_test_context: bool,
) -> list[str]:
    if synthetic_test_context:
        return [
            str(node),
            str(frontend),
            "--deployment",
            str(deployment),
            "--artifact-root",
            str(artifact_root),
        ]
    return [
        str(node),
        f"--max-old-space-size={v8_old_space_mib}",
        str(frontend),
        "--deployment",
        str(deployment),
        "--artifact-root",
        str(artifact_root),
    ]


def main() -> int:
    args = _parser().parse_args()
    verified_files: list[_VerifiedFile] = []
    try:
        os.umask(0o077)
        resource.setrlimit(
            resource.RLIMIT_FSIZE,
            (args.file_size_bytes, args.file_size_bytes),
        )
        resource.setrlimit(
            resource.RLIMIT_CPU,
            (args.cpu_seconds, args.cpu_seconds),
        )
        if hasattr(signal, "SIGXFSZ"):
            signal.signal(signal.SIGXFSZ, signal.SIG_DFL)
        if hasattr(signal, "SIGXCPU"):
            signal.signal(signal.SIGXCPU, signal.SIG_DFL)
        _verify_interpreter(args.interpreter_identity_json)
        _verify_process_exec(args.process_exec_identity_json)
        node = _verify_file(
            args.node_path,
            args.node_device,
            args.node_inode,
            args.node_size,
            args.node_sha256,
            executable=True,
            expected_mode=args.node_mode,
            expected_uid=args.node_uid,
            expected_mtime_ns_max=args.node_mtime_ns_max,
            max_bytes=256 * 1024 * 1024,
        )
        verified_files.append(node)
        frontend = _verify_file(
            args.frontend_path,
            args.frontend_device,
            args.frontend_inode,
            args.frontend_size,
            args.frontend_sha256,
            executable=False,
            expected_mode=args.frontend_mode,
            expected_uid=args.frontend_uid,
            expected_mtime_ns_max=args.frontend_mtime_ns_max,
            max_bytes=1024 * 1024,
        )
        verified_files.append(frontend)
        deployment = _verify_file(
            args.deployment_path,
            args.deployment_device,
            args.deployment_inode,
            args.deployment_size,
            args.deployment_sha256,
            executable=False,
            expected_mode=args.deployment_mode,
            expected_uid=args.deployment_uid,
            expected_mtime_ns_max=args.deployment_mtime_ns_max,
            max_bytes=65536,
        )
        verified_files.append(deployment)
        artifact_root = _verify_directory(
            args.artifact_root,
            args.artifact_root_device,
            args.artifact_root_inode,
        )
        environment = _validated_environment(args.synthetic_test_context, artifact_root)
        if not args.synthetic_test_context and args.v8_old_space_mib != 1024:
            raise ValueError("v8_limit_mismatch")
        for verified in verified_files:
            _revalidate_verified_file(verified)
        argv = build_target_argv(
            node.path,
            frontend.path,
            deployment.path,
            artifact_root,
            args.v8_old_space_mib,
            args.synthetic_test_context,
        )
        os.execve(node.path, argv, environment)
    except Exception:
        for verified in verified_files:
            try:
                os.close(verified.descriptor)
            except OSError:
                pass
        # Do not leak paths, environment values, or platform exception text.
        os.write(2, b"A2_PROCESS_EXEC_PREFLIGHT_FAILED\n")
        return 125
    return 125


if __name__ == "__main__":
    raise SystemExit(main())
