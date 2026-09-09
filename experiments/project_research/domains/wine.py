"""UCI Wine Quality grouped custody and exploratory prediction experiment."""
from __future__ import annotations

import csv
import io
import json
import math
import os
import random
import time
import urllib.request
import zipfile
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from threadpoolctl import threadpool_limits

from .common import DomainError, EventSink, digest, emit, file_digest, json_bytes, read_regular, write_new

SOURCE_URL = "https://archive.ics.uci.edu/static/public/186/wine+quality.zip"
SOURCE_PAGE = "https://archive.ics.uci.edu/dataset/186/wine+quality"
SOURCE_SHA256 = "3ed56667f4b828242bd732d7d1dd7f2861e54432239d7fa63877014cbb0304d4"
MEMBER_SHA256 = {
    "winequality-red.csv": "4a402cf041b025d4566d954c3b9ba8635a3a8a01e039005d97d6a710278cf05e",
    "winequality-white.csv": "76c3f809815c17c07212622f776311faeb31e87610d52c26d87d6e361b169836",
}
FEATURES = (
    "fixed acidity", "volatile acidity", "citric acid", "residual sugar", "chlorides",
    "free sulfur dioxide", "total sulfur dioxide", "density", "pH", "sulphates", "alcohol",
)
HEADER = ("row_id", "color", "group_id", *FEATURES, "quality")
PARTITIONS = ("train", "dev", "final", "future")


@dataclass(frozen=True)
class WineRow:
    row_id: str
    color: str
    features: tuple[str, ...]
    quality: str

    @property
    def group_id(self) -> str:
        # Color and target are excluded: identical physicochemical inputs stay together.
        canonical = [str(Decimal(value).normalize()) if Decimal(value) else "0" for value in self.features]
        return digest(json.dumps(canonical, separators=(",", ":")).encode())


def parse_source(data: bytes, color: str) -> list[WineRow]:
    if color not in {"red", "white"}:
        raise DomainError("unknown wine color")
    reader = csv.reader(io.StringIO(data.decode("utf-8")), delimiter=";", strict=True)
    if tuple(next(reader, ())) != (*FEATURES, "quality"):
        raise DomainError("wine source schema mismatch")
    rows: list[WineRow] = []
    for index, values in enumerate(reader):
        if len(values) != 12 or index >= 10000:
            raise DomainError("wine source row shape or count mismatch")
        try:
            numbers = [Decimal(value) for value in values]
        except InvalidOperation as error:
            raise DomainError("wine source has a nonnumeric field") from error
        if any(not value.is_finite() for value in numbers):
            raise DomainError("wine source has a nonfinite field")
        if not 0 <= numbers[-1] <= 10 or numbers[-1] != numbers[-1].to_integral_value():
            raise DomainError("wine quality is not an integer in [0, 10]")
        rows.append(WineRow(f"{color}-{index:05d}", color, tuple(values[:-1]), values[-1]))
    if not rows:
        raise DomainError("empty wine source")
    return rows


def partition_rows(rows: list[WineRow], seed: int) -> dict[str, list[WineRow]]:
    if len({row.row_id for row in rows}) != len(rows):
        raise DomainError("duplicate wine row identity")
    groups = sorted({row.group_id for row in rows})
    if len(groups) < 20:
        raise DomainError("insufficient unique input groups")
    random.Random(seed).shuffle(groups)
    boundaries = (int(len(groups) * 0.6), int(len(groups) * 0.8), int(len(groups) * 0.9))
    labels = {
        group: PARTITIONS[sum(index >= boundary for boundary in boundaries)]
        for index, group in enumerate(groups)
    }
    split = {name: [row for row in rows if labels[row.group_id] == name] for name in PARTITIONS}
    for name, selected in split.items():
        if {row.color for row in selected} != {"red", "white"}:
            raise DomainError(f"split {name} lacks a color; choose a new preregistered split seed")
    return split


def encode_rows(rows: list[WineRow]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(HEADER)
    writer.writerows((row.row_id, row.color, row.group_id, *row.features, row.quality) for row in rows)
    return output.getvalue().encode()


def disjoint_roots(worker_root: Path, evaluator_root: Path) -> tuple[Path, Path]:
    paths = (Path(worker_root), Path(evaluator_root))
    for path in paths:
        if path.exists() or path.is_symlink():
            raise DomainError("custody output already exists")
        if not path.parent.is_dir():
            raise DomainError("custody output parent must exist")
        if any(parent.is_symlink() for parent in [path, *path.parents]):
            raise DomainError("custody path contains a symlink")
    worker, evaluator = (path.resolve() for path in paths)
    if worker == evaluator or worker in evaluator.parents or evaluator in worker.parents:
        raise DomainError("worker and evaluator roots must be separate nonnested directories")
    return worker, evaluator


def prepare_wine(worker_root: Path, evaluator_root: Path, seed: int,
                 archive_path: Path | None = None) -> dict[str, object]:
    worker, evaluator = disjoint_roots(worker_root, evaluator_root)
    if archive_path is None:
        with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:
            data = response.read(2 * 1024 * 1024 + 1)
    else:
        data = read_regular(archive_path, 2 * 1024 * 1024)
    if digest(data) != SOURCE_SHA256:
        raise DomainError("UCI archive identity changed; review source before proceeding")
    rows: list[WineRow] = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for color in ("red", "white"):
            name = f"winequality-{color}.csv"
            member = archive.read(name)
            if digest(member) != MEMBER_SHA256[name]:
                raise DomainError("wine source member identity mismatch")
            rows.extend(parse_source(member, color))
    if sum(row.color == "red" for row in rows) != 1599 or len(rows) != 6497:
        raise DomainError("UCI red/white source row counts changed")
    split = partition_rows(rows, seed)
    files = {f"{name}.csv": encode_rows(selected) for name, selected in split.items()}
    for path in (worker, evaluator):
        path.mkdir(mode=0o700)
        os.chmod(path, 0o700)
    for name in ("train", "dev"):
        write_new(worker / f"{name}.csv", files[f"{name}.csv"])
    for name in ("final", "future"):
        write_new(evaluator / f"{name}.csv", files[f"{name}.csv"])
    write_new(evaluator / "source.zip", data)
    public = {
        "schema_version": "project-research-wine-worker-data/v1",
        "source": {"url": SOURCE_PAGE, "download_url": SOURCE_URL,
                   "archive_sha256": SOURCE_SHA256, "member_sha256": MEMBER_SHA256,
                   "doi": "10.24432/C56S3T", "license": "CC-BY-4.0",
                   "attribution": "Cortez, Cerdeira, Almeida, Matos and Reis (2009), UCI Wine Quality"},
        "features": list(FEATURES),
        "split_rule": "60/20/10/10 percent of unique canonical 11-feature groups; all colors grouped together",
        "split_seed_custody": "evaluator only",
        "files": {name: {"sha256": digest(files[name]), "bytes": len(files[name])}
                  for name in ("train.csv", "dev.csv")},
        "counts": {name: {color: sum(row.color == color for row in split[name])
                          for color in ("red", "white")} for name in ("train", "dev")},
        "holdout_access": "final/future/raw source not worker inputs; controller must enforce mounts and network policy",
        "public_source_limit": "Public dataset provenance does not itself guarantee label secrecy against reacquisition.",
    }
    private = {
        "schema_version": "project-research-wine-evaluator-data/v1", "seed": seed,
        "all_files": {name: {"sha256": digest(contents), "bytes": len(contents)}
                      for name, contents in files.items()},
        "partition_group_sha256": {name: digest(json_bytes(sorted({row.group_id for row in selected})))
                                   for name, selected in split.items()},
        "counts": {name: {color: sum(row.color == color for row in selected)
                          for color in ("red", "white")} for name, selected in split.items()},
        "cross_partition_group_overlap": 0,
    }
    write_new(worker / "manifest.json", json_bytes(public))
    write_new(evaluator / "manifest.json", json_bytes(private))
    return {"worker_manifest": public, "evaluator_manifest_sha256": digest(json_bytes(private)),
            "cross_partition_group_overlap": 0, "evaluator_values_disclosed": False}


def read_partition(path: Path) -> list[WineRow]:
    reader = csv.reader(io.StringIO(read_regular(path).decode()), strict=True)
    if tuple(next(reader, ())) != HEADER:
        raise DomainError("prepared wine schema mismatch")
    result: list[WineRow] = []
    for values in reader:
        if len(values) != len(HEADER):
            raise DomainError("prepared wine row shape mismatch")
        row = WineRow(values[0], values[1], tuple(values[3:-1]), values[-1])
        try:
            finite = all(math.isfinite(float(value)) for value in [*row.features, row.quality])
            group_matches = row.group_id == values[2]
        except (ValueError, InvalidOperation) as error:
            raise DomainError("prepared wine numeric field mismatch") from error
        if row.color not in {"red", "white"} or not finite or not group_matches:
            raise DomainError("prepared wine identity or value mismatch")
        if not 0 <= float(row.quality) <= 10:
            raise DomainError("prepared wine target range mismatch")
        result.append(row)
    if not result or len({row.row_id for row in result}) != len(result):
        raise DomainError("empty partition or duplicate row identity")
    return result


def load_worker(root: Path) -> tuple[list[WineRow], list[WineRow], dict[str, object]]:
    root = Path(root)
    manifest = json.loads(read_regular(root / "manifest.json"))
    if manifest.get("schema_version") != "project-research-wine-worker-data/v1":
        raise DomainError("wine worker manifest mismatch")
    if set(path.name for path in root.iterdir()) != {"train.csv", "dev.csv", "manifest.json"}:
        raise DomainError("worker input must contain only train/dev and manifest")
    for name in ("train.csv", "dev.csv"):
        if file_digest(root / name) != manifest["files"][name]["sha256"]:
            raise DomainError("wine worker file hash mismatch")
    train, dev = read_partition(root / "train.csv"), read_partition(root / "dev.csv")
    if {row.group_id for row in train} & {row.group_id for row in dev}:
        raise DomainError("identical feature group crosses train/dev")
    if {row.row_id for row in train} & {row.row_id for row in dev}:
        raise DomainError("row identity crosses train/dev")
    return train, dev, manifest


def score_predictions(rows: list[WineRow], predicted: np.ndarray) -> dict[str, float]:
    if predicted.shape != (len(rows),) or not np.isfinite(predicted).all():
        raise DomainError("wine predictions are nonfinite or misaligned")
    actual = np.array([float(row.quality) for row in rows])
    scores: dict[str, float] = {}
    for color in ("red", "white"):
        selected = np.array([row.color == color for row in rows])
        if not selected.any():
            raise DomainError("wine evaluation lacks a color")
        score = float(mean_absolute_error(actual[selected], predicted[selected]))
        manual = math.fsum(abs(float(a) - float(p)) for a, p in zip(actual[selected], predicted[selected])) / int(selected.sum())
        if not math.isclose(score, manual, rel_tol=1e-13, abs_tol=1e-13):
            raise DomainError("independent wine MAE calculation disagrees")
        scores[f"{color}_mae"] = score
    scores["equal_weight_mae"] = (scores["red_mae"] + scores["white_mae"]) / 2
    scores["row_weight_mae"] = float(mean_absolute_error(actual, predicted))
    return scores


def fit_predict(train: list[WineRow], target: list[WineRow], method: str, seed: int,
                trees: int = 256) -> tuple[np.ndarray, dict[str, object]]:
    features = np.array([[float(value) for value in row.features] for row in train])
    targets = np.array([float(row.quality) for row in train])
    test_features = np.array([[float(value) for value in row.features] for row in target])
    colors = np.array([row.color == "white" for row in train])
    test_colors = np.array([row.color == "white" for row in target])
    config: dict[str, object]
    if method == "pooled_histogram_boosting":
        config = {"loss": "squared_error", "max_iter": 250, "learning_rate": 0.05,
                  "max_leaf_nodes": 31, "l2_regularization": 1.0, "early_stopping": False,
                  "random_state": seed}
        model = HistGradientBoostingRegressor(**config)
        model.fit(np.column_stack((features, colors)), targets)
        predicted = model.predict(np.column_stack((test_features, test_colors)))
    elif method in {"pooled_extra_trees", "separate_color_extra_trees"}:
        config = {"n_estimators": trees, "min_samples_leaf": 2, "max_features": 1.0,
                  "criterion": "squared_error", "n_jobs": 1, "random_state": seed}
        if method == "pooled_extra_trees":
            model = ExtraTreesRegressor(**config)
            model.fit(np.column_stack((features, colors)), targets)
            predicted = model.predict(np.column_stack((test_features, test_colors)))
        else:
            predicted = np.empty(len(target))
            for color in (False, True):
                selected = colors == color
                test_selected = test_colors == color
                if not selected.any():
                    raise DomainError("color-specific training lacks a color")
                model = ExtraTreesRegressor(**config)
                model.fit(features[selected], targets[selected])
                if test_selected.any():
                    predicted[test_selected] = model.predict(test_features[test_selected])
    else:
        raise DomainError("unknown frozen wine method")
    return np.asarray(predicted), {"method": method, "estimator_parameters": config,
                                  "prediction_transform": "none", "train_color_feature": method != "separate_color_extra_trees"}


def run_wine(worker_root: Path, artifact_root: Path, seed: int,
             sink: EventSink | None = None) -> dict[str, object]:
    train, dev, manifest = load_worker(worker_root)
    artifact_root.mkdir(mode=0o700)
    methods = ("pooled_histogram_boosting", "pooled_extra_trees", "separate_color_extra_trees")
    observations: dict[str, dict[str, object]] = {}
    with threadpool_limits(limits=1):
        for method in methods:
            started = time.perf_counter()
            predicted, specification = fit_predict(train, dev, method, seed)
            elapsed = time.perf_counter() - started
            metrics = score_predictions(dev, predicted)
            output = io.StringIO(newline="")
            writer = csv.writer(output, lineterminator="\n")
            writer.writerow(("row_id", "prediction"))
            writer.writerows((row.row_id, format(float(value), ".17g")) for row, value in zip(dev, predicted))
            path = artifact_root / f"{method}.predictions.csv"
            write_new(path, output.getvalue().encode())
            observations[method] = {"metrics": metrics, "fit_predict_seconds": elapsed,
                                    "specification": specification, "prediction_file": path.name,
                                    "prediction_sha256": file_digest(path)}
            emit(sink, "hypothesis_observation" if method == methods[-1] else "baseline_observation",
                 domain="wine", method=method, metrics=metrics)
    baseline = min(methods[:2], key=lambda name: observations[name]["metrics"]["equal_weight_mae"])
    alternative = methods[-1]
    baseline_mae = observations[baseline]["metrics"]["equal_weight_mae"]
    alternative_mae = observations[alternative]["metrics"]["equal_weight_mae"]
    return {
        "research_question": "Does fitting color-specific tree ensembles improve equal-color MAE over strong pooled nonlinear predictors?",
        "hypothesis": "Color-specific ExtraTrees fits reduce equal-color development MAE.",
        "source": manifest["source"], "input_manifest_sha256": file_digest(worker_root / "manifest.json"),
        "input_files": manifest["files"], "sample_counts": manifest["counts"],
        "split_integrity": {"train_dev_input_group_overlap": 0, "final_future_read": False},
        "observations": observations, "strongest_observed_development_baseline": baseline,
        "baseline_selection": "Exploratory minimum of two development MAEs; not hidden-test selection or unbiased inferential estimate.",
        "hypothesis_result": {"alternative": alternative, "mae_difference_alternative_minus_baseline": alternative_mae - baseline_mae,
                              "development_direction_supported": alternative_mae < baseline_mae,
                              "final_generalization": "UNASSESSED"},
        "verification": {"mae_independent_arithmetic": True, "independent_retraining": "REQUIRED_SEPARATE_EXECUTION"},
        "limitations": ["One grouped development split and fixed configurations.",
                        "Color-specific fits also alter sample size and total tree count; this is an operating alternative comparison.",
                        "Public-source holdouts require external custody; no external-validity or model SOTA claim."],
    }
