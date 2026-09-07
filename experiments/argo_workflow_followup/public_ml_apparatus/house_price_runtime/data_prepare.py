"""Trusted source-compatible data split; never trains, scores or prints row values."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import stat
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

import sklearn
from sklearn.model_selection import train_test_split

MAX_INPUT_BYTES = 8_388_608
MAX_ROWS = 10_000
MAX_COLUMNS = 256
MAX_FIELD_BYTES = 8192
OUTPUT_NAMES = frozenset({"train_inner.csv", "dev_features.csv", "dev_targets.csv",
                          "train_outer.csv", "hidden_features.csv", "hidden_targets.csv",
                          "dev_ids.json", "hidden_ids.json"})


class PreparationError(ValueError):
    """Safe status only; no source row, path or parser exception text."""


@dataclass(frozen=True)
class PreparedData:
    files: dict[str, bytes]
    public_manifest: dict[str, object]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_rows(header: list[str], rows: list[list[str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def _load(data: bytes, expected_sha256: str, rows: int, columns: int) -> tuple[list[str], list[list[str]]]:
    if (type(rows) is not int or not 5 <= rows <= MAX_ROWS or
            type(columns) is not int or not 2 <= columns <= MAX_COLUMNS):
        raise PreparationError("CONTRACT")
    if (not isinstance(data, bytes) or not 0 < len(data) <= MAX_INPUT_BYTES or
            not isinstance(expected_sha256, str) or
            not re.fullmatch(r"[a-f0-9]{64}", expected_sha256) or digest(data) != expected_sha256):
        raise PreparationError("INPUT_IDENTITY")
    try:
        reader = csv.reader(io.StringIO(data.decode("utf-8"), newline=""), strict=True)
        header = next(reader)
        if (len(header) != columns or len(set(header)) != columns or
                "Id" not in header or "SalePrice" not in header or
                any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_]{0,127}", value) for value in header)):
            raise PreparationError("INPUT_SCHEMA")
        table: list[list[str]] = []
        ids: set[str] = set()
        id_index, target_index = header.index("Id"), header.index("SalePrice")
        for row in reader:
            if len(table) >= rows or len(row) != columns:
                raise PreparationError("INPUT_ROWS")
            if any(len(value.encode("utf-8")) > MAX_FIELD_BYTES or "\x00" in value for value in row):
                raise PreparationError("INPUT_FIELD")
            row_id = row[id_index]
            if not re.fullmatch(r"[0-9]{1,32}", row_id) or row_id in ids:
                raise PreparationError("INPUT_IDS")
            value = row[target_index]
            if not re.fullmatch(r"[0-9]{1,16}(?:\.[0-9]{1,8})?", value):
                raise PreparationError("INPUT_TARGET")
            target = Decimal(value)
            if not target.is_finite() or target <= 0:
                raise PreparationError("INPUT_TARGET")
            ids.add(row_id)
            table.append(row)
        if len(table) != rows:
            raise PreparationError("INPUT_ROWS")
    except (csv.Error, UnicodeError, StopIteration, InvalidOperation):
        raise PreparationError("INPUT_FORMAT") from None
    return header, table


def prepare_bytes(data: bytes, expected_sha256: str, rows: int, columns: int) -> PreparedData:
    header, table = _load(data, expected_sha256, rows, columns)
    outer_end = int(len(table) * 0.8)
    inner, dev = train_test_split(list(range(outer_end)), test_size=0.25,
                                  random_state=1, shuffle=True, stratify=None)
    groups = {"inner_train": inner, "dev": dev, "outer_train": list(range(outer_end)),
              "hidden": list(range(outer_end, rows))}
    target_index, id_index = header.index("SalePrice"), header.index("Id")
    feature_indices = [index for index in range(columns) if index != target_index]
    feature_header = [header[index] for index in feature_indices]
    files: dict[str, bytes] = {}
    for group, filename in [("inner_train", "train_inner.csv"), ("outer_train", "train_outer.csv")]:
        files[filename] = encode_rows(header, [table[index] for index in groups[group]])
    for group in ["dev", "hidden"]:
        selected = [table[index] for index in groups[group]]
        files[group+"_features.csv"] = encode_rows(feature_header,
            [[row[index] for index in feature_indices] for row in selected])
        files[group+"_targets.csv"] = encode_rows(["Id", "SalePrice"],
            [[row[id_index], row[target_index]] for row in selected])
        files[group+"_ids.json"] = json.dumps([row[id_index] for row in selected],
            ensure_ascii=True, separators=(",", ":")).encode()
    manifest: dict[str, object] = {
        "schema_version": "argo-house-price-prepared-data/v1",
        "source_sha256": digest(data),
        "source_bytes": len(data),
        "counts": {"all": rows, "outer_train": outer_end, "inner_train": len(inner),
                   "dev": len(dev), "hidden": rows-outer_end},
        "columns": header,
        "split": {"outer": "positional_prefix_int_N_times_0.8", "inner_test_size": 0.25,
                  "random_state": 1, "shuffle": True, "stratify": None,
                  "sklearn_version": sklearn.__version__},
        "ordered_id_sha256": {group: digest(json.dumps([table[index][id_index] for index in indices],
            ensure_ascii=True, separators=(",", ":")).encode()) for group, indices in groups.items()},
        "files": {name: {"sha256": digest(contents), "bytes": len(contents)}
                  for name, contents in files.items()},
        "custody": "Training CSVs contain approved training targets. Dev/hidden feature CSVs do not. Targets stay in trusted external custody; hashes are identity, not concealment.",
    }
    return PreparedData(files, manifest)


def write_prepared(prepared: PreparedData, output: Path) -> None:
    if set(prepared.files) != OUTPUT_NAMES:
        raise PreparationError("OUTPUT_CONTRACT")
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise PreparationError("OUTPUT_EXISTS")
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise PreparationError("OUTPUT_PARENT")
    try:
        output.mkdir(mode=0o700)
    except FileExistsError:
        raise PreparationError("OUTPUT_EXISTS") from None
    except OSError:
        raise PreparationError("OUTPUT_IO") from None
    os.chmod(output, 0o700)
    all_files = dict(prepared.files)
    all_files["public_manifest.json"] = (json.dumps(prepared.public_manifest, ensure_ascii=False,
                                                     indent=2)+"\n").encode()
    try:
        for name, contents in all_files.items():
            fd = os.open(output/name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(contents)
                stream.flush()
                os.fsync(stream.fileno())
        fd = os.open(output, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError:
        # Retain incomplete directory for trusted inspection; never silently retry/overwrite.
        raise PreparationError("OUTPUT_IO") from None


def read_source(path: Path) -> bytes:
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or
                    not 0 < before.st_size <= MAX_INPUT_BYTES):
                raise PreparationError("INPUT_FILE")
            data = stream.read(MAX_INPUT_BYTES+1)
            after = os.fstat(stream.fileno())
            if ((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
                    (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)):
                raise PreparationError("INPUT_CHANGED")
        return data
    except OSError:
        raise PreparationError("INPUT_FILE") from None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--columns", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        prepared = prepare_bytes(read_source(args.input), args.sha256, args.rows, args.columns)
        write_prepared(prepared, args.output)
    except PreparationError as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1
    print(json.dumps({"ok": True, "public_manifest": prepared.public_manifest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
