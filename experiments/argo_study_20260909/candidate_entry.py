"""Sandbox-only candidate entry. This module contains no private scorer."""
from __future__ import annotations

import json
import os
import random
import sys
import types
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

SENTINEL = "__ARGO_MISSING_20260909__"


def features(frame: pd.DataFrame, schema: dict) -> pd.DataFrame:
    if list(frame.columns) != schema["feature_columns"]:
        raise ValueError("FEATURE_SCHEMA")
    result = frame.replace("", pd.NA).copy()
    for name in schema["numeric_columns"]:
        result[name] = pd.to_numeric(result[name], errors="raise").astype(float)
        if np.isinf(result[name]).any():
            raise ValueError("NUMERIC_NONFINITE")
    for name in schema["categorical_columns"]:
        result[name] = result[name].astype("string")
    return result


class BaselineModel:
    def __init__(self, config: dict):
        self.config = config

    def prepare(self, frame: pd.DataFrame) -> pd.DataFrame:
        frame = features(frame, self.config)
        for name in self.config["categorical_columns"]:
            if frame[name].eq(SENTINEL).any():
                raise ValueError("RESERVED_SENTINEL")
            frame[name] = frame[name].fillna(SENTINEL).astype(object)
        return frame

    def fit(self, frame: pd.DataFrame, labels: np.ndarray) -> BaselineModel:
        frame = self.prepare(frame)
        transforms = []
        if self.config["numeric_columns"]:
            transforms.append(("numeric", SimpleImputer(strategy="median", keep_empty_features=True), self.config["numeric_columns"]))
        if self.config["categorical_columns"]:
            categories = [sorted(set(frame[name]) | {SENTINEL}) for name in self.config["categorical_columns"]]
            transforms.append(("categorical", OneHotEncoder(categories=categories, handle_unknown="ignore", sparse_output=True), self.config["categorical_columns"]))
        self.pipeline = Pipeline([
            ("preprocessing", ColumnTransformer(transforms, sparse_threshold=0.3)),
            ("classifier", RandomForestClassifier(**self.config["model_parameters"])),
        ])
        self.pipeline.fit(frame, labels)
        return self

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        return self.pipeline.predict(self.prepare(frame))


def baseline_fit(train_X: pd.DataFrame, train_y: np.ndarray, frozen_config: dict) -> BaselineModel:
    return BaselineModel(frozen_config).fit(train_X, train_y)


def run(stage: str, app: Path, data: Path, output: Path) -> None:
    schema = json.loads((app / "public.json").read_text())
    config = json.loads((app / "config.json").read_text())
    random.seed(20260909)
    np.random.seed(20260909)
    solution = types.ModuleType("solution")
    solution.__file__ = str(app / "solution.py")
    sys.modules["solution"] = solution
    exec(compile((app / "solution.py").read_bytes(), solution.__file__, "exec"), solution.__dict__)
    if stage == "fit":
        frame = pd.read_csv(data / "train.csv", dtype="string", keep_default_na=False)
        if list(frame.columns) != schema["feature_columns"] + [schema["target_column"]]:
            raise ValueError("TRAIN_SCHEMA")
        labels = pd.to_numeric(frame.pop(schema["target_column"]), errors="raise").to_numpy(dtype=np.int64)
        model = solution.fit(features(frame, schema), labels, config)
        if not callable(getattr(model, "predict", None)):
            raise ValueError("PREDICT_INTERFACE")
        joblib.dump(model, output / "model.joblib", compress=0)
    elif stage == "predict":
        model = joblib.load(data / "model.joblib")
        frame = pd.read_csv(data / "features.csv", dtype="string", keep_default_na=False)
        predicted = np.asarray(model.predict(features(frame, schema)))
        if predicted.ndim != 1 or len(predicted) != len(frame) or predicted.dtype.kind not in "iuf":
            raise ValueError("PREDICTION_SHAPE_OR_TYPE")
        if not np.isfinite(predicted).all() or not np.equal(predicted, np.floor(predicted)).all():
            raise ValueError("PREDICTION_NONFINITE_OR_FRACTIONAL")
        if not np.isin(predicted, schema["classes"]).all():
            raise ValueError("PREDICTION_CLASS")
        (output / "predictions.json").write_text(json.dumps(predicted.astype(int).tolist(), allow_nan=False))
    else:
        raise ValueError("UNKNOWN_STAGE")


if __name__ == "__main__":
    try:
        run(sys.argv[1], Path("/app"), Path("/data"), Path("/output"))
    except BaseException:
        # The host discards all sandbox streams; this code is never evidence.
        os._exit(42)
