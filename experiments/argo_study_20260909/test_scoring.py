"""Synthetic checks only: python3 -m unittest test_scoring -v (from this directory)."""
from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

from scoring import (
    MISSING_SENTINEL,
    RF_PARAMETERS,
    CandidateIdentity,
    ContractError,
    PrivateScoringError,
    SelectionState,
    begin_final_refit,
    canonical_config,
    content_sha256,
    environment_manifest,
    fit,
    lock_artifact,
    read_features_csv,
    read_prediction_json,
    read_training_csv,
    recipe_manifest,
    register_default,
    register_verified_candidate,
    resolve_final_lock,
    score_private_labels,
    validate_predictions,
)


def metadata() -> dict[str, object]:
    return {
        "target_column": "class",
        "feature_columns": ["value", "empty", "category"],
        "numeric_columns": ["value", "empty"],
        "categorical_columns": ["category"],
        "class_mapping": ["negative", "positive"],
        "classes": [0, 1],
    }


def training() -> tuple[pd.DataFrame, np.ndarray]:
    return pd.DataFrame({
        "value": [1.0, 2.0, np.nan, 4.0, 5.0, 6.0],
        "empty": [np.nan] * 6,
        "category": ["a", "a", None, "b", "b", "NA"],
    }), np.array([0, 0, 0, 1, 1, 1])


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = canonical_config(metadata())
        self.features, self.labels = training()
        self.artifact = fit(self.features, self.labels, self.config)

    def test_rf_parameters_complete_and_fixed(self) -> None:
        self.assertEqual(self.artifact.pipeline["classifier"].get_params(), RF_PARAMETERS)
        self.assertEqual(self.config["model_parameters"]["n_estimators"], 100)
        self.assertEqual(self.config["model_parameters"]["random_state"], 20260909)
        self.assertEqual(self.config["model_parameters"]["n_jobs"], 2)

    def test_numeric_median_and_empty_column_fit_train_only(self) -> None:
        numeric = self.artifact.pipeline["preprocessing"].named_transformers_["numeric"]
        np.testing.assert_array_equal(numeric.statistics_, [4.0, 0.0])
        frame = pd.DataFrame({"value": [np.nan, 999999.0], "empty": [np.nan, 100.0]})
        np.testing.assert_array_equal(numeric.transform(frame), [[4.0, 0.0], [999999.0, 100.0]])
        np.testing.assert_array_equal(numeric.statistics_, [4.0, 0.0])

    def test_nominal_unknown_all_zero_and_missing_reserved(self) -> None:
        encoder = self.artifact.pipeline["preprocessing"].named_transformers_["categorical"]
        transformed = encoder.transform(pd.DataFrame({"category": ["never-seen", MISSING_SENTINEL]})).toarray()
        self.assertEqual(float(transformed[0].sum()), 0.0)
        self.assertEqual(float(transformed[1].sum()), 1.0)
        self.assertIn("NA", encoder.categories_[0])

    def test_sentinel_reserved_even_without_train_missing(self) -> None:
        frame = self.features.fillna({"category": "a"})
        artifact = fit(frame, self.labels, self.config)
        encoder = artifact.pipeline["preprocessing"].named_transformers_["categorical"]
        self.assertIn(MISSING_SENTINEL, encoder.categories_[0])

    def test_predictions_deterministic_and_frozen_config_copied(self) -> None:
        before = self.artifact.predict(self.features)
        duplicate = fit(self.features, self.labels, self.config)
        np.testing.assert_array_equal(before, duplicate.predict(self.features))
        self.assertEqual(self.artifact.manifest, duplicate.manifest)
        self.config["model_parameters"]["n_estimators"] = 1
        self.assertEqual(json.loads(self.artifact.config_json)["model_parameters"]["n_estimators"], 100)

    def test_joblib_round_trip_preserves_fitted_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic-artifact.joblib"
            joblib.dump(self.artifact, path)
            restored = joblib.load(path)
            self.assertEqual(restored.manifest, self.artifact.manifest)
            np.testing.assert_array_equal(restored.predict(self.features), self.artifact.predict(self.features))

    def test_modified_fitted_model_is_rejected(self) -> None:
        self.artifact.pipeline["classifier"].estimators_[0].tree_.value[0, 0, 0] = 0.314159
        with self.assertRaisesRegex(ContractError, "FITTED_ARTIFACT_CHANGED"):
            self.artifact.predict(self.features)

    def test_modified_config_or_manifest_cannot_reuse_identity(self) -> None:
        config = json.loads(self.artifact.config_json)
        config["class_mapping"] = ["positive", "negative"]
        changed = replace(self.artifact, config_json=json.dumps(config))
        with self.assertRaisesRegex(ContractError, "ARTIFACT_CONFIG_CHANGED"):
            changed.predict(self.features)
        recipe = json.loads(self.artifact.recipe_json)
        recipe["seed_sha256"] = "a" * 64
        changed = replace(self.artifact, recipe_json=json.dumps(recipe))
        with self.assertRaisesRegex(ContractError, "ARTIFACT_RECIPE_CHANGED"):
            _ = changed.manifest

    def test_reordered_features_and_reserved_collision_are_rejected(self) -> None:
        with self.assertRaisesRegex(ContractError, "FEATURE_SCHEMA_MISMATCH"):
            self.artifact.predict(self.features[["category", "value", "empty"]])
        frame = self.features.copy()
        frame.loc[0, "category"] = MISSING_SENTINEL
        with self.assertRaisesRegex(ContractError, "RESERVED_SENTINEL_COLLISION"):
            self.artifact.predict(frame)

    def test_nonfinite_numeric_and_absent_training_class_are_rejected(self) -> None:
        frame = self.features.copy()
        frame.loc[0, "value"] = np.inf
        with self.assertRaisesRegex(ContractError, "NONFINITE_NUMERIC_FEATURE"):
            self.artifact.predict(frame)
        with self.assertRaisesRegex(ContractError, "TRAINING_CLASS_ABSENT"):
            fit(self.features, np.zeros(len(self.features), dtype=int), self.config)

    def test_all_categorical_and_all_numeric_schemas(self) -> None:
        for numeric, categorical in [(["value", "empty"], []), ([], ["category"])]:
            with self.subTest(numeric=numeric, categorical=categorical):
                schema = metadata()
                schema.update(feature_columns=numeric + categorical, numeric_columns=numeric, categorical_columns=categorical)
                frame = self.features[numeric + categorical]
                artifact = fit(frame, self.labels, canonical_config(schema))
                self.assertEqual(artifact.predict(frame).shape, (len(frame),))

    def test_csv_preserves_literal_na_and_blank_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "train.csv"
            frame = self.features.copy()
            frame["class"] = self.labels
            frame.to_csv(path, index=False)
            features, labels = read_training_csv(path, self.config)
            self.assertEqual(features["category"].iloc[-1], "NA")
            self.assertTrue(pd.isna(features["category"].iloc[2]))
            artifact = fit(features, labels, self.config)
            path = Path(directory) / "features.csv"
            self.features.to_csv(path, index=False)
            loaded = read_features_csv(path, self.config)
            np.testing.assert_array_equal(artifact.predict(loaded), self.artifact.predict(self.features))


class ManifestTests(unittest.TestCase):
    def test_manifest_binds_all_recipe_components(self) -> None:
        config = canonical_config(metadata())
        manifest = recipe_manifest(config)
        self.assertEqual(manifest["config_sha256"], content_sha256(config))
        for key in ("code_sha256", "class_mapping_sha256", "seed_sha256", "preprocessing_sha256", "environment_sha256", "recipe_sha256"):
            self.assertEqual(len(manifest[key]), 64)
        self.assertEqual(manifest["environment"], environment_manifest())
        schema = metadata()
        schema["class_mapping"] = ["positive", "negative"]
        other = recipe_manifest(canonical_config(schema))
        self.assertNotEqual(other["class_mapping_sha256"], manifest["class_mapping_sha256"])
        self.assertNotEqual(other["recipe_sha256"], manifest["recipe_sha256"])
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "candidate.py"
            source.write_text("synthetic version 1\n", encoding="utf-8")
            first = recipe_manifest(config, {"candidate.py": source})
            source.write_text("synthetic version 2\n", encoding="utf-8")
            second = recipe_manifest(config, {"candidate.py": source})
            self.assertNotEqual(first["code_sha256"], second["code_sha256"])

    def test_bad_schema_and_modified_baseline_rejected(self) -> None:
        schema = metadata()
        schema["classes"] = [1, 2]
        with self.assertRaises(ContractError):
            canonical_config(schema)
        config = canonical_config(metadata())
        config["model_parameters"]["n_jobs"] = 3
        with self.assertRaisesRegex(ContractError, "BASELINE_RECIPE_CHANGED"):
            recipe_manifest(config)


class ScoringTests(unittest.TestCase):
    def test_prediction_negative_fixtures(self) -> None:
        invalid = [[], [0], [[0], [1]], [0, float("nan")], [0, float("inf")], [0, 0.5],
                   [0, 2], [0, -1], ["0", "1"], [True, 1], np.array([False, True]),
                   np.array([0, 1], dtype=object), [[0], 1], [0j, 1j]]
        for values in invalid:
            with self.subTest(values=repr(values)):
                with self.assertRaises(ContractError):
                    validate_predictions(values, 2, [0, 1])
        np.testing.assert_array_equal(validate_predictions([0, 1], 2, [0, 1]), [0, 1])

    def test_balanced_accuracy_matches_reference_and_only_scalar_exposed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic-private-labels.csv"
            labels = [0, 0, 0, 1]
            predicted = [0, 0, 1, 1]
            pd.DataFrame({"class": labels}).to_csv(path, index=False)
            result = score_private_labels(predicted, path, expected_rows=4, classes=[0, 1])
            self.assertEqual(result, {"status": "VALID", "balanced_accuracy": balanced_accuracy_score(labels, predicted)})
            self.assertEqual(set(result), {"status", "balanced_accuracy"})
            self.assertEqual(result, score_private_labels(predicted, path, expected_rows=4, classes=[0, 1]))
            self.assertAlmostEqual(result["balanced_accuracy"], 5.0 / 6.0)

    def test_multiclass_macro_recall_and_extremes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.csv"
            labels = [0, 0, 0, 1, 1, 2]
            pd.DataFrame({"class": labels}).to_csv(path, index=False)
            for predictions in (labels, [1, 1, 1, 2, 2, 0], [0, 1, 0, 1, 2, 2]):
                result = score_private_labels(predictions, path, expected_rows=6, classes=[0, 1, 2])
                self.assertEqual(result["balanced_accuracy"], balanced_accuracy_score(labels, predictions))

    def test_invalid_prediction_never_reads_private_labels(self) -> None:
        with patch.object(Path, "read_text", side_effect=AssertionError("private label read")):
            with self.assertRaises(ContractError):
                score_private_labels([0, 3], "does-not-exist", expected_rows=2, classes=[0, 1])

    def test_private_file_failures_have_one_generic_unknown_error(self) -> None:
        fixtures = ["wrong\n0\n1\n", "class\n0\n0\n", "class\n0\n", "class\n0\n2\n",
                    "class\n0\nNaN\n", "class\n0,1\n1\n", 'class\n0\n"1\n']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic-private.csv"
            for contents in fixtures:
                path.write_text(contents, encoding="utf-8")
                with self.assertRaisesRegex(PrivateScoringError, "^TRUSTED_SCORING_UNAVAILABLE$"):
                    score_private_labels([0, 1], path, expected_rows=2, classes=[0, 1])
            path.unlink()
            with self.assertRaises(PrivateScoringError):
                score_private_labels([0, 1], path, expected_rows=2, classes=[0, 1])

    def test_json_prediction_reader_rejects_extra_vectors_and_boolean(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "predictions.json"
            for value in ([[0, 1], [1, 0]], [False, 1], {"predictions": [0, 1]}, [0, float("nan")]):
                path.write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaises(ContractError):
                    read_prediction_json(path, 2, [0, 1])
            path.write_text("[0,1]", encoding="utf-8")
            np.testing.assert_array_equal(read_prediction_json(path, 2, [0, 1]), [0, 1])


class SelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.default = CandidateIdentity("a" * 64, "b" * 64)
        self.alternative = CandidateIdentity("c" * 64, "d" * 64)
        self.state = register_verified_candidate(register_default(self.default), self.alternative)

    def test_deadline_uses_default_not_last_or_highest_scored_candidate(self) -> None:
        final = resolve_final_lock(self.state)
        self.assertEqual(final.locked, self.default)
        self.assertEqual(final.lock_source, "deadline_default")
        self.assertIs(resolve_final_lock(final), final)

    def test_one_explicit_lock_is_idempotent_and_cannot_be_reselected(self) -> None:
        final = lock_artifact(self.state, self.alternative)
        self.assertIs(lock_artifact(final, self.alternative), final)
        with self.assertRaisesRegex(ContractError, "FINAL_SELECTION_CLOSED"):
            lock_artifact(final, self.default)
        with self.assertRaises(ContractError):
            register_verified_candidate(final, CandidateIdentity("e" * 64, "f" * 64))

    def test_unverified_candidate_cannot_lock(self) -> None:
        with self.assertRaisesRegex(ContractError, "UNVERIFIED_FINAL_ARTIFACT"):
            lock_artifact(self.state, CandidateIdentity("e" * 64, "f" * 64))

    def test_refit_consumed_before_launch_and_recipe_cannot_change(self) -> None:
        final = lock_artifact(self.state, self.alternative)
        with self.assertRaisesRegex(ContractError, "FINAL_LOCK_MISMATCH"):
            begin_final_refit(final, self.default, self.default.recipe_sha256)
        with self.assertRaisesRegex(ContractError, "FINAL_RECIPE_CHANGED"):
            begin_final_refit(final, self.alternative, "e" * 64)
        consumed = begin_final_refit(final, self.alternative, self.alternative.recipe_sha256)
        self.assertEqual(consumed.refit_attempts, 1)
        with self.assertRaisesRegex(ContractError, "FINAL_REFIT_EXHAUSTED"):
            begin_final_refit(consumed, self.alternative, self.alternative.recipe_sha256)
        self.assertEqual(final.refit_attempts, 0)

    def test_invalid_state_and_conflicting_digest_are_rejected(self) -> None:
        with self.assertRaises(ContractError):
            register_verified_candidate(self.state, CandidateIdentity(self.default.artifact_sha256, "e" * 64))
        with self.assertRaises(ContractError):
            replace(self.state, refit_attempts=1)
        with self.assertRaises(ContractError):
            SelectionState(self.default, ())
        with self.assertRaises(ContractError):
            CandidateIdentity("bad", "b" * 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
