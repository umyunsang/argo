"""Pure ML/scoring apparatus for the 2026-09-09 study, not an isolation boundary.

Only a trusted controller may persist selection state, admit refits, or call the
private-label scorer. Generated code, fitted artifacts and finalizer output must
be isolated by the caller. Exceptions contain label-independent status codes.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import platform
from collections import UserList
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Mapping, Sequence

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


SEED = 20260909
MISSING_SENTINEL = "__ARGO_MISSING_20260909__"
RF_PARAMETERS = {
    "n_estimators": 100,
    "criterion": "gini",
    "max_depth": None,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "min_weight_fraction_leaf": 0.0,
    "max_features": "sqrt",
    "max_leaf_nodes": None,
    "min_impurity_decrease": 0.0,
    "bootstrap": True,
    "oob_score": False,
    "n_jobs": 2,
    "random_state": SEED,
    "verbose": 0,
    "warm_start": False,
    "class_weight": None,
    "ccp_alpha": 0.0,
    "max_samples": None,
    "monotonic_cst": None,
}
PREPROCESSING = {
    "numeric_imputation": "train_median",
    "all_missing_numeric_fill": 0.0,
    "nominal_missing_sentinel": MISSING_SENTINEL,
    "nominal_categories": "train_observed_plus_reserved_missing",
    "unknown_nominal": "all_zero",
    "numeric_dtype": "float64",
    "one_hot_dtype": "float64",
    "one_hot_sparse_output": True,
    "column_transformer_sparse_threshold": 0.3,
    "remainder": "drop",
}


class ContractError(ValueError):
    """Public status independent of private target contents."""


class PrivateScoringError(RuntimeError):
    """Trusted failure: caller must preserve UNKNOWN rather than assign zero."""


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def content_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_sha256(path: str | Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def environment_manifest() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "system": platform.system(),
        "machine": platform.machine(),
        "scikit_learn": sklearn.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "joblib": joblib.__version__,
    }


def _validate_classes(classes: Sequence[int]) -> tuple[int, ...]:
    values = tuple(classes)
    if len(values) < 2 or any(type(value) is not int for value in values):
        raise ContractError("INVALID_CLASS_SCHEMA")
    if values != tuple(range(len(values))):
        raise ContractError("INVALID_CLASS_SCHEMA")
    return values


def canonical_config(metadata: Mapping[str, object]) -> dict[str, object]:
    """Construct the fixed RF baseline from public custody schema only."""
    required = ("feature_columns", "numeric_columns", "categorical_columns", "class_mapping", "target_column")
    if any(name not in metadata for name in required):
        raise ContractError("MISSING_PUBLIC_SCHEMA")
    config = {
        "schema": "study-canonical-rf/v1",
        "feature_columns": metadata["feature_columns"],
        "numeric_columns": metadata["numeric_columns"],
        "categorical_columns": metadata["categorical_columns"],
        "class_mapping": metadata["class_mapping"],
        "target_column": metadata["target_column"],
        "seed": SEED,
        "model": "RandomForestClassifier",
        "model_parameters": RF_PARAMETERS,
        "preprocessing": PREPROCESSING,
    }
    config = json.loads(canonical_json(config))
    _validate_config(config)
    if "classes" in metadata:
        classes = _validate_classes(metadata["classes"])
        if len(classes) != len(config["class_mapping"]):
            raise ContractError("INVALID_CLASS_SCHEMA")
    return config


def _validate_config(config: Mapping[str, object]) -> None:
    expected_keys = {
        "schema", "feature_columns", "numeric_columns", "categorical_columns",
        "class_mapping", "target_column", "seed", "model", "model_parameters", "preprocessing",
    }
    if set(config) != expected_keys or config["schema"] != "study-canonical-rf/v1":
        raise ContractError("INVALID_CONFIG")
    columns = config["feature_columns"]
    numeric = config["numeric_columns"]
    categorical = config["categorical_columns"]
    mapping = config["class_mapping"]
    for names in (columns, numeric, categorical, mapping):
        if not isinstance(names, list) or any(not isinstance(name, str) or not name for name in names):
            raise ContractError("INVALID_PUBLIC_SCHEMA")
        if len(set(names)) != len(names):
            raise ContractError("INVALID_PUBLIC_SCHEMA")
    if not columns or set(numeric) & set(categorical) or set(columns) != set(numeric + categorical):
        raise ContractError("INVALID_FEATURE_SCHEMA")
    if len(mapping) < 2:
        raise ContractError("INVALID_CLASS_SCHEMA")
    if not isinstance(config["target_column"], str) or not config["target_column"] or config["target_column"] in columns:
        raise ContractError("INVALID_TARGET_SCHEMA")
    if (type(config["seed"]) is not int or config["seed"] != SEED or config["model"] != "RandomForestClassifier"
            or canonical_json(config["model_parameters"]) != canonical_json(RF_PARAMETERS)
            or canonical_json(config["preprocessing"]) != canonical_json(PREPROCESSING)):
        raise ContractError("BASELINE_RECIPE_CHANGED")


def recipe_manifest(config: Mapping[str, object], code_files: Mapping[str, str | Path] | None = None) -> dict[str, object]:
    """Bind source, complete config, schema, seed, environment and preprocessing."""
    _validate_config(config)
    sources = dict(code_files or {})
    sources["canonical_scoring.py"] = Path(__file__)
    body = {
        "schema": "study-artifact-recipe/v1",
        "code_files": {name: file_sha256(path) for name, path in sorted(sources.items())},
        "config_sha256": content_sha256(config),
        "class_mapping_sha256": content_sha256(config["class_mapping"]),
        "seed_sha256": content_sha256(config["seed"]),
        "preprocessing_sha256": content_sha256(config["preprocessing"]),
        "environment": environment_manifest(),
    }
    body["code_sha256"] = content_sha256(body["code_files"])
    body["environment_sha256"] = content_sha256(body["environment"])
    return {**body, "recipe_sha256": content_sha256(body)}


def _features(frame: pd.DataFrame, config: Mapping[str, object]) -> pd.DataFrame:
    if not isinstance(frame, pd.DataFrame) or list(frame.columns) != config["feature_columns"]:
        raise ContractError("FEATURE_SCHEMA_MISMATCH")
    result = frame.copy()
    for name in config["numeric_columns"]:
        try:
            values = pd.to_numeric(result[name], errors="raise").to_numpy(dtype=np.float64, na_value=np.nan)
        except (TypeError, ValueError):
            raise ContractError("INVALID_NUMERIC_FEATURE") from None
        if np.isinf(values).any():
            raise ContractError("NONFINITE_NUMERIC_FEATURE")
        result[name] = values
    for name in config["categorical_columns"]:
        values = result[name].astype("string")
        if values.eq(MISSING_SENTINEL).any():
            raise ContractError("RESERVED_SENTINEL_COLLISION")
        result[name] = values.fillna(MISSING_SENTINEL).astype(object)
    return result


def read_features_csv(path: str | Path, config: Mapping[str, object]) -> pd.DataFrame:
    """Blank is missing; strings such as NA and NULL remain real categories."""
    _validate_config(config)
    frame = pd.read_csv(path, dtype="string", keep_default_na=False)
    frame = frame.replace("", pd.NA)
    _features(frame, config)
    return frame


def read_training_csv(path: str | Path, config: Mapping[str, object]) -> tuple[pd.DataFrame, np.ndarray]:
    _validate_config(config)
    frame = pd.read_csv(path, dtype="string", keep_default_na=False)
    target = config["target_column"]
    if list(frame.columns) != config["feature_columns"] + [target]:
        raise ContractError("TRAINING_SCHEMA_MISMATCH")
    labels = _parse_class_strings(frame.pop(target).tolist())
    validate_predictions(labels, len(frame), tuple(range(len(config["class_mapping"]))))
    # Normalization belongs to fit/predict; return missing nominal values intact.
    return frame.replace("", pd.NA), labels


def validate_predictions(predictions: object, expected_rows: int, classes: Sequence[int]) -> np.ndarray:
    """Accept exactly one finite integer-ID vector, without coercing bad types."""
    allowed = _validate_classes(classes)
    if type(expected_rows) is not int or expected_rows <= 0:
        raise ContractError("INVALID_EXPECTED_LENGTH")
    if isinstance(predictions, (list, tuple)) and any(isinstance(value, (bool, np.bool_)) for value in predictions):
        raise ContractError("PREDICTION_TYPE")
    try:
        values = np.asarray(predictions)
    except (TypeError, ValueError):
        raise ContractError("PREDICTION_TYPE") from None
    if values.ndim != 1 or values.shape[0] != expected_rows:
        raise ContractError("PREDICTION_LENGTH_OR_SHAPE")
    if values.dtype.kind not in "iuf":
        raise ContractError("PREDICTION_TYPE")
    if not np.isfinite(values).all():
        raise ContractError("PREDICTION_NONFINITE")
    if not np.equal(values, np.floor(values)).all() or not np.isin(values, allowed).all():
        raise ContractError("PREDICTION_CLASS")
    return values.astype(np.int64, copy=True)


def _parse_class_strings(values: Sequence[str]) -> np.ndarray:
    if any(not value.isascii() or not value.isdecimal() for value in values):
        raise ContractError("INVALID_CLASS_FILE")
    try:
        return np.asarray([int(value) for value in values], dtype=np.int64)
    except (ValueError, OverflowError):
        raise ContractError("INVALID_CLASS_FILE") from None


def read_prediction_json(path: str | Path, expected_rows: int, classes: Sequence[int]) -> np.ndarray:
    try:
        values = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        raise ContractError("INVALID_PREDICTION_FILE") from None
    if not isinstance(values, list) or any(type(value) not in (int, float) for value in values):
        raise ContractError("PREDICTION_TYPE")
    return validate_predictions(values, expected_rows, classes)


def _learned_state(value: object) -> object:
    """Hash contents rather than pickle memoization or NumPy memory layout."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else {"float": str(value)}
    if isinstance(value, np.generic):
        return _learned_state(value.item())
    if isinstance(value, np.dtype):
        return {"numpy_dtype": str(value)}
    if isinstance(value, np.ndarray):
        data = ({name: _learned_state(value[name]) for name in value.dtype.names}
                if value.dtype.names else _learned_state(value.tolist()))
        return {"ndarray_dtype": str(value.dtype), "shape": list(value.shape), "data": data}
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ContractError("UNSUPPORTED_FITTED_STATE_TYPE")
        return {key: _learned_state(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_learned_state(item) for item in value]
    if isinstance(value, UserList):
        return _learned_state(value.data)
    if isinstance(value, slice):
        return {"slice": [value.start, value.stop, value.step]}
    if isinstance(value, type):
        return {"type": f"{value.__module__}.{value.__qualname__}"}
    value_type = type(value)
    if isinstance(value, BaseEstimator) or (value_type.__module__ == "sklearn.tree._tree" and value_type.__name__ == "Tree"):
        return {
            "estimator_type": f"{value_type.__module__}.{value_type.__qualname__}",
            "state": _learned_state(value.__getstate__()),
        }
    raise ContractError("UNSUPPORTED_FITTED_STATE_TYPE")


def fitted_state_sha256(pipeline: Pipeline) -> str:
    return content_sha256(_learned_state(pipeline))


@dataclass(frozen=True)
class FittedArtifact:
    pipeline: Pipeline
    config_json: str
    recipe_json: str
    fitted_state_sha256: str

    def validate_recipe(self) -> None:
        config = json.loads(self.config_json)
        _validate_config(config)
        recipe = json.loads(self.recipe_json)
        claimed_digest = recipe.pop("recipe_sha256", None)
        if claimed_digest != content_sha256(recipe):
            raise ContractError("ARTIFACT_RECIPE_CHANGED")
        if recipe["config_sha256"] != content_sha256(config):
            raise ContractError("ARTIFACT_CONFIG_CHANGED")
        if (recipe["class_mapping_sha256"] != content_sha256(config["class_mapping"])
                or recipe["seed_sha256"] != content_sha256(config["seed"])
                or recipe["preprocessing_sha256"] != content_sha256(config["preprocessing"])
                or recipe["code_sha256"] != content_sha256(recipe["code_files"])
                or recipe["environment_sha256"] != content_sha256(recipe["environment"])):
            raise ContractError("ARTIFACT_RECIPE_CHANGED")
        if recipe["code_files"].get("canonical_scoring.py") != file_sha256(Path(__file__)):
            raise ContractError("ARTIFACT_SOURCE_CHANGED")
        if recipe["environment"] != environment_manifest():
            raise ContractError("ARTIFACT_ENVIRONMENT_CHANGED")

    @property
    def manifest(self) -> dict[str, object]:
        self.validate_recipe()
        recipe = json.loads(self.recipe_json)
        body = {"recipe": recipe, "fitted_state_sha256": self.fitted_state_sha256}
        return {**body, "artifact_sha256": content_sha256(body)}

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        self.validate_recipe()
        config = json.loads(self.config_json)
        _validate_config(config)
        if fitted_state_sha256(self.pipeline) != self.fitted_state_sha256:
            raise ContractError("FITTED_ARTIFACT_CHANGED")
        values = self.pipeline.predict(_features(features, config))
        return validate_predictions(values, len(features), tuple(range(len(config["class_mapping"]))))


def fit(train_X: pd.DataFrame, train_y: object, frozen_config: Mapping[str, object]) -> FittedArtifact:
    """Fit the canonical baseline only; this does not admit or meter a run."""
    config = json.loads(canonical_json(frozen_config))
    _validate_config(config)
    features = _features(train_X, config)
    classes = tuple(range(len(config["class_mapping"])))
    labels = validate_predictions(train_y, len(features), classes)
    if tuple(np.unique(labels)) != classes:
        raise ContractError("TRAINING_CLASS_ABSENT")
    transformers = []
    if config["numeric_columns"]:
        transformers.append(("numeric", SimpleImputer(strategy="median", keep_empty_features=True), config["numeric_columns"]))
    if config["categorical_columns"]:
        categories = [sorted(set(features[name]) | {MISSING_SENTINEL}) for name in config["categorical_columns"]]
        encoder = OneHotEncoder(categories=categories, handle_unknown="ignore", sparse_output=True, dtype=np.float64)
        transformers.append(("categorical", encoder, config["categorical_columns"]))
    transform = ColumnTransformer(transformers, remainder="drop", sparse_threshold=0.3)
    model = RandomForestClassifier(**config["model_parameters"])
    if model.get_params(deep=False) != config["model_parameters"]:
        raise ContractError("UNPINNED_MODEL_PARAMETER")
    pipeline = Pipeline([("preprocessing", transform), ("classifier", model)])
    pipeline.fit(features, labels)
    return FittedArtifact(
        pipeline=pipeline,
        config_json=canonical_json(config),
        recipe_json=canonical_json(recipe_manifest(config)),
        fitted_state_sha256=fitted_state_sha256(pipeline),
    )


def score_private_labels(predictions: object, private_labels_path: str | Path, *, expected_rows: int,
                         classes: Sequence[int], target_column: str = "class") -> dict[str, object]:
    """Return only scalar BA/status. Keep this function in the trusted scorer.

    Prediction validation precedes any label read. Private-file/schema problems
    raise one generic trusted error; they never become an agent-invalid score.
    """
    allowed = _validate_classes(classes)
    predicted = validate_predictions(predictions, expected_rows, allowed)
    try:
        raw = Path(private_labels_path).read_text(encoding="utf-8")
        rows = list(csv.reader(io.StringIO(raw), strict=True))
        if not rows or rows[0] != [target_column] or any(len(row) != 1 for row in rows[1:]):
            raise ValueError
        labels = _parse_class_strings([row[0] for row in rows[1:]])
        labels = validate_predictions(labels, expected_rows, allowed)
        if tuple(np.unique(labels)) != allowed:
            raise ValueError
    except (OSError, UnicodeError, ValueError, csv.Error):
        raise PrivateScoringError("TRUSTED_SCORING_UNAVAILABLE") from None
    recalls = [float(np.count_nonzero((labels == class_id) & (predicted == class_id))) /
               float(np.count_nonzero(labels == class_id)) for class_id in allowed]
    score = math.fsum(recalls) / len(allowed)
    return {"status": "VALID", "balanced_accuracy": score}


def _digest(value: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise ContractError("INVALID_ARTIFACT_IDENTITY")


@dataclass(frozen=True)
class CandidateIdentity:
    artifact_sha256: str
    recipe_sha256: str

    def __post_init__(self) -> None:
        _digest(self.artifact_sha256)
        _digest(self.recipe_sha256)

    @classmethod
    def from_artifact(cls, artifact: FittedArtifact) -> CandidateIdentity:
        manifest = artifact.manifest
        return cls(manifest["artifact_sha256"], manifest["recipe"]["recipe_sha256"])


@dataclass(frozen=True)
class SelectionState:
    """A pure transition record; persistence and exclusive admission are external."""
    default: CandidateIdentity
    verified: tuple[CandidateIdentity, ...]
    locked: CandidateIdentity | None = None
    lock_source: str | None = None
    refit_attempts: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.verified, tuple) or self.default not in self.verified:
            raise ContractError("INVALID_SELECTION_STATE")
        if len({item.artifact_sha256 for item in self.verified}) != len(self.verified):
            raise ContractError("INVALID_SELECTION_STATE")
        if type(self.refit_attempts) is not int or self.refit_attempts not in (0, 1):
            raise ContractError("INVALID_SELECTION_STATE")
        if self.locked is None:
            if self.lock_source is not None or self.refit_attempts:
                raise ContractError("INVALID_SELECTION_STATE")
        elif self.locked not in self.verified or self.lock_source not in ("explicit_agent_lock", "deadline_default"):
            raise ContractError("INVALID_SELECTION_STATE")


def register_default(identity: CandidateIdentity) -> SelectionState:
    return SelectionState(default=identity, verified=(identity,))


def register_verified_candidate(state: SelectionState, identity: CandidateIdentity) -> SelectionState:
    if state.locked is not None or state.refit_attempts:
        raise ContractError("FINAL_SELECTION_CLOSED")
    if identity in state.verified:
        return state
    if any(candidate.artifact_sha256 == identity.artifact_sha256 for candidate in state.verified):
        raise ContractError("CONFLICTING_ARTIFACT_IDENTITY")
    return replace(state, verified=state.verified + (identity,))


def lock_artifact(state: SelectionState, identity: CandidateIdentity) -> SelectionState:
    if state.locked is not None:
        if state.locked == identity:
            return state
        raise ContractError("FINAL_SELECTION_CLOSED")
    if identity not in state.verified or state.refit_attempts:
        raise ContractError("UNVERIFIED_FINAL_ARTIFACT")
    return replace(state, locked=identity, lock_source="explicit_agent_lock")


def resolve_final_lock(state: SelectionState) -> SelectionState:
    """Deadline fallback stays the registered default, never archive-best."""
    if state.locked is not None:
        return state
    return replace(lock_artifact(state, state.default), lock_source="deadline_default")


def begin_final_refit(state: SelectionState, identity: CandidateIdentity, recipe_sha256: str) -> SelectionState:
    """Consume before launching; failure still spends the sole refit attempt."""
    _digest(recipe_sha256)
    if state.locked is None or identity != state.locked:
        raise ContractError("FINAL_LOCK_MISMATCH")
    if recipe_sha256 != identity.recipe_sha256:
        raise ContractError("FINAL_RECIPE_CHANGED")
    if state.refit_attempts != 0:
        raise ContractError("FINAL_REFIT_EXHAUSTED")
    return replace(state, refit_attempts=1)
