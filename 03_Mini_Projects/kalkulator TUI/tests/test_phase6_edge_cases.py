from __future__ import annotations

import pytest

from hitung.engine import CalcError, evaluate
from hitung.engines.conversion_engine import ConversionError, convert_value
from hitung.engines.percentage_engine import discount_price, what_percent
from hitung.engines.util import EngineError
from hitung.format import format_number


@pytest.mark.parametrize("expr", ["1/0", "sqrt(-1)", "ncr(5;6)", "logn(1;8)"])
def test_engine_rejects_invalid_inputs(expr):
    with pytest.raises(CalcError):
        evaluate(expr)


def test_format_plain_and_small_values():
    assert format_number(1234.5, number_format="plain", thousands=False, precision=2) in {"1234.5", "1234.50"}
    assert format_number(0.0000001, precision=2)  # should not crash (scientific fallback)


def test_conversion_and_percentage_errors():
    with pytest.raises(ConversionError):
        convert_value(1, "m", "kg", "length")
    with pytest.raises(EngineError):
        what_percent(1, 0)
    with pytest.raises(EngineError):
        discount_price(-1, 10)
