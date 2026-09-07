"""Synthetic split/custody regressions; no task data or model fitting."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from sklearn.model_selection import train_test_split

from data_prepare import PreparationError, prepare_bytes, write_prepared, read_source


def raw_table(rows: int = 20) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["Id", "Feature", "SalePrice"])
    writer.writerows([[f"{i:03}", f"feature-{i}", str(10000000+i)] for i in range(rows)])
    return out.getvalue().encode()


def records(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode(), newline="")))


class TrustedPreparationTest(unittest.TestCase):
    def prepare(self, data: bytes | None = None):
        data = raw_table() if data is None else data
        return prepare_bytes(data, hashlib.sha256(data).hexdigest(), 20, 3)

    def test_source_ordered_split_matches_sklearn_exactly_and_is_exhaustive(self):
        prepared = self.prepare()
        train, dev = train_test_split(list(range(16)), test_size=0.25, random_state=1, shuffle=True, stratify=None)
        ids = lambda name: [row["Id"] for row in records(prepared.files[name])]
        self.assertEqual(ids("train_inner.csv"), [f"{i:03}" for i in train])
        self.assertEqual(ids("dev_features.csv"), [f"{i:03}" for i in dev])
        self.assertEqual(ids("dev_targets.csv"), ids("dev_features.csv"))
        self.assertEqual(ids("train_outer.csv"), [f"{i:03}" for i in range(16)])
        self.assertEqual(ids("hidden_features.csv"), [f"{i:03}" for i in range(16,20)])
        self.assertEqual(ids("hidden_targets.csv"), ids("hidden_features.csv"))
        self.assertFalse(set(ids("train_inner.csv")) & set(ids("dev_features.csv")))
        self.assertEqual(set(ids("train_inner.csv")) | set(ids("dev_features.csv")) | set(ids("hidden_features.csv")), {f"{i:03}" for i in range(20)})

    def test_numeric_leading_feature_names_are_source_compatible(self):
        data = raw_table().replace(b"Id,Feature,SalePrice", b"Id,1stFlrSF,SalePrice")
        prepared = self.prepare(data)
        self.assertEqual(prepared.public_manifest["columns"], ["Id", "1stFlrSF", "SalePrice"])

    def test_targets_are_separate_and_public_metadata_has_no_payload(self):
        prepared = self.prepare()
        for name in ["dev_features.csv", "hidden_features.csv"]:
            self.assertNotIn("SalePrice", records(prepared.files[name])[0])
        for name in ["dev_targets.csv", "hidden_targets.csv"]:
            self.assertEqual(set(records(prepared.files[name])[0]), {"Id", "SalePrice"})
        text = json.dumps(prepared.public_manifest)
        for i in range(20):
            self.assertNotIn(str(10000000+i), text)
            self.assertNotIn(f"feature-{i}", text)
        self.assertNotIn('"ids"', text)
        self.assertEqual(prepared.public_manifest["counts"], {"all":20,"outer_train":16,"inner_train":12,"dev":4,"hidden":4})
        for name, data in prepared.files.items():
            self.assertEqual(prepared.public_manifest["files"][name]["sha256"], hashlib.sha256(data).hexdigest())

    def test_input_identity_schema_and_targets_fail_closed(self):
        good = raw_table()
        with self.assertRaisesRegex(PreparationError, "^INPUT_IDENTITY$"):
            prepare_bytes(good,"0"*64,20,3)
        variants = [good.replace(b"Id,Feature,SalePrice",b"Id,Id,SalePrice"),
                    good.replace(b"Id,Feature,SalePrice",b"Id,Feature,Target"),
                    good.replace(b"001,feature-1",b"000,feature-1"),
                    good.replace(b"000,feature-0",b",feature-0"),
                    good.replace(b"10000000",b"NaN"),
                    good.replace(b"10000000",b"-1"),
                    good.replace(b"10000000",b"1e999999"),
                    good.replace(b"000,feature-0,10000000",b"000,feature-0"),
                    good+b"020,f,10\n", b"\xff"]
        for data in variants:
            with self.subTest(size=len(data)):
                with self.assertRaises(PreparationError) as ctx:
                    self.prepare(data)
                self.assertNotIn("10000000", str(ctx.exception))
        for rows, cols in [(True,3),(0,3),(20,True),(20,1)]:
            with self.assertRaises(PreparationError):
                prepare_bytes(good,hashlib.sha256(good).hexdigest(),rows,cols)

    def test_read_source_rejects_symlink_hardlink_fifo_directory_and_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/"source.csv"
            source.write_bytes(raw_table())
            self.assertEqual(read_source(source), raw_table())
            link = root/"link.csv"
            link.symlink_to(source)
            with self.assertRaises(PreparationError):
                read_source(link)
            hard = root/"hard.csv"
            os.link(source, hard)
            with self.assertRaises(PreparationError):
                read_source(source)
            fifo = root/"fifo.csv"
            os.mkfifo(fifo)
            with self.assertRaises(PreparationError):
                read_source(fifo)
            with self.assertRaises(PreparationError):
                read_source(root)
            empty = root/"empty.csv"
            empty.write_bytes(b"")
            with self.assertRaises(PreparationError):
                read_source(empty)

    def test_private_ordered_id_manifests_match_feature_order(self):
        prepared = self.prepare()
        for group in ["dev", "hidden"]:
            ids = json.loads(prepared.files[group+"_ids.json"])
            self.assertEqual(ids, [row["Id"] for row in records(prepared.files[group+"_features.csv"])])
            self.assertEqual(hashlib.sha256(prepared.files[group+"_ids.json"]).hexdigest(), prepared.public_manifest["ordered_id_sha256"][group])

    def test_no_overwrite_symlink_or_extra_public_payload(self):
        prepared = self.prepare()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/"prepared"
            write_prepared(prepared, root)
            self.assertEqual(root.stat().st_mode & 0o777, 0o700)
            self.assertEqual(set(p.name for p in root.iterdir()),set(prepared.files)|{"public_manifest.json"})
            for name,data in prepared.files.items():
                self.assertEqual((root/name).read_bytes(),data)
                self.assertEqual((root/name).stat().st_mode & 0o777,0o600)
            with self.assertRaisesRegex(PreparationError,"^OUTPUT_EXISTS$"):
                write_prepared(prepared,root)
            link=Path(tmp)/"link";link.symlink_to(root,target_is_directory=True)
            with self.assertRaises(PreparationError):
                write_prepared(prepared,link)
            self.assertEqual((root/"train_outer.csv").read_bytes(),prepared.files["train_outer.csv"])


if __name__ == "__main__":
    unittest.main()
