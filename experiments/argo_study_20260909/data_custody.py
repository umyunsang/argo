"""Trusted development-data preparation. Never print rows or label values."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.io import arff
from sklearn.model_selection import train_test_split


DEFAULT_CUSTODY = Path.home() / ".local/share/argo-study-20260909/custody"
SEED = 20260909
DEVELOPMENT_IDS = {37: (37, 1), 146820: (40983, 2), 31: (31, 1), 146821: (40975, 3)}
APPROVED_HOSTS = {"openml.org", "www.openml.org", "data.openml.org", "archive.ics.uci.edu"}
UCI_SOURCES = {
    40983: (
        "https://archive.ics.uci.edu/dataset/285/wilt",
        "Johnson, B. (2013). Wilt. UCI Machine Learning Repository. DOI:10.24432/C5KS4M",
    ),
    31: (
        "https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data",
        "Hofmann, H. (1994). Statlog (German Credit Data). UCI Machine Learning Repository. DOI:10.24432/C5NC77",
    ),
    40975: (
        "https://archive.ics.uci.edu/dataset/19/car+evaluation",
        "Bohanec, M. (1988). Car Evaluation. UCI Machine Learning Repository. DOI:10.24432/C5JP48",
    ),
}


class CustodyError(Exception):
    """A label-independent failure code, safe for controller output."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def private_directory(path: Path) -> None:
    if path.is_symlink():
        raise CustodyError("CUSTODY_SYMLINK")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.chmod(0o700)


def write_private(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        os.chmod(path, 0o600)
        stream.write(data)


def write_json(path: Path, value: object) -> None:
    write_private(path, (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode())


def validate_source_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in APPROVED_HOSTS:
        raise CustodyError("UNAPPROVED_SOURCE_URL")
    if parsed.username or parsed.password or parsed.port not in {None, 443}:
        raise CustodyError("UNAPPROVED_SOURCE_URL")


class SourceRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_source_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url: str, destination: Path) -> dict:
    validate_source_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": "argo-study-custody/1.0"})
    opener = urllib.request.build_opener(SourceRedirect)
    try:
        with opener.open(request, timeout=45) as response:
            validate_source_url(response.url)
            body = response.read(16_000_001)
            if len(body) > 16_000_000:
                raise CustodyError("SOURCE_SIZE_LIMIT")
            receipt = {
                "requested_url": url,
                "resolved_url": response.url,
                "status": response.status,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "content_type": response.headers.get("Content-Type"),
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
                "bytes": len(body),
                "sha256": sha256(body),
            }
    except urllib.error.HTTPError as exc:
        raise CustodyError(f"SOURCE_HTTP_{exc.code}") from None
    except (urllib.error.URLError, TimeoutError):
        raise CustodyError("SOURCE_NETWORK_FAILURE") from None
    write_private(destination, body)
    return receipt


def development_roster(path: Path) -> list[dict]:
    document = json.loads(path.read_text())
    rows = [row for row in document["rows"] if row["allocation"] == "development"]
    if len(rows) != 4 or {row["task_id"] for row in rows} != set(DEVELOPMENT_IDS):
        raise CustodyError("DEVELOPMENT_ROSTER_MISMATCH")
    for row in rows:
        if (row["data_id"], row["data_version"]) != DEVELOPMENT_IDS[row["task_id"]]:
            raise CustodyError("DEVELOPMENT_VERSION_MISMATCH")
    return rows


def validate_metadata(row: dict, description: dict, task: dict) -> str:
    if (
        int(description["id"]) != row["data_id"]
        or int(description["version"]) != row["data_version"]
        or description["name"] != row["name"]
        or description["default_target_attribute"] != row["target_feature"]
        or description["format"].upper() != "ARFF"
        or description["visibility"] != "public"
        or description["status"] != "active"
        or description["licence"] != "Public"
        or int(task["task_id"]) != row["task_id"]
        or int(task["task_type_id"]) != 1
    ):
        raise CustodyError("SOURCE_METADATA_MISMATCH")
    inputs = {item["name"]: item for item in task["input"]}
    source = inputs["source_data"]["data_set"]
    estimate = inputs["estimation_procedure"]["estimation_procedure"]
    parameters = {item["name"]: item.get("value") for item in estimate["parameter"]}
    if (
        int(source["data_set_id"]) != row["data_id"]
        or source["target_feature"] != row["target_feature"]
        or estimate["type"] != "crossvalidation"
        or parameters.get("number_repeats") != "1"
        or parameters.get("number_folds") != "10"
        or parameters.get("stratified_sampling") != "true"
    ):
        raise CustodyError("TASK_SPLIT_METADATA_MISMATCH")
    return estimate["data_splits_url"]


def parse_arff(data: bytes) -> tuple[pd.DataFrame, object]:
    try:
        array, schema = arff.loadarff(io.StringIO(data.decode("utf-8")))
        frame = pd.DataFrame(array)
        for name in schema.names():
            if schema[name][0] == "nominal":
                frame[name] = frame[name].map(
                    lambda value: value.decode("utf-8") if isinstance(value, bytes) else value
                )
        return frame, schema
    except Exception:
        raise CustodyError("ARFF_PARSE_FAILURE") from None


def outer_indices(split_frame: pd.DataFrame, n_rows: int) -> tuple[np.ndarray, np.ndarray]:
    required = {"repeat", "fold", "rowid", "type"}
    if not required.issubset(split_frame.columns):
        raise CustodyError("SPLIT_SCHEMA_MISMATCH")
    selected = split_frame.loc[(split_frame["repeat"] == 0) & (split_frame["fold"] == 0)]
    if len(selected) != n_rows or set(selected["type"]) != {"TRAIN", "TEST"}:
        raise CustodyError("SPLIT_PARTITION_MISMATCH")
    values = selected["rowid"].to_numpy(dtype=float)
    if not np.isfinite(values).all() or not np.equal(values, np.floor(values)).all():
        raise CustodyError("SPLIT_ROW_ID_INVALID")
    row_ids = values.astype(np.int64)
    if len(set(row_ids)) != n_rows or set(row_ids) != set(range(n_rows)):
        raise CustodyError("SPLIT_COVERAGE_MISMATCH")
    return row_ids[selected["type"].to_numpy() == "TRAIN"], row_ids[selected["type"].to_numpy() == "TEST"]


def export_splits(data_bytes: bytes, split_bytes: bytes, row: dict, destination: Path) -> dict:
    frame, schema = parse_arff(data_bytes)
    splits, _ = parse_arff(split_bytes)
    target = row["target_feature"]
    quality = row["quality"]
    if len(frame) != int(quality["NumberOfInstances"]) or len(frame.columns) != int(quality["NumberOfFeatures"]):
        raise CustodyError("SOURCE_DIMENSIONS_MISMATCH")
    if target not in frame.columns or schema[target][0] != "nominal":
        raise CustodyError("TARGET_SCHEMA_INVALID")
    class_mapping = list(schema[target][1])
    if len(class_mapping) != int(quality["NumberOfClasses"]) or len(set(class_mapping)) != len(class_mapping):
        raise CustodyError("CLASS_SCHEMA_MISMATCH")
    mapped = frame[target].map({label: index for index, label in enumerate(class_mapping)})
    if mapped.isna().any():
        raise CustodyError("TARGET_MISSING_OR_OUTSIDE_PUBLIC_SCHEMA")
    frame[target] = mapped.astype("int64")
    feature_columns = [name for name in schema.names() if name != target]
    numeric_columns = [name for name in feature_columns if schema[name][0] == "numeric"]
    categorical_columns = [name for name in feature_columns if schema[name][0] == "nominal"]
    if set(numeric_columns + categorical_columns) != set(feature_columns):
        raise CustodyError("UNSUPPORTED_FEATURE_SCHEMA")
    for name in categorical_columns:
        if "" in schema[name][1]:
            raise CustodyError("EMPTY_CATEGORY_CONFLICTS_WITH_MISSING_ENCODING")
        frame[name] = frame[name].replace("?", pd.NA).astype("string")
    for name in numeric_columns:
        if np.isinf(frame[name].to_numpy(dtype=float)).any():
            raise CustodyError("NONFINITE_NUMERIC_FEATURE")
    if int(frame.isna().sum().sum()) != int(quality["NumberOfMissingValues"]):
        raise CustodyError("SOURCE_MISSING_COUNT_MISMATCH")
    outer_train, test = outer_indices(splits, len(frame))
    try:
        inner_train, dev = train_test_split(
            outer_train, test_size=0.2, random_state=SEED, shuffle=True,
            stratify=frame.iloc[outer_train][target].to_numpy(),
        )
    except ValueError:
        raise CustodyError("INNER_STRATIFICATION_FAILED") from None
    identities = {"inner_train": inner_train, "dev": dev, "outer_train": outer_train, "test": test}
    expected_classes = set(range(len(class_mapping)))
    for indices in identities.values():
        if set(frame.iloc[indices][target]) != expected_classes:
            raise CustodyError("CLASS_ABSENT_FROM_SPLIT")
    if set(inner_train) & set(dev) or set(inner_train) | set(dev) != set(outer_train):
        raise CustodyError("INNER_PARTITION_MISMATCH")
    columns = feature_columns + [target]
    exports = {
        "inner_train.csv": frame.iloc[inner_train][columns],
        "dev_X.csv": frame.iloc[dev][feature_columns],
        "dev_y.csv": frame.iloc[dev][[target]],
        "outer_train.csv": frame.iloc[outer_train][columns],
        "test_X.csv": frame.iloc[test][feature_columns],
        "test_y.csv": frame.iloc[test][[target]],
    }
    private_directory(destination)
    hashes = {}
    for filename, table in exports.items():
        payload = table.to_csv(index=False, lineterminator="\n", na_rep="").encode()
        write_private(destination / filename, payload)
        hashes[filename] = sha256(payload)
    write_json(destination / "row_identity.json", {name: ids.tolist() for name, ids in identities.items()})
    hashes["row_identity.json"] = sha256((destination / "row_identity.json").read_bytes())
    return {
        "schema": "argo-study-data-custody/v1",
        "task_id": row["task_id"], "data_id": row["data_id"], "data_version": row["data_version"],
        "allocation": "development", "name": row["name"],
        "target_column": target, "feature_columns": feature_columns,
        "numeric_columns": numeric_columns, "categorical_columns": categorical_columns,
        "feature_dtypes": {name: "float64" if name in numeric_columns else "string" for name in feature_columns},
        "class_mapping": class_mapping, "classes": list(range(len(class_mapping))), "n_classes": len(class_mapping),
        "class_schema_source": "Original ARFF nominal target header, before label observations",
        "target_encoding": "Zero-based index in the original ARFF target nominal declaration",
        "missing_encoding": "Empty CSV field; read categorical strings with keep_default_na=False; source zeros unchanged",
        "row_counts": {"source": len(frame), **{name: len(ids) for name, ids in identities.items()}},
        "split": {
            "outer_repeat": 0, "outer_fold": 0, "outer_row_order": "Original split ARFF TRAIN/TEST entry order",
            "inner_test_size": 0.2, "inner_seed": SEED, "inner_shuffle": True,
            "inner_method": "sklearn.model_selection.train_test_split(stratify=outer_train_target)",
        },
        "environment": {
            "python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
            "scipy": scipy.__version__, "scikit_learn": sklearn.__version__,
        },
        "files_sha256": hashes,
        "trust_boundary": "Custody only; permissions do not establish isolation from another process with the same UID",
    }


def prepare_task(row: dict, custody: Path, roster_hash: str) -> dict:
    task_id = row["task_id"]
    if task_id not in DEVELOPMENT_IDS or row["allocation"] != "development":
        raise CustodyError("NON_DEVELOPMENT_TASK_REJECTED")
    final = custody / f"task_{task_id}"
    if final.exists():
        raise CustodyError("TASK_ALREADY_PREPARED_REFUSE_OVERWRITE")
    stage = Path(tempfile.mkdtemp(prefix=f".task_{task_id}-", dir=custody))
    raw = stage / "source"
    private_directory(raw)
    receipts = {}
    for key, url in {
        "data_metadata.json": f"https://www.openml.org/api/v1/json/data/{row['data_id']}",
        "task_metadata.json": f"https://www.openml.org/api/v1/json/task/{task_id}",
    }.items():
        receipts[key] = download(url, raw / key)
    description = json.loads((raw / "data_metadata.json").read_bytes())["data_set_description"]
    task = json.loads((raw / "task_metadata.json").read_bytes())["task"]
    split_url = validate_metadata(row, description, task)
    license_record = {"openml_declared": description["licence"], "visibility": description["visibility"]}
    if row["data_id"] in UCI_SOURCES:
        license_url, attribution = UCI_SOURCES[row["data_id"]]
        receipts["uci_source.html"] = download(license_url, raw / "uci_source.html")
        source_html = (raw / "uci_source.html").read_text()
        if "CC BY 4.0" not in source_html or "creativecommons.org/licenses/by/4.0" not in source_html:
            raise CustodyError("UCI_LICENSE_STATEMENT_NOT_FOUND")
        license_record.update({"original_source_license": "CC-BY-4.0", "source_url": license_url, "attribution": attribution})
    else:
        license_record.update({
            "original_source_license": "Not independently established; legacy UCI URL unavailable",
            "source_url": description["original_data_url"],
            "attribution": "Pima Indians Diabetes; National Institute of Diabetes and Digestive and Kidney Diseases; donor Vincent Sigillito; OpenML data 37 v1",
            "scope": "Local research through public OpenML distribution; no redistribution or unsupported SPDX claim",
        })
    receipts["dataset.arff"] = download(description["url"], raw / "dataset.arff")
    data_bytes = (raw / "dataset.arff").read_bytes()
    if hashlib.md5(data_bytes).hexdigest() != description["md5_checksum"]:
        raise CustodyError("OPENML_SOURCE_MD5_MISMATCH")
    receipts["splits.arff"] = download(split_url, raw / "splits.arff")
    metadata = export_splits(data_bytes, (raw / "splits.arff").read_bytes(), row, stage)
    metadata.update({
        "license": license_record,
        "source_hashes": {filename: receipt["sha256"] for filename, receipt in receipts.items()},
        "source_md5_verified": True, "roster_sha256": roster_hash,
        "utility_sha256": sha256(Path(__file__).read_bytes()),
        "source_notes": [
            "Rows and missing/zero values preserved without repair",
            "Fixed OpenML row-split prediction only; not original-source split or group generalization",
        ],
    })
    if row["data_id"] == 40983:
        metadata["source_notes"].append("UCI headline 4889 conflicts with its 4339+500 file description; OpenML 4839 rows retained")
    write_json(stage / "source_receipts.json", receipts)
    metadata["files_sha256"]["source_receipts.json"] = sha256((stage / "source_receipts.json").read_bytes())
    write_json(stage / "metadata.json", metadata)
    stage.rename(final)
    return {
        "task_id": task_id, "data_id": row["data_id"], "data_version": row["data_version"],
        "status": "PREPARED", "custody_path": str(final), "row_counts": metadata["row_counts"],
        "n_features": len(metadata["feature_columns"]), "n_classes": metadata["n_classes"],
        "metadata_sha256": sha256((final / "metadata.json").read_bytes()),
        "source_hashes": metadata["source_hashes"], "license": license_record,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", type=Path, required=True)
    parser.add_argument("--custody", type=Path, default=DEFAULT_CUSTODY)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--task-id", type=int, action="append", choices=sorted(DEVELOPMENT_IDS))
    args = parser.parse_args()
    os.umask(0o077)
    custody = args.custody.expanduser().absolute()
    if custody.resolve() != DEFAULT_CUSTODY.resolve() or custody.is_symlink():
        raise CustodyError("CUSTODY_MUST_USE_FIXED_PRIVATE_LOCATION")
    private_directory(custody)
    rows = development_roster(args.roster)
    if args.task_id:
        rows = [row for row in rows if row["task_id"] in args.task_id]
    result = {"schema": "argo-study-development-custody-summary/v1", "tasks": [], "labels_or_rows_printed": False}
    for row in rows:
        try:
            summary = prepare_task(row, custody, sha256(args.roster.read_bytes()))
        except CustodyError as exc:
            summary = {"task_id": row["task_id"], "status": "BLOCKED", "reason": str(exc)}
        except Exception as exc:
            summary = {"task_id": row["task_id"], "status": "BLOCKED", "reason": f"UNEXPECTED_{type(exc).__name__}"}
        result["tasks"].append(summary)
        print(json.dumps(summary, ensure_ascii=False), flush=True)
    result["all_prepared"] = all(task["status"] == "PREPARED" for task in result["tasks"])
    write_json(args.summary, result)
    return 0 if result["all_prepared"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CustodyError as error:
        print(json.dumps({"status": "BLOCKED", "reason": str(error)}))
        raise SystemExit(1) from None
