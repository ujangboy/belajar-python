"""Mesin persentase (murni)."""

from __future__ import annotations

import math

from .util import EngineError, to_float


def percent_of(percent: float, base: float) -> float:
    p, b = to_float(percent, "persen"), to_float(base, "nilai")
    return b * p / 100.0


def what_percent(part: float, whole: float) -> float:
    a, b = to_float(part, "bagian"), to_float(whole, "total")
    if b == 0:
        raise EngineError("Total tidak boleh nol.")
    return a / b * 100.0


def percent_change(old: float, new: float) -> float:
    o, n = to_float(old, "nilai awal"), to_float(new, "nilai baru")
    if o == 0:
        raise EngineError("Nilai awal tidak boleh nol.")
    return (n - o) / abs(o) * 100.0


def discount_price(price: float, percent: float) -> tuple[float, float]:
    price_v, pct = to_float(price, "harga"), to_float(percent, "diskon")
    if price_v < 0 or pct < 0:
        raise EngineError("Harga dan diskon tidak boleh negatif.")
    amount = price_v * pct / 100.0
    return amount, price_v - amount


def tax_amount(price: float, percent: float) -> tuple[float, float]:
    price_v, pct = to_float(price, "harga"), to_float(percent, "pajak")
    if price_v < 0 or pct < 0:
        raise EngineError("Harga dan pajak tidak boleh negatif.")
    amount = price_v * pct / 100.0
    return amount, price_v + amount


def tip_amount(bill: float, percent: float, people: int = 1) -> tuple[float, float, float]:
    bill_v, pct = to_float(bill, "tagihan"), to_float(percent, "tip")
    if bill_v < 0 or pct < 0:
        raise EngineError("Tagihan dan tip tidak boleh negatif.")
    if people < 1:
        raise EngineError("Jumlah orang minimal 1.")
    amount = bill_v * pct / 100.0
    total = bill_v + amount
    return amount, total, total / people
