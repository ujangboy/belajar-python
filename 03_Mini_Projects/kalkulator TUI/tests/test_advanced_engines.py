from decimal import Decimal
import pytest

from hitung.engines.percentage_engine import discount_price, percent_change, percent_of, tax_amount, tip_amount, what_percent
from hitung.engines.math_engine import combinations, gcd, is_prime, lcm, permutations, prime_factors, stats
from hitung.engines.data_engine import bitwise, number_bases
from hitung.engines.electrical_engine import ohms_law
from hitung.engines.finance_engine import compound_interest, loan_payment, savings_future, simple_interest
from hitung.engines.date_engine import add_days, age, date_diff, from_unix, to_unix


def test_percentage():
    assert percent_of(10, 200) == 20
    assert what_percent(50, 200) == 25
    assert percent_change(100, 120) == 20
    assert discount_price(100, 10) == (10, 90)
    assert tax_amount(100, 11) == (11, 111)
    tip, total, per = tip_amount(100, 10, 2)
    assert (tip, total, per) == (10, 110, 55)


def test_math():
    assert gcd(12, 18) == 6
    assert lcm(4, 6) == 12
    assert is_prime(97) is True
    assert is_prime(1) is False
    assert prime_factors(84) == [2, 2, 3, 7]
    s = stats([1, 2, 2, 3])
    assert s["mean"] == 2
    assert s["median"] == 2
    assert combinations(5, 2) == 10
    assert permutations(5, 2) == 20


def test_data():
    b = number_bases("255", 10)
    assert b["hex"] == "0xFF" and b["bin"].startswith("0b")
    r = bitwise(6, "AND", 3)
    assert r["dec"] == 2
    assert bitwise(1, "SHL", 3)["dec"] == 8
    assert bitwise(0, "NOT")["dec"] == 0xFFFFFFFF


def test_electrical():
    r = ohms_law(voltage=12, resistance=6)
    assert r["current"] == 2 and r["power"] == 24
    assert "Rumus" not in r["formula"] and "V" in r["formula"]


def test_finance_decimal():
    s = simple_interest(1000, 10, 2)
    assert s["interest"] == Decimal("200.00")
    c = compound_interest(1000, 12, 1, 12)
    assert c["total"] > Decimal("1120.00")
    l = loan_payment(12000, 12, 12)
    assert l["payment"] > Decimal("1000.00")
    sv = savings_future(100, 0, 12)
    assert sv["future_value"] == Decimal("1200.00")


def test_date():
    d = date_diff("2026-01-01", "2026-01-11")
    assert d["days"] == 10
    assert str(add_days("2026-01-01", 1)) == "2026-01-02"
    a = age("2000-01-01", "2026-01-01")
    assert a["years"] == 26
    ts = to_unix("1970-01-01 00:00:00")
    assert ts == 0
    assert from_unix(0).year == 1970
