from __future__ import annotations

import pytest

from hitung.format import MAX_PRECISION, format_number


@pytest.mark.parametrize(
    ("value", "kwargs", "expected"),
    [
        (0.0, {}, "0"),
        (-0.0, {}, "0"),
        (15.0, {}, "15"),
        (1234567.5, {}, "1.234.567,5"),
        (-1234.5, {}, "-1.234,5"),
        (1234567.5, {"thousands": False}, "1234567,5"),
        (1 / 3, {"precision": 2}, "0,33"),
        (2.5, {"precision": 0}, "3"),
        (-2.5, {"precision": 0}, "-3"),
        (0.5, {"precision": 0}, "1"),
        (1500.0, {"precision": 0}, "1.500"),
        (1.5e15, {}, "1,5e+15"),
        (-1.5e15, {}, "-1,5e+15"),
        (1.0, {"precision": 4}, "1"),
        (1.2300, {"precision": 4}, "1,23"),
    ],
)
def test_format_number(value: float, kwargs: dict, expected: str) -> None:
    assert format_number(value, **kwargs) == expected


def test_precision_is_clamped() -> None:
    assert format_number(1.23456789, precision=99) == format_number(
        1.23456789,
        precision=MAX_PRECISION,
    )
    assert format_number(1.23456789, precision=-5) == format_number(
        1.23456789,
        precision=0,
    )


def test_small_values_use_scientific_notation() -> None:
    text = format_number(1e-9, precision=6)
    assert "e-09" in text


def test_non_finite_is_described() -> None:
    assert format_number(float("inf")) == "Tak terhingga"
    assert format_number(float("-inf")) == "Tak terhingga"
