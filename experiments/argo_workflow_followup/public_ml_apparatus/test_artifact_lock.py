"""Focused stdlib regression tests for the static artifact-lock fixture."""

from __future__ import annotations

import hashlib
import math
import os
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from artifact_lock import (
    ArtifactLock,
    LockRegistry,
    MockScoreReceipt,
    bind_mock_score,
    lock_artifact_bytes,
    lock_artifact_file,
    verify_lock,
)

PROTOCOL_SHA256 = hashlib.sha256(b"frozen public protocol v1").hexdigest()


class ArtifactLockTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bytes = b"synthetic selected artifact\x00v1"
        self.lock = lock_artifact_bytes(
            lock_id="selection-001",
            study_id="study-static-001",
            protocol_id="protocol-v1",
            protocol_sha256=PROTOCOL_SHA256,
            artifact_identity="synthetic-artifact-001",
            artifact_bytes=self.bytes,
        )

    def test_good_byte_lock_verifies_publishes_once_and_binds_matching_receipt(self) -> None:
        self.assertEqual(verify_lock(self.lock, artifact_bytes=self.bytes), self.lock)
        registry = LockRegistry()
        self.assertEqual(registry.publish(self.lock, artifact_bytes=self.bytes), self.lock)
        receipt = MockScoreReceipt(
            receipt_id="mock-receipt-001",
            lock_id=self.lock.lock_id,
            study_id=self.lock.study_id,
            protocol_id=self.lock.protocol_id,
            protocol_sha256=self.lock.protocol_sha256,
            artifact_identity=self.lock.artifact_identity,
            artifact_sha256=self.lock.artifact_sha256,
            artifact_size_bytes=self.lock.artifact_size_bytes,
            score=0.75,
        )
        bound = bind_mock_score(self.lock, receipt, artifact_bytes=self.bytes)
        self.assertEqual(bound.lock, self.lock)
        self.assertEqual(bound.receipt, receipt)

    def test_file_lock_rejects_mutation_missing_and_retargeted_root(self) -> None:
        with TemporaryDirectory() as directory, TemporaryDirectory() as other_directory:
            root = Path(directory)
            artifact = root / "chosen.bin"
            artifact.write_bytes(self.bytes)
            lock = lock_artifact_file(
                lock_id="selection-file-001",
                study_id="study-static-001",
                protocol_id="protocol-v1",
                protocol_sha256=PROTOCOL_SHA256,
                artifact_identity="synthetic-file-001",
                artifact_path=artifact,
                declared_root=root,
            )
            self.assertEqual(verify_lock(lock, declared_root=root), lock)
            with self.assertRaises(ValueError):
                verify_lock(lock, declared_root=Path(other_directory))
            artifact.write_bytes(b"changed bytes")
            with self.assertRaises(ValueError):
                verify_lock(lock, declared_root=root)
            artifact.unlink()
            with self.assertRaises(ValueError):
                verify_lock(lock, declared_root=root)

    def test_registry_rejects_every_repeated_lock_id_even_when_bytes_are_valid(self) -> None:
        registry = LockRegistry()
        registry.publish(self.lock, artifact_bytes=self.bytes)
        with self.assertRaisesRegex(ValueError, "already published"):
            registry.publish(self.lock, artifact_bytes=self.bytes)

        replacement_bytes = b"different valid selected artifact"
        replacement = lock_artifact_bytes(
            lock_id=self.lock.lock_id,
            study_id=self.lock.study_id,
            protocol_id=self.lock.protocol_id,
            protocol_sha256=self.lock.protocol_sha256,
            artifact_identity="synthetic-artifact-002",
            artifact_bytes=replacement_bytes,
        )
        with self.assertRaisesRegex(ValueError, "already published"):
            registry.publish(replacement, artifact_bytes=replacement_bytes)

    def test_missing_first_file_artifact_cannot_reset_its_published_lock_id(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            first_path = root / "first.bin"
            first_path.write_bytes(self.bytes)
            registry = LockRegistry()
            first = lock_artifact_file(
                lock_id="selection-file-published-001",
                study_id="study-static-001",
                protocol_id="protocol-v1",
                protocol_sha256=PROTOCOL_SHA256,
                artifact_identity="synthetic-file-first-001",
                artifact_path=first_path,
                declared_root=root,
            )
            registry.publish(first, declared_root=root)
            first_path.unlink()
            replacement_path = root / "replacement.bin"
            replacement_bytes = b"replacement bytes with correct lock metadata"
            replacement_path.write_bytes(replacement_bytes)
            replacement = lock_artifact_file(
                lock_id=first.lock_id,
                study_id=first.study_id,
                protocol_id=first.protocol_id,
                protocol_sha256=first.protocol_sha256,
                artifact_identity="synthetic-file-replacement-001",
                artifact_path=replacement_path,
                declared_root=root,
            )
            with self.assertRaisesRegex(ValueError, "already published"):
                registry.publish(replacement, declared_root=root)

    def test_score_receipt_requires_exact_lock_protocol_and_artifact_binding(self) -> None:
        receipt = MockScoreReceipt(
            receipt_id="mock-receipt-002",
            lock_id=self.lock.lock_id,
            study_id=self.lock.study_id,
            protocol_id=self.lock.protocol_id,
            protocol_sha256=self.lock.protocol_sha256,
            artifact_identity=self.lock.artifact_identity,
            artifact_sha256=self.lock.artifact_sha256,
            artifact_size_bytes=self.lock.artifact_size_bytes,
            score=1.0,
        )
        for altered in (
            replace(receipt, lock_id="selection-other"),
            replace(receipt, study_id="study-other"),
            replace(receipt, protocol_id="protocol-other"),
            replace(receipt, protocol_sha256=hashlib.sha256(b"other protocol").hexdigest()),
            replace(receipt, artifact_identity="artifact-other"),
            replace(receipt, artifact_sha256=hashlib.sha256(b"other").hexdigest()),
            replace(receipt, artifact_size_bytes=receipt.artifact_size_bytes + 1),
        ):
            with self.assertRaises(ValueError):
                bind_mock_score(self.lock, altered, artifact_bytes=self.bytes)

    def test_rejects_malformed_metadata_self_report_only_and_nonfinite_score(self) -> None:
        with self.assertRaises(ValueError):
            lock_artifact_bytes(
                lock_id="selection-bad",
                study_id="study-static-001",
                protocol_id="protocol-v1",
                protocol_sha256="not-a-sha256",
                artifact_identity="synthetic-artifact-001",
                artifact_bytes=self.bytes,
            )
        with self.assertRaises(ValueError):
            verify_lock(self.lock)
        for malformed in (
            replace(self.lock, artifact_size_bytes=-1),
            replace(self.lock, schema_version="wrong-schema"),
        ):
            with self.assertRaises(ValueError):
                verify_lock(malformed, artifact_bytes=self.bytes)
        for value in (math.nan, math.inf, -math.inf, True):
            receipt = MockScoreReceipt(
                receipt_id="mock-receipt-nonfinite",
                lock_id=self.lock.lock_id,
                study_id=self.lock.study_id,
                protocol_id=self.lock.protocol_id,
                protocol_sha256=self.lock.protocol_sha256,
                artifact_identity=self.lock.artifact_identity,
                artifact_sha256=self.lock.artifact_sha256,
                artifact_size_bytes=self.lock.artifact_size_bytes,
                score=value,
            )
            with self.assertRaises(ValueError):
                bind_mock_score(self.lock, receipt, artifact_bytes=self.bytes)

    def test_file_selection_rejects_outside_path_and_symlink(self) -> None:
        with TemporaryDirectory() as directory, TemporaryDirectory() as outside_directory:
            root = Path(directory)
            outside = Path(outside_directory) / "outside.bin"
            outside.write_bytes(self.bytes)
            with self.assertRaises(ValueError):
                lock_artifact_file(
                    lock_id="selection-outside-001",
                    study_id="study-static-001",
                    protocol_id="protocol-v1",
                    protocol_sha256=PROTOCOL_SHA256,
                    artifact_identity="synthetic-outside-001",
                    artifact_path=outside,
                    declared_root=root,
                )
            linked = root / "linked.bin"
            try:
                linked.symlink_to(outside)
            except (NotImplementedError, OSError) as error:
                self.skipTest(f"symlinks unavailable: {error}")
            with self.assertRaises(ValueError):
                lock_artifact_file(
                    lock_id="selection-symlink-001",
                    study_id="study-static-001",
                    protocol_id="protocol-v1",
                    protocol_sha256=PROTOCOL_SHA256,
                    artifact_identity="synthetic-symlink-001",
                    artifact_path=linked,
                    declared_root=root,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
