"""Synthetic-only data integrity and custody tests."""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from data_custody import CustodyError, SEED, development_roster, export_splits, outer_indices, parse_arff, sha256, validate_source_url


def fixture() -> tuple[bytes, bytes, dict]:
    header = "@relation synthetic\n@attribute number numeric\n@attribute category {NA,x}\n@attribute class {zeta,alpha}\n@data\n"
    # Header order deliberately differs from alphabetical order and class appearance.
    lines = [f"{index},{'NA' if index % 3 == 0 else 'x'},{'alpha' if index % 2 == 0 else 'zeta'}" for index in range(100)]
    data = (header + "\n".join(lines) + "\n").encode()
    split_header = "@relation splits\n@attribute type {TRAIN,TEST}\n@attribute rowid numeric\n@attribute repeat numeric\n@attribute fold numeric\n@data\n"
    split_lines = [f"{'TRAIN' if index < 80 else 'TEST'},{index},0,0" for index in range(99, -1, -1)]
    splits = (split_header + "\n".join(split_lines) + "\n").encode()
    row = {
        "task_id": 37, "data_id": 37, "data_version": 1, "name": "synthetic", "target_feature": "class",
        "quality": {"NumberOfInstances": 100, "NumberOfFeatures": 3, "NumberOfClasses": 2, "NumberOfMissingValues": 0},
    }
    return data, splits, row


class DataCustodyTests(unittest.TestCase):
    def test_exact_split_order_class_schema_and_categorical_na_roundtrip(self):
        data, splits, row = fixture()
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            metadata = export_splits(data, splits, row, destination)
            identities = json.loads((destination / "row_identity.json").read_text())
            self.assertEqual(identities["outer_train"], list(range(79, -1, -1)))
            self.assertEqual(identities["test"], list(range(99, 79, -1)))
            expected_train, expected_dev = train_test_split(
                np.arange(79, -1, -1), test_size=0.2, random_state=SEED,
                stratify=np.array([0 if index % 2 else 1 for index in range(79, -1, -1)]),
            )
            self.assertEqual(identities["inner_train"], expected_train.tolist())
            self.assertEqual(identities["dev"], expected_dev.tolist())
            self.assertEqual(metadata["class_mapping"], ["zeta", "alpha"])
            self.assertEqual(metadata["row_counts"], {"source": 100, "inner_train": 64, "dev": 16, "outer_train": 80, "test": 20})
            train = pd.read_csv(destination / "inner_train.csv", keep_default_na=False)
            self.assertIn("NA", set(train["category"]))
            self.assertTrue((train["class"] == (train["number"] % 2 == 0).astype(int)).all())
            for name in ["dev_X.csv", "test_X.csv"]:
                self.assertEqual(list(pd.read_csv(destination / name).columns), ["number", "category"])
            for name in ["dev_y.csv", "test_y.csv"]:
                self.assertEqual(list(pd.read_csv(destination / name).columns), ["class"])
            self.assertEqual(destination.stat().st_mode & 0o777, 0o700)
            for path in destination.iterdir():
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                self.assertEqual(metadata["files_sha256"][path.name], sha256(path.read_bytes()))

    def test_split_overlap_duplicate_and_out_of_range_are_rejected(self):
        _, splits, _ = fixture()
        frame, _ = parse_arff(splits)
        for invalid in [99.0, 100.0, -1.0, 0.5, float("nan")]:
            corrupted = frame.copy()
            corrupted.loc[99, "rowid"] = invalid
            with self.assertRaises(CustodyError):
                outer_indices(corrupted, 100)

    def test_missing_class_in_outer_test_is_rejected_before_export(self):
        data, splits, row = fixture()
        # The outer test contains only even row IDs and hence only one class.
        lines = splits.decode().split("@data\n")[0] + "@data\n"
        lines += "\n".join(f"{'TEST' if index >= 80 and index % 2 == 0 else 'TRAIN'},{index},0,0" for index in range(100))
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(CustodyError, "CLASS_ABSENT_FROM_SPLIT"):
                export_splits(data, lines.encode(), row, Path(directory))
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_target_outside_public_header_is_rejected(self):
        data, splits, row = fixture()
        corrupted = data.replace(b"0,NA,alpha", b"0,NA,unknown", 1)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(CustodyError, "ARFF_PARSE_FAILURE"):
                export_splits(corrupted, splits, row, Path(directory))

    def test_unexpected_source_dimensions_and_missing_count_are_rejected(self):
        data, splits, row = fixture()
        for field, value in [("NumberOfInstances", 99), ("NumberOfFeatures", 4), ("NumberOfMissingValues", 1)]:
            changed = {**row, "quality": {**row["quality"], field: value}}
            with tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(CustodyError):
                    export_splits(data, splits, changed, Path(directory))

    def test_source_zeros_are_preserved_and_missing_values_are_not_dropped(self):
        data, splits, row = fixture()
        data = data.replace(b"0,NA,alpha", b"?,NA,alpha", 1)
        row["quality"]["NumberOfMissingValues"] = 1
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            metadata = export_splits(data, splits, row, destination)
            train = pd.read_csv(destination / "outer_train.csv", keep_default_na=False)
            self.assertEqual(len(train), 80)
            self.assertEqual(int((train["number"] == "").sum()), 1)
            self.assertEqual(metadata["row_counts"]["source"], 100)

    def test_non_development_roster_change_fails_closed(self):
        rows = [
            {"task_id": task, "data_id": data, "data_version": version, "allocation": "development"}
            for task, data, version in [(37, 37, 1), (146820, 40983, 2), (31, 31, 1), (146821, 40975, 3)]
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "roster.json"
            path.write_text(json.dumps({"rows": rows + [{"allocation": "selection"}]}))
            self.assertEqual(len(development_roster(path)), 4)
            rows[0]["data_version"] = 2
            path.write_text(json.dumps({"rows": rows}))
            with self.assertRaisesRegex(CustodyError, "DEVELOPMENT_VERSION_MISMATCH"):
                development_roster(path)

    def test_nonprimary_urls_credentials_and_insecure_transport_are_rejected(self):
        validate_source_url("https://openml.org/data/v1/download/37/diabetes.arff")
        for url in ["http://openml.org/data", "https://example.org/data", "https://token@openml.org/data", "file:///tmp/data", "https://openml.org:8443/data"]:
            with self.assertRaises(CustodyError):
                validate_source_url(url)

    def test_exports_are_deterministic_and_existing_files_not_overwritten(self):
        data, splits, row = fixture()
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "first", Path(directory) / "second"
            first_metadata = export_splits(data, splits, row, first)
            second_metadata = export_splits(data, splits, row, second)
            self.assertEqual(first_metadata, second_metadata)
            with self.assertRaises(FileExistsError):
                export_splits(data, splits, row, first)


if __name__ == "__main__":
    unittest.main()
