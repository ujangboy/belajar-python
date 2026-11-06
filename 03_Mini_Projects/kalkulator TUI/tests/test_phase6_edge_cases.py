from __future__ import annotations

import pytest

from hitung.engine import CalcError, evaluate
from hitung.engines.conversion_engine import ConversionError, convert_value
from hitung.engines.data_engine import bitwise, number_bases
from hitung.engines.electrical_engine import ohms_law
from hitung.engines.finance_engine import loan_payment
from hitung.engines.percentage_engine import what_percent
from hitung.engines.util import EngineError
from hitung.format import format_number


@pytest.mark.parametrize("expr", ["1/0", "sqrt(-1)", "ncr(5;6)", "logn(1;8)"])
def test_engine_rejects_invalid_inputs(expr):
    with pytest.raises(CalcError):
        evaluate(expr)


def test_format_plain_and_small_values():
    assert format_number(1234.5, number_format="plain", thousands=False, precision=2) in {"1234.5", "1234.50"}
    assert format_number(0.0000001, precision=2)  # should not crash (scientific fallback)


def test_conversion_and_ohm_errors():
    with pytest.raises(ConversionError):
        convert_value(1, "m", "kg", "length")
    with pytest.raises(EngineError):
        ohms_law(voltage=1)  # needs exactly 2
    with pytest.raises(EngineError):
        what_percent(1, 0)


def test_data_and_finance_edge_cases():
    assert number_bases("FF", 16)["dec"] == "255"
    assert bitwise(1, "SHL", 1)["dec"] == 2
    r = loan_payment(1000, 0, 10)
    assert float(r["payment"]) == pytest.approx(100.0)
