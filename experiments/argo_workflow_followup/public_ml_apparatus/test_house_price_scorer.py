"""Focused synthetic tests for the static House Price MAE scorer fixture."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from decimal import Decimal
from fractions import Fraction
import csv
import unittest

from house_price_scorer import (
    ArtifactInvalidError,
    ScorerContractError,
    ScorerLimits,
    score_prediction_csv,
)


class HousePriceScorerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.expected_ids = ("0007", "08", "X9")
        self.reference = {"0007": 100010, "08": 0, "X9": Decimal("20.5")}
        self.limits = ScorerLimits(
            max_artifact_bytes=256,
            max_data_rows=3,
            max_field_bytes=32,
            max_coefficient_digits=12,
            max_decimal_exponent=6,
        )
        self.good_csv = b"Id,SalePrice\n0007,100000\n08,-10\nX9,30.5\n"

    def test_hand_calculated_original_unit_mae_and_immutable_result(self) -> None:
        result = score_prediction_csv(
            self.good_csv, self.expected_ids, self.reference, self.limits
        )
        self.assertEqual(result.mae, Fraction(10, 1))
        self.assertEqual(result.row_count, 3)
        with self.assertRaises(FrozenInstanceError):
            result.row_count = 4  # type: ignore[misc]

    def test_nontrivial_fractional_mae_has_no_rounding(self) -> None:
        result = score_prediction_csv(
            b"Id,SalePrice\n001,1.5\n2,1.75\n03,3\n",
            ("001", "2", "03"),
            {"001": 1, "2": 2, "03": 3},
            self.limits,
        )
        self.assertEqual(result.mae, Fraction(1, 4))

    def test_empty_and_duplicate_header_artifacts_are_invalid(self) -> None:
        for artifact in (b"", b"Id,Id\n0007,100000\n08,-10\nX9,30.5\n"):
            with self.subTest():
                with self.assertRaises(ArtifactInvalidError):
                    score_prediction_csv(
                        artifact, self.expected_ids, self.reference, self.limits
                    )

    def test_public_manifest_capacity_and_encoding_fail_as_scorer_errors(self) -> None:
        too_many_ids = ("0007", "08", "X9", "extra")
        row_limited = ScorerLimits(256, 3, 32, 12, 6)
        byte_limited = ScorerLimits(256, 3, 5, 12, 6)
        with self.assertRaises(ScorerContractError) as raised:
            score_prediction_csv(
                self.good_csv,
                too_many_ids,
                {"0007": 1, "08": 2, "X9": 3, "extra": 4},
                row_limited,
            )
        self.assertNotIn("extra", str(raised.exception))
        for identifiers, reference in (
            (("ééé", "08", "X9"), {"ééé": 1, "08": 2, "X9": 3}),
            (("\ud800", "08", "X9"), {"\ud800": 1, "08": 2, "X9": 3}),
        ):
            with self.subTest():
                with self.assertRaises(ScorerContractError):
                    score_prediction_csv(self.good_csv, identifiers, reference, byte_limited)

    def test_bad_reference_keys_and_csv_field_limit_state_are_sanitized(self) -> None:
        prior_limit = csv.field_size_limit()
        score_prediction_csv(
            self.good_csv, self.expected_ids, self.reference, self.limits
        )
        bad_references = (
            {"0007": 1, "08": 2, "ééé": 3},
            {"0007": 1, "08": 2, "\ud800": 3},
        )
        for reference in bad_references:
            with self.subTest():
                with self.assertRaises(ScorerContractError) as raised:
                    score_prediction_csv(
                        self.good_csv,
                        self.expected_ids,
                        reference,
                        ScorerLimits(256, 3, 5, 12, 6),
                    )
                self.assertNotIn("ééé", str(raised.exception))
        self.assertEqual(csv.field_size_limit(), prior_limit)

    def test_preserves_leading_zero_ids_and_rejects_any_identity_or_order_change(self) -> None:
        invalid_artifacts = (
            b"Id,SalePrice\n08,-10\n0007,100000\nX9,30.5\n",
            b"Id,SalePrice\n0007,100000\nX9,30.5\n",
            b"Id,SalePrice\n0007,100000\n08,-10\n08,30.5\n",
            b"Id,SalePrice\n0007,100000\n08,-10\nX9,30.5\nextra,1\n",
            b"Id,SalePrice\n7,100000\n08,-10\nX9,30.5\n",
        )
        for artifact in invalid_artifacts:
            with self.subTest(artifact=artifact):
                with self.assertRaises(ArtifactInvalidError):
                    score_prediction_csv(
                        artifact, self.expected_ids, self.reference, self.limits
                    )

    def test_rejects_header_row_encoding_and_numeric_artifact_failures_without_leaks(self) -> None:
        invalid_artifacts = (
            b"SalePrice,Id\n100000,0007\n-10,08\n30.5,X9\n",
            b"Id,SalePrice,extra\n0007,100000\n08,-10\nX9,30.5\n",
            b"Id,SalePrice\n0007,100000,extra\n08,-10\nX9,30.5\n",
            b"Id,SalePrice\n0007,100000\n08,\nX9,30.5\n",
            b"Id,SalePrice\n0007,NaN\n08,-10\nX9,30.5\n",
            b"Id,SalePrice\n0007,Infinity\n08,-10\nX9,30.5\n",
            b"Id,SalePrice\n0007,untrusted-secret\n08,-10\nX9,30.5\n",
            b"Id,SalePrice\n0007,1e999\n08,-10\nX9,30.5\n",
            b"Id,SalePrice\n0007,100000\n08,-10\nX9,30.5\xff",
        )
        for artifact in invalid_artifacts:
            with self.subTest(artifact=artifact):
                with self.assertRaises(ArtifactInvalidError) as raised:
                    score_prediction_csv(
                        artifact, self.expected_ids, self.reference, self.limits
                    )
                self.assertNotIn("untrusted-secret", str(raised.exception))
                self.assertNotIn("100010", str(raised.exception))

    def test_invalid_reference_or_public_manifest_is_scorer_error(self) -> None:
        invalid_references = (
            {"0007": 100010, "08": 0},
            {"0007": 100010, "08": 0, "other": 20.5},
            {"0007": 100010, "08": float("nan"), "X9": 20.5},
            {"0007": 100010, "08": True, "X9": 20.5},
            [100010, 0, 20.5],
        )
        for reference in invalid_references:
            with self.subTest(reference=type(reference).__name__):
                with self.assertRaises(ScorerContractError) as raised:
                    score_prediction_csv(
                        self.good_csv, self.expected_ids, reference, self.limits
                    )
                self.assertNotIn("100010", str(raised.exception))

        for invalid_ids in ([], ("0007", "0007"), ("0007", 8, "X9"), ()):
            with self.subTest(ids=invalid_ids):
                with self.assertRaises(ScorerContractError):
                    score_prediction_csv(
                        self.good_csv, invalid_ids, self.reference, self.limits
                    )

    def test_configured_byte_row_field_and_numeric_guards_are_artifact_invalid(self) -> None:
        tiny_bytes = ScorerLimits(
            max_artifact_bytes=len(self.good_csv) - 1,
            max_data_rows=3,
            max_field_bytes=32,
            max_coefficient_digits=12,
            max_decimal_exponent=6,
        )
        tiny_field = ScorerLimits(256, 3, 9, 12, 6)
        tiny_digits = ScorerLimits(256, 3, 32, 3, 6)
        tiny_exponent = ScorerLimits(256, 3, 32, 12, 2)
        small_reference = {"0007": 1, "08": 0, "X9": 2}
        cases = (
            (self.good_csv, tiny_bytes, self.reference),
            (b"Id,SalePrice\nvery-long-id,1\n", tiny_field, self.reference),
            (b"Id,SalePrice\n0007,1000\n08,-10\nX9,30.5\n", tiny_digits, small_reference),
            (b"Id,SalePrice\n0007,1e3\n08,-10\nX9,30.5\n", tiny_exponent, self.reference),
            (b"Id,SalePrice\n0007,100000\n08,-10\nX9,30.5\nextra,1\n", self.limits, self.reference),
        )
        for artifact, limits, reference in cases:
            with self.subTest(limits=limits):
                with self.assertRaises(ArtifactInvalidError):
                    score_prediction_csv(artifact, self.expected_ids, reference, limits)

    def test_invalid_limits_are_scorer_error_and_negative_finite_prediction_is_allowed(self) -> None:
        with self.assertRaises(ScorerContractError):
            score_prediction_csv(
                self.good_csv,
                self.expected_ids,
                self.reference,
                ScorerLimits(0, 3, 32, 12, 6),
            )
        result = score_prediction_csv(
            b"Id,SalePrice\n0007,-1\n08,-2\nX9,-3\n",
            self.expected_ids,
            {"0007": -1, "08": -2, "X9": -3},
            self.limits,
        )
        self.assertEqual(result.mae, Fraction(0, 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
