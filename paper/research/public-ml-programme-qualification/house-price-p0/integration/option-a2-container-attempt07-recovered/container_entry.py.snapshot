"""Trusted fixed entry point executed inside the sealed HousePrice solution container."""

from __future__ import annotations

import csv
import importlib.util
import math
import os
import resource
from pathlib import Path
from typing import Iterable

import pandas as pd


SOLUTION_PATH = Path("/solution/solution.py")
TRAIN_PATH = Path("/input/train.csv")
FEATURES_PATH = Path("/input/features.csv")
OUTPUT_PATH = Path("/tmp/predictions.csv")


def _load_solution():
    spec = importlib.util.spec_from_file_location("house_price_solution", SOLUTION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("solution_load")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    candidate = getattr(module, "fit_predict", None)
    if not callable(candidate):
        raise RuntimeError("solution_api")
    return candidate


def _finite_predictions(values: Iterable[object], expected_rows: int) -> list[float]:
    try:
        result = list(values)
    except TypeError as error:
        raise RuntimeError("prediction_shape") from error
    if len(result) != expected_rows:
        raise RuntimeError("prediction_length")
    converted: list[float] = []
    for value in result:
        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise RuntimeError("prediction_numeric") from error
        if not math.isfinite(number):
            raise RuntimeError("prediction_finite")
        converted.append(number)
    return converted


def main() -> int:
    # Set both limits before loading arbitrary module code. A non-root solution
    # may lower, but cannot raise, the inherited hard limit.
    output_limit = int(os.environ["ARGO_OUTPUT_BYTES"])
    resource.setrlimit(resource.RLIMIT_FSIZE, (output_limit, output_limit))
    train = pd.read_csv(TRAIN_PATH, dtype={"Id": "string"})
    features = pd.read_csv(FEATURES_PATH, dtype={"Id": "string"})
    if "Id" not in train.columns or "SalePrice" not in train.columns:
        raise RuntimeError("train_schema")
    if "Id" not in features.columns or "SalePrice" in features.columns:
        raise RuntimeError("features_schema")

    predict = _load_solution()
    predictions = _finite_predictions(predict(train, features), len(features))

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("Id", "SalePrice"))
        for identifier, prediction in zip(features["Id"].astype(str), predictions, strict=True):
            writer.writerow((identifier, repr(prediction)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # The host deliberately receives only a typed status, never this detail.
        raise SystemExit(1)
