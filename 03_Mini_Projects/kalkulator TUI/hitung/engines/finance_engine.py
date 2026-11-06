"""Mesin keuangan (Decimal, murni)."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, getcontext

from .util import EngineError

getcontext().prec = 28
_CENT = Decimal("0.01")


def _d(value: object, label: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise EngineError(f"{label} harus berupa angka.") from None


def _money(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def simple_interest(principal: object, rate_percent: object, years: object) -> dict[str, object]:
    p, r, t = _d(principal, "pokok"), _d(rate_percent, "bunga"), _d(years, "waktu")
    if p < 0 or r < 0 or t < 0:
        raise EngineError("Nilai tidak boleh negatif.")
    interest = p * r / Decimal(100) * t
    total = p + interest
    return {
        "interest": _money(interest), "total": _money(total),
        "formula": "Bunga = P × r × t; Total = P + Bunga", "units": "nilai uang",
    }


def compound_interest(principal: object, rate_percent: object, years: object, compounds_per_year: object = 12) -> dict[str, object]:
    p, r, t = _d(principal, "pokok"), _d(rate_percent, "bunga"), _d(years, "waktu")
    n = _d(compounds_per_year, "periode/tahun")
    if p < 0 or r < 0 or t < 0 or n <= 0:
        raise EngineError("Input keuangan tidak valid.")
    rate = r / Decimal(100)
    periods = int((n * t).to_integral_value(rounding=ROUND_HALF_UP))
    amount = p * (Decimal(1) + rate / n) ** periods
    interest = amount - p
    return {
        "interest": _money(interest), "total": _money(amount),
        "formula": "A = P(1 + r/n)^(n×t)", "units": "nilai uang",
    }


def loan_payment(principal: object, annual_rate_percent: object, months: object) -> dict[str, object]:
    p = _d(principal, "pinjaman")
    annual = _d(annual_rate_percent, "bunga tahunan")
    m = int(_d(months, "bulan").to_integral_value(rounding=ROUND_HALF_UP))
    if p <= 0 or annual < 0 or m <= 0:
        raise EngineError("Input pinjaman tidak valid.")
    monthly = annual / Decimal(100) / Decimal(12)
    if monthly == 0:
        payment = p / Decimal(m)
    else:
        payment = p * (monthly * (Decimal(1) + monthly) ** m) / ((Decimal(1) + monthly) ** m - 1)
    total = payment * Decimal(m)
    interest = total - p
    return {
        "payment": _money(payment), "total": _money(total), "interest": _money(interest),
        "formula": "Cicilan = P×i(1+i)^n / ((1+i)^n - 1)", "units": "per bulan / total",
    }


def savings_future(monthly: object, annual_rate_percent: object, months: object) -> dict[str, object]:
    c = _d(monthly, "setoran/bulan")
    annual = _d(annual_rate_percent, "bunga tahunan")
    m = int(_d(months, "bulan").to_integral_value(rounding=ROUND_HALF_UP))
    if c < 0 or annual < 0 or m <= 0:
        raise EngineError("Input tabungan tidak valid.")
    i = annual / Decimal(100) / Decimal(12)
    if i == 0:
        fv = c * Decimal(m)
    else:
        fv = c * (((Decimal(1) + i) ** m - 1) / i)
    invested = c * Decimal(m)
    return {
        "future_value": _money(fv), "invested": _money(invested), "gain": _money(fv - invested),
        "formula": "FV = C × (((1+i)^n - 1)/i)", "units": "nilai uang",
    }
