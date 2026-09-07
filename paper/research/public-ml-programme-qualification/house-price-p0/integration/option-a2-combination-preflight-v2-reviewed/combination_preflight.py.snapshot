"""Trusted pre-import gate for one synthetic combination case.

This module imports only the standard library and the reviewed sibling
source_closure module. It never imports or writes the case namespace.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

from source_closure import ClosureError, ClosureLimits, SourceTree, verify_tree

KERNEL = "/Users/um-yunsang/.prime/agent/kernel-venv/bin/python"
PYVENV_CONFIG = Path(KERNEL).parent.parent / "pyvenv.cfg"
DRIVER_MODULE = "experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_driver"
RUNTIME = "experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime"
DRIVER_RELATIVE = RUNTIME + "/combination_driver.py"
FIXTURE_RELATIVE = RUNTIME + "/combination_fixture.py"
ACCEPTANCE_RELATIVE = RUNTIME + "/combination_acceptance.py"
FAUX_RELATIVE = "a2-frontend-probes/a2-combination-frontend.ts"
CONFIG_SCHEMA = "argo-house-price-a2-combination-case-config/v2"
FAILURE = "COMBINATION_PREFLIGHT_INVALID\n"
HEX64 = re.compile(r"[0-9a-f]{64}")
SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
CONFIG_LIMIT = 65_536
NAMESPACE_LIMITS = ClosureLimits(160, 8_388_608, 1_048_576, 8, 4096)
INSTALLED_LIMITS = ClosureLimits(30_000, 268_435_456, 67_108_864, 32, 4096)
CHILD_ENV = {"LANG":"C.UTF-8","LC_ALL":"C.UTF-8","PATH":"/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin","TZ":"UTC"}


class PreflightError(ValueError):
    pass


@dataclass(frozen=True)
class _DirectoryRecord:
    path: Path
    device: int
    inode: int


@dataclass(frozen=True)
class _CaseConfig:
    case_root: Path
    protected_roots: dict[str, _DirectoryRecord]
    namespace_tree: SourceTree
    frontend_seed_tree: SourceTree
    installed_prime_tree: SourceTree
    expected_faux_frontend_sha256: str
    expected_fixture_module_sha256: str
    expected_acceptance_module_sha256: str


def execute_preflight(config_path: Path, expected_sha256: str) -> int:
    try:
        _validate_request(config_path, expected_sha256)
        _check_interpreter()
        initial = _read_config_bytes(config_path, expected_sha256)
        config = _parse_config(initial)
        protected_fds = _open_protected_roots(config)
        namespace_fd: int | None = None
        try:
            _validate_layout(config_path, config)
            _verify_trees_and_members(config)
            namespace_fd = _open_namespace(config.namespace_tree)
            if _read_config_bytes(config_path, expected_sha256) != initial:
                raise PreflightError()
            _revalidate_protected_roots(config, protected_fds)
            os.fchdir(namespace_fd)
        finally:
            if namespace_fd is not None:
                os.close(namespace_fd)
            for descriptor in reversed(protected_fds):
                os.close(descriptor)
        argv = [KERNEL, "-B", "-m", DRIVER_MODULE,
                "--config", str(config_path), "--config-sha256", expected_sha256]
        os.execve(KERNEL, argv, CHILD_ENV)
        raise PreflightError()
    except Exception:
        sys.stderr.write(FAILURE)
        return 2


def fixed_entry_source(config_path: Path, expected_sha256: str) -> str:
    _validate_request(config_path, expected_sha256, require_existing=False)
    return "\n".join([
        f"#!{KERNEL}",
        '"""Fixed root-owned combination preflight entry."""',
        "import sys",
        "from pathlib import Path",
        "from combination_preflight import execute_preflight",
        "",
        "if len(sys.argv) != 1:",
        f"    sys.stderr.write({FAILURE!r})",
        "    raise SystemExit(2)",
        f"raise SystemExit(execute_preflight(Path({str(config_path)!r}), {expected_sha256!r}))",
        "",
    ])


def _validate_request(config_path: Path, expected_sha256: str, require_existing: bool = True) -> None:
    if (not isinstance(config_path, Path) or not config_path.is_absolute() or ".." in config_path.parts or
            type(expected_sha256) is not str or HEX64.fullmatch(expected_sha256) is None):
        raise PreflightError()
    if require_existing:
        try:
            if config_path.resolve(strict=True) != config_path:
                raise PreflightError()
        except (OSError, RuntimeError):
            raise PreflightError() from None


def _check_interpreter() -> None:
    if (sys.executable != KERNEL or type(sys.flags.no_site) is not int or sys.flags.no_site != 1 or
            type(sys.flags.dont_write_bytecode) is not int or sys.flags.dont_write_bytecode != 1):
        raise PreflightError()
    invocation = Path(KERNEL)
    try:
        if not invocation.is_absolute() or ".." in invocation.parts or invocation.parent.resolve(strict=True) != invocation.parent:
            raise PreflightError()
        before = invocation.lstat()
        if not stat.S_ISLNK(before.st_mode):
            raise PreflightError()
        target_text = os.readlink(invocation)
        if not isinstance(target_text, str) or not target_text:
            raise PreflightError()
        resolved = invocation.resolve(strict=True)
        target = resolved.stat()
        if (not stat.S_ISREG(target.st_mode) or not target.st_mode & 0o111 or not os.access(resolved, os.X_OK)):
            raise PreflightError()
        after = invocation.lstat()
        if _identity(before) != _identity(after):
            raise PreflightError()
        _read_regular_shape(PYVENV_CONFIG, CONFIG_LIMIT)
    except PreflightError:
        raise
    except (OSError, RuntimeError, ValueError):
        raise PreflightError() from None


def _read_config_bytes(path: Path, expected_sha256: str) -> bytes:
    data, info = _read_regular(path, CONFIG_LIMIT)
    try:
        parent = path.parent.lstat()
        if (not stat.S_ISDIR(parent.st_mode) or stat.S_ISLNK(parent.st_mode) or
                stat.S_IMODE(parent.st_mode) != 0o700 or parent.st_uid != os.getuid() or
                stat.S_IMODE(info.st_mode) != 0o600 or info.st_uid != os.getuid() or
                hashlib.sha256(data).hexdigest() != expected_sha256):
            raise PreflightError()
    except OSError:
        raise PreflightError() from None
    return data


def _read_regular_shape(path: Path, cap: int) -> bytes:
    data, _ = _read_regular(path, cap)
    return data


def _read_regular(path: Path, cap: int) -> tuple[bytes, os.stat_result]:
    if (not isinstance(path, Path) or not path.is_absolute() or ".." in path.parts or
            type(cap) is not int or cap <= 0):
        raise PreflightError()
    descriptors: list[int] = []
    try:
        if path.resolve(strict=True) != path:
            raise PreflightError()
        parent = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(parent)
        for part in path.parts[1:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            descriptors.append(parent)
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or not 0 < before.st_size <= cap:
                raise PreflightError()
            data = stream.read(cap + 1)
            after = os.fstat(stream.fileno())
            named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            if (_identity(before) != _identity(after) or _identity(after) != _identity(named) or
                    len(data) != before.st_size):
                raise PreflightError()
        return data, before
    except PreflightError:
        raise
    except (OSError, RuntimeError, ValueError):
        raise PreflightError() from None
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _parse_config(data: bytes) -> _CaseConfig:
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except (ValueError, UnicodeError, RecursionError):
        raise PreflightError() from None
    keys = {"schema_version", "case_root", "protected_roots", "namespace_tree", "frontend_seed_tree",
            "installed_prime_tree", "expected_faux_frontend_sha256", "expected_fixture_module_sha256",
            "expected_acceptance_module_sha256"}
    if type(value) is not dict or set(value) != keys or value["schema_version"] != CONFIG_SCHEMA:
        raise PreflightError()
    if type(value["case_root"]) is not str:
        raise PreflightError()
    hashes = [value[name] for name in ("expected_faux_frontend_sha256", "expected_fixture_module_sha256",
                                      "expected_acceptance_module_sha256")]
    if any(type(item) is not str or HEX64.fullmatch(item) is None for item in hashes):
        raise PreflightError()
    return _CaseConfig(
        Path(value["case_root"]),
        _protected_roots(value["protected_roots"]),
        _source_tree(value["namespace_tree"]),
        _source_tree(value["frontend_seed_tree"]),
        _source_tree(value["installed_prime_tree"]),
        hashes[0], hashes[1], hashes[2],
    )


def _protected_roots(value: object) -> dict[str, _DirectoryRecord]:
    roles = {"raw", "auth", "profile", "controller", "public"}
    if type(value) is not dict or set(value) != roles:
        raise PreflightError()
    result: dict[str, _DirectoryRecord] = {}
    for role in sorted(roles):
        record = value[role]
        if (type(record) is not dict or set(record) != {"path", "device", "inode"} or
                type(record["path"]) is not str or type(record["device"]) is not int or
                type(record["inode"]) is not int or not 0 <= record["device"] <= 2**64 - 1 or
                not 1 <= record["inode"] <= 2**64 - 1):
            raise PreflightError()
        result[role] = _DirectoryRecord(Path(record["path"]), record["device"], record["inode"])
    return result


def _source_tree(value: object) -> SourceTree:
    expected = {item.name for item in fields(SourceTree)}
    if type(value) is not dict or set(value) != expected:
        raise PreflightError()
    try:
        return SourceTree(**value)
    except TypeError:
        raise PreflightError() from None


def _validate_layout(config_path: Path, config: _CaseConfig) -> None:
    roots = [Path(config.namespace_tree.root), Path(config.frontend_seed_tree.root),
             Path(config.installed_prime_tree.root)]
    for index, left in enumerate(roots):
        for right in roots[index + 1:]:
            if _overlaps(left, right):
                raise PreflightError()
    tcb = Path(__file__).resolve().parent
    for root in roots:
        if _overlaps(root, tcb) or root == config_path or root in config_path.parents:
            raise PreflightError()
    if tcb == config_path.parent or tcb in config_path.parents:
        raise PreflightError()
    case = config.case_root
    if (not case.is_absolute() or ".." in case.parts or SAFE_NAME.fullmatch(case.name) is None or
            os.path.lexists(case) or _overlaps(case, tcb) or
            any(_overlaps(case, root) for root in roots) or
            any(_overlaps(case, item.path) for item in config.protected_roots.values()) or
            case == config_path or case in config_path.parents):
        raise PreflightError()
    try:
        parent = case.parent
        if parent.resolve(strict=True) != parent:
            raise PreflightError()
        info = parent.lstat()
        if (not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or
                stat.S_IMODE(info.st_mode) != 0o700 or info.st_uid != os.getuid()):
            raise PreflightError()
    except (OSError, RuntimeError):
        raise PreflightError() from None


def _open_protected_roots(config: _CaseConfig) -> list[int]:
    descriptors: list[int] = []
    try:
        for role in ("raw", "auth", "profile", "controller", "public"):
            record = config.protected_roots[role]
            path = record.path
            if (not path.is_absolute() or ".." in path.parts or path.resolve(strict=True) != path):
                raise PreflightError()
            descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            descriptors.append(descriptor)
            _validate_protected_fd(descriptor, record)
        return descriptors
    except PreflightError:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise
    except (OSError, RuntimeError, ValueError):
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise PreflightError() from None


def _revalidate_protected_roots(config: _CaseConfig, descriptors: list[int]) -> None:
    if type(descriptors) is not list or len(descriptors) != 5:
        raise PreflightError()
    for descriptor, role in zip(descriptors, ("raw", "auth", "profile", "controller", "public")):
        _validate_protected_fd(descriptor, config.protected_roots[role])


def _validate_protected_fd(descriptor: int, record: _DirectoryRecord) -> None:
    try:
        opened = os.fstat(descriptor)
        named = record.path.lstat()
        if (not stat.S_ISDIR(opened.st_mode) or not stat.S_ISDIR(named.st_mode) or
                stat.S_ISLNK(named.st_mode) or opened.st_uid != os.getuid() or named.st_uid != os.getuid() or
                (opened.st_dev, opened.st_ino) != (record.device, record.inode) or
                _identity(opened) != _identity(named)):
            raise PreflightError()
    except PreflightError:
        raise
    except OSError:
        raise PreflightError() from None


def _verify_trees_and_members(config: _CaseConfig) -> None:
    try:
        verify_tree(Path(config.namespace_tree.root), config.namespace_tree, NAMESPACE_LIMITS)
        verify_tree(Path(config.frontend_seed_tree.root), config.frontend_seed_tree, NAMESPACE_LIMITS)
        verify_tree(Path(config.installed_prime_tree.root), config.installed_prime_tree, INSTALLED_LIMITS)
    except ClosureError:
        raise PreflightError() from None
    namespace = Path(config.namespace_tree.root)
    frontend = Path(config.frontend_seed_tree.root)
    _read_member(namespace, DRIVER_RELATIVE, None)
    _read_member(namespace, FIXTURE_RELATIVE, config.expected_fixture_module_sha256)
    _read_member(namespace, ACCEPTANCE_RELATIVE, config.expected_acceptance_module_sha256)
    _read_member(frontend, FAUX_RELATIVE, config.expected_faux_frontend_sha256)


def _read_member(root: Path, relative: str, expected_sha256: str | None) -> bytes:
    path = root / relative
    data, _ = _read_regular(path, 1_048_576)
    if expected_sha256 is not None and hashlib.sha256(data).hexdigest() != expected_sha256:
        raise PreflightError()
    return data


def _open_namespace(tree: SourceTree) -> int:
    root = Path(tree.root)
    try:
        descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        opened = os.fstat(descriptor)
        named = root.lstat()
        if (not stat.S_ISDIR(opened.st_mode) or stat.S_IMODE(opened.st_mode) != 0o700 or
                opened.st_uid != os.getuid() or (opened.st_dev, opened.st_ino) != (tree.root_device, tree.root_inode) or
                _identity(opened) != _identity(named)):
            os.close(descriptor)
            raise PreflightError()
        return descriptor
    except PreflightError:
        raise
    except OSError:
        raise PreflightError() from None


def _overlaps(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def _identity(value: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise PreflightError()
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise PreflightError()
