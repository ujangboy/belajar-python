"""Utilitas error/validasi engine (murni)."""

from __future__ import annotations

import math


class EngineError(ValueError):
    pass


def to_float(value: object, label: str) -> float:
    try:
        n = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise EngineError(f"{label} harus berupa angka.") from None
    if not math.isfinite(n):
        raise EngineError(f"{label} tidak valid.")
    return n


def to_int(value: object, label: str) -> int:
    n = to_float(value, label)
    if abs(n - round(n)) > 1e-9:
        raise EngineError(f"{label} harus bilangan bulat.")
    return int(round(n))
