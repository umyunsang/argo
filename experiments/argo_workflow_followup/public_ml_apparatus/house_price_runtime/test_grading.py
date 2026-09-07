"""Synthetic grading I/O and public-metric tests. No task labels or provider calls."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding, GradingError, grade_files, read_bound, format_dev_mae


class GradingTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hp-grade-test-")
        self.root = Path(self.temp.name).resolve()
        self.pred = self.make("pred.csv", b"Id,SalePrice\n001,10.25\n002,19.75\n")
        self.ids = self.make("ids.json", b'["001","002"]')
        self.targets = self.make("target.csv", b"Id,SalePrice\n001,10\n002,20\n")

    def tearDown(self):
        self.temp.cleanup()

    def make(self, name, data):
        path = self.root/name
        path.write_bytes(data)
        return FileBinding(path, hashlib.sha256(data).hexdigest(), len(data), path.stat().st_mtime_ns)

    def test_exact_quarter_mae_and_public_precision_no_raw_payload(self):
        result = grade_files(self.pred, self.ids, self.targets, max_rows=2)
        self.assertEqual(result.mae, Fraction(1,4))
        self.assertEqual(result.row_count, 2)
        self.assertEqual(result.predictions_sha256, self.pred.sha256)
        self.assertEqual(format_dev_mae(result.mae), "0.250000")
        self.assertEqual(format_dev_mae(Fraction(1,3)), "0.333333")
        self.assertEqual(format_dev_mae(Fraction(1,2000000)), "0.000000")
        self.assertEqual(format_dev_mae(Fraction(3,2000000)), "0.000002")
        self.assertNotIn("001", json.dumps(result.public_metric()))
        self.assertNotIn("10.25", json.dumps(result.public_metric()))

    def test_missing_changed_same_length_stale_time_and_wrong_hash_rejected(self):
        for field,value in [("sha256", "0"*64), ("bytes", self.pred.bytes+1), ("mtime_ns_max",0)]:
            options = self.pred.__dict__.copy(); options[field]=value
            with self.subTest(field=field), self.assertRaises(GradingError):
                read_bound(FileBinding(**options),1024)
        original = self.pred.path.read_bytes()
        self.pred.path.write_bytes(original.replace(b"10.25",b"11.25"))
        os.utime(self.pred.path, ns=(self.pred.mtime_ns_max,self.pred.mtime_ns_max))
        with self.assertRaises(GradingError):
            read_bound(self.pred,1024)
        self.pred.path.unlink()
        with self.assertRaises(GradingError):
            read_bound(self.pred,1024)

    def test_symlink_hardlink_fifo_and_directory_rejected_without_reads(self):
        link = self.root/"link";link.symlink_to(self.pred.path)
        for path in [link,self.root]:
            with self.assertRaises(GradingError):
                read_bound(FileBinding(path,self.pred.sha256,self.pred.bytes,self.pred.mtime_ns_max),1024)
        directory_link = self.root/"parent-link"
        directory_link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(GradingError):
            read_bound(FileBinding(directory_link/self.pred.path.name,self.pred.sha256,self.pred.bytes,self.pred.mtime_ns_max),1024)
        hard = self.root/"hard";os.link(self.pred.path,hard)
        with self.assertRaises(GradingError):
            read_bound(self.pred,1024)
        fifo = self.root/"fifo";os.mkfifo(fifo)
        with self.assertRaises(GradingError):
            read_bound(FileBinding(fifo,"0"*64,1,2**63-1),1024)

    def test_target_and_id_contract_order_uniqueness_caps_and_schema(self):
        bad_targets = [b"Id,Target\n001,10\n002,20\n", b"Id,SalePrice\n002,20\n001,10\n", b"Id,SalePrice\n001,10\n001,20\n", b"Id,SalePrice\n001,NaN\n002,20\n", b"Id,SalePrice\n001,1e999999\n002,20\n"]
        for data in bad_targets:
            target = self.make("bad-target.csv",data)
            with self.subTest(data=data):
                with self.assertRaises(GradingError) as ctx:
                    grade_files(self.pred,self.ids,target,max_rows=2)
                self.assertNotIn("001",str(ctx.exception))
                self.assertNotIn("NaN",str(ctx.exception))
        for data in [b'["001","001"]', b'[1,2]', b'[]', b'{}', b'["002","001"]', b'\xff']:
            ids = self.make("bad-ids.json",data)
            with self.subTest(data=data), self.assertRaises(GradingError):
                grade_files(self.pred,ids,self.targets,max_rows=2)
        with self.assertRaises(GradingError):
            grade_files(self.pred,self.ids,self.targets,max_rows=1)
        with self.assertRaises(GradingError):
            read_bound(self.pred,self.pred.bytes-1)
        with self.assertRaises(GradingError):
            grade_files(self.pred,self.ids,self.targets,max_rows=True)

    def test_invalid_prediction_has_no_score_and_valid_negative_allowed(self):
        for data in [b"Id,SalePrice\n002,19\n001,11\n", b"Id,SalePrice\n001,NaN\n002,20\n",b"Id,SalePrice\n001,1e999999\n002,20\n",b"Id,SalePrice,extra\n001,10,x\n002,20,x\n"]:
            pred = self.make("bad-pred.csv",data)
            with self.assertRaisesRegex(GradingError,"^ARTIFACT_INVALID$"):
                grade_files(pred,self.ids,self.targets,max_rows=2)
        pred = self.make("negative.csv",b"Id,SalePrice\n001,-10\n002,20\n")
        self.assertEqual(grade_files(pred,self.ids,self.targets,max_rows=2).mae,Fraction(10))
        for value in [Fraction(-1),Fraction(10**12+1)]:
            with self.assertRaises(GradingError):format_dev_mae(value)


if __name__ == "__main__":
    unittest.main(verbosity=2)
