"""Pure static CSV validator and exact MAE fixture for the selected House Price task.

This is deliberately only a local parser/math fixture.  It has no file, network,
training, provider, ORX, artifact-lock, or native-runtime integration.  It does
not secure data from another action in the same user REPL, and it is not an
actual task scorer or hidden-label evaluator.

``score_prediction_csv`` accepts only caller-supplied prediction *bytes*, an
immutable public ID tuple, and a synthetic reference mapping for unit tests.  A
successful result contains an exact ``fractions.Fraction`` MAE in original
``SalePrice`` units.  There is no rounding: CSV decimal lexemes and finite
``int``/``float``/``Decimal`` reference values are converted to exact rational
values (a float first uses its documented ``str(float)`` decimal spelling).
Configured coefficient and exponent guards bound this exact arithmetic.  A
byte-level preflight bounds raw CSV field tokens and records before UTF-8 decode
and CSV parsing; it does not mutate ``csv.field_size_limit`` or other
process-global parser state.  Errors never contain CSV fields, IDs, labels, or
residuals.
"""

from __future__ import annotations

from collections.abc import Mapping
import csv
from dataclasses import dataclass
from decimal import Decimal, DecimalException
from fractions import Fraction
import io
import math
import re
import sys


_NUMERIC_LEXEME = re.compile(
    r"(?P<sign>[+-]?)(?P<coefficient>(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+))"
    r"(?:[eE](?P<exponent>[+-]?[0-9]+))?$"
)


class ArtifactInvalidError(ValueError):
    """The submitted prediction artifact is invalid; no score exists."""


class ScorerContractError(ValueError):
    """The evaluator/public-manifest/reference contract is invalid; no score exists."""


@dataclass(frozen=True)
class ScorerLimits:
    """Explicit resource and numeric limits for one static scoring call.

    ``max_artifact_bytes`` includes the whole UTF-8 CSV byte sequence.
    ``max_data_rows`` excludes the header.  ``max_field_bytes`` applies to each
    raw CSV field token including quote/escape bytes and headers; public IDs and
    reference keys use their UTF-8 encoded byte length.  Coefficient digits
    exclude sign, decimal point, and exponent.  ``max_decimal_exponent`` bounds the absolute literal
    exponent and the stored Decimal exponent before exact Fraction conversion.
    No P0 production limits are implied; callers must supply all five limits.
    """

    max_artifact_bytes: int
    max_data_rows: int
    max_field_bytes: int
    max_coefficient_digits: int
    max_decimal_exponent: int


@dataclass(frozen=True)
class ScoreResult:
    """A valid exact MAE and the validated number of prediction rows."""

    mae: Fraction
    row_count: int


def score_prediction_csv(
    prediction_csv: bytes,
    expected_ids: tuple[str, ...],
    reference_sale_prices: Mapping[str, int | float | Decimal],
    limits: ScorerLimits,
) -> ScoreResult:
    """Validate an exact ordered ``Id,SalePrice`` CSV and return original-unit MAE.

    Artifact failures raise ``ArtifactInvalidError``.  Invalid limits, public ID
    manifest, or synthetic reference contract raise ``ScorerContractError``.
    Neither case returns a score.  Negative finite predictions are valid.
    """
    _validate_limits(limits)
    public_ids = _validate_public_ids(expected_ids, limits)
    reference = _validate_reference(public_ids, reference_sale_prices, limits)
    data = _validate_artifact_bytes(prediction_csv, limits)
    return _score_validated_csv(data, public_ids, reference, limits)


def _validate_limits(limits: ScorerLimits) -> None:
    if not isinstance(limits, ScorerLimits):
        raise ScorerContractError("SCORER_ERROR: invalid scorer limits")
    values = (
        limits.max_artifact_bytes,
        limits.max_data_rows,
        limits.max_field_bytes,
        limits.max_coefficient_digits,
        limits.max_decimal_exponent,
    )
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise ScorerContractError("SCORER_ERROR: invalid scorer limits")
    if (
        limits.max_artifact_bytes <= 0
        or limits.max_data_rows <= 0
        or limits.max_field_bytes <= 0
        or limits.max_coefficient_digits <= 0
        or limits.max_decimal_exponent < 0
        or any(value > sys.maxsize for value in values)
    ):
        raise ScorerContractError("SCORER_ERROR: invalid scorer limits")


def _validate_public_ids(
    expected_ids: tuple[str, ...], limits: ScorerLimits
) -> tuple[str, ...]:
    error = ScorerContractError("SCORER_ERROR: invalid public ID manifest")
    if not isinstance(expected_ids, tuple) or not expected_ids:
        raise error
    if len(expected_ids) > limits.max_data_rows:
        raise error
    for value in expected_ids:
        if not isinstance(value, str) or value == "":
            raise error
        _validate_text_field_size(value, limits, error)
    if len(set(expected_ids)) != len(expected_ids):
        raise error
    return expected_ids


def _validate_reference(
    expected_ids: tuple[str, ...],
    reference_sale_prices: Mapping[str, int | float | Decimal],
    limits: ScorerLimits,
) -> dict[str, Fraction]:
    if not isinstance(reference_sale_prices, Mapping):
        raise ScorerContractError("SCORER_ERROR: invalid reference contract")
    try:
        if len(reference_sale_prices) != len(expected_ids):
            raise ScorerContractError("SCORER_ERROR: invalid reference contract")
        observed_keys: set[str] = set()
        for key in reference_sale_prices.keys():
            if not isinstance(key, str) or key == "":
                raise ScorerContractError("SCORER_ERROR: invalid reference contract")
            _validate_text_field_size(
                key,
                limits,
                ScorerContractError("SCORER_ERROR: invalid reference contract"),
            )
            observed_keys.add(key)
        if observed_keys != set(expected_ids):
            raise ScorerContractError("SCORER_ERROR: invalid reference contract")
        return {
            identifier: _reference_to_fraction(
                reference_sale_prices[identifier], limits
            )
            for identifier in expected_ids
        }
    except ScorerContractError:
        raise
    except (ArithmeticError, DecimalException, MemoryError, TypeError, ValueError):
        raise ScorerContractError("SCORER_ERROR: invalid reference contract") from None


def _reference_to_fraction(value: int | float | Decimal, limits: ScorerLimits) -> Fraction:
    if isinstance(value, bool):
        raise ScorerContractError("SCORER_ERROR: invalid reference contract")
    if isinstance(value, int):
        text = str(value)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ScorerContractError("SCORER_ERROR: invalid reference contract")
        text = str(value)
    elif isinstance(value, Decimal):
        if not value.is_finite():
            raise ScorerContractError("SCORER_ERROR: invalid reference contract")
        text = str(value)
    else:
        raise ScorerContractError("SCORER_ERROR: invalid reference contract")
    return _decimal_text_to_fraction(
        text, limits, ScorerContractError("SCORER_ERROR: invalid reference contract")
    )


def _validate_artifact_bytes(prediction_csv: bytes, limits: ScorerLimits) -> bytes:
    if not isinstance(prediction_csv, bytes) or len(prediction_csv) > limits.max_artifact_bytes:
        raise ArtifactInvalidError("INVALID: malformed prediction artifact")
    return prediction_csv


def _score_validated_csv(
    data: bytes,
    expected_ids: tuple[str, ...],
    reference: dict[str, Fraction],
    limits: ScorerLimits,
) -> ScoreResult:
    _preflight_csv_bytes(data, limits)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise ArtifactInvalidError("INVALID: malformed prediction artifact") from None

    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        try:
            header = next(reader)
        except StopIteration:
            raise ArtifactInvalidError("INVALID: malformed prediction artifact") from None
        _validate_row_shape_and_field_sizes(header, limits)
        if header != ["Id", "SalePrice"]:
            raise ArtifactInvalidError("INVALID: malformed prediction artifact")

        total_error = Fraction(0, 1)
        data_rows = 0
        for row in reader:
            data_rows += 1
            if data_rows > limits.max_data_rows:
                raise ArtifactInvalidError("INVALID: malformed prediction artifact")
            _validate_row_shape_and_field_sizes(row, limits)
            identifier, sale_price_text = row
            if data_rows > len(expected_ids) or identifier != expected_ids[data_rows - 1]:
                raise ArtifactInvalidError("INVALID: malformed prediction artifact")
            prediction = _decimal_text_to_fraction(
                sale_price_text,
                limits,
                ArtifactInvalidError("INVALID: malformed prediction artifact"),
            )
            try:
                total_error += abs(prediction - reference[identifier])
            except (ArithmeticError, MemoryError, OverflowError):
                raise ScorerContractError("SCORER_ERROR: numerical computation failed") from None
    except csv.Error:
        raise ArtifactInvalidError("INVALID: malformed prediction artifact") from None

    if data_rows != len(expected_ids):
        raise ArtifactInvalidError("INVALID: malformed prediction artifact")
    try:
        return ScoreResult(mae=total_error / data_rows, row_count=data_rows)
    except (ArithmeticError, MemoryError, OverflowError):
        raise ScorerContractError("SCORER_ERROR: numerical computation failed") from None


def _preflight_csv_bytes(data: bytes, limits: ScorerLimits) -> None:
    """Bound raw field tokens and records without process-global csv settings.

    A raw field token includes its surrounding/escaped quote bytes.  This is a
    conservative byte limit: decoded field UTF-8 bytes can never exceed it.
    Records are counted outside quoted fields, with the header included.
    ``csv.reader(..., strict=True)`` remains the syntax authority after this
    bounded preflight.
    """
    field_bytes = 0
    record_count = 0
    record_started = False
    in_quotes = False
    index = 0
    while index < len(data):
        byte = data[index]
        if in_quotes:
            record_started = True
            field_bytes = _next_raw_field_size(field_bytes, limits)
            if byte == ord('"'):
                if index + 1 < len(data) and data[index + 1] == ord('"'):
                    field_bytes = _next_raw_field_size(field_bytes, limits)
                    index += 2
                    continue
                in_quotes = False
            index += 1
            continue

        if byte == ord(','):
            record_started = True
            field_bytes = 0
            index += 1
            continue
        if byte == ord('\n') or byte == ord('\r'):
            record_count += 1
            if record_count > limits.max_data_rows + 1:
                raise ArtifactInvalidError("INVALID: malformed prediction artifact")
            field_bytes = 0
            record_started = False
            if byte == ord('\r') and index + 1 < len(data) and data[index + 1] == ord('\n'):
                index += 2
            else:
                index += 1
            continue

        record_started = True
        field_bytes = _next_raw_field_size(field_bytes, limits)
        if byte == ord('"') and field_bytes == 1:
            in_quotes = True
        index += 1

    if record_started:
        record_count += 1
        if record_count > limits.max_data_rows + 1:
            raise ArtifactInvalidError("INVALID: malformed prediction artifact")


def _next_raw_field_size(field_bytes: int, limits: ScorerLimits) -> int:
    if field_bytes >= limits.max_field_bytes:
        raise ArtifactInvalidError("INVALID: malformed prediction artifact")
    return field_bytes + 1



def _validate_text_field_size(
    value: str, limits: ScorerLimits, error: ScorerContractError
) -> None:
    try:
        field_bytes = len(value.encode("utf-8"))
    except UnicodeEncodeError:
        raise error from None
    if field_bytes > limits.max_field_bytes:
        raise error


def _validate_row_shape_and_field_sizes(row: list[str], limits: ScorerLimits) -> None:
    if len(row) != 2 or any(
        len(field.encode("utf-8")) > limits.max_field_bytes for field in row
    ):
        raise ArtifactInvalidError("INVALID: malformed prediction artifact")


def _decimal_text_to_fraction(
    text: str, limits: ScorerLimits, error: ArtifactInvalidError | ScorerContractError
) -> Fraction:
    match = _NUMERIC_LEXEME.fullmatch(text)
    if match is None:
        raise error
    coefficient_digits = match.group("coefficient").replace(".", "")
    if len(coefficient_digits) > limits.max_coefficient_digits:
        raise error
    exponent_text = match.group("exponent")
    if exponent_text is not None and not _bounded_exponent(exponent_text, limits):
        raise error
    try:
        value = Decimal(text)
        if not value.is_finite() or abs(value.as_tuple().exponent) > limits.max_decimal_exponent:
            raise error
        return Fraction(value)
    except (ArithmeticError, DecimalException, MemoryError, OverflowError, ValueError):
        raise error from None


def _bounded_exponent(text: str, limits: ScorerLimits) -> bool:
    magnitude = text.lstrip("+-").lstrip("0") or "0"
    maximum = str(limits.max_decimal_exponent)
    if len(magnitude) != len(maximum):
        return len(magnitude) < len(maximum)
    return magnitude <= maximum
