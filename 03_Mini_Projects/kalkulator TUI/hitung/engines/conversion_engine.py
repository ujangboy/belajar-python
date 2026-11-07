"""Mesin konversi murni (tanpa UI)."""

from __future__ import annotations

import math

from ..data.units import CategoryDef, UnitDef, get_category


class ConversionError(ValueError):
    """Kesalahan konversi yang aman ditampilkan."""


def _find_unit(category: CategoryDef, unit_id: str) -> UnitDef:
    for unit in category.units:
        if unit.unit_id == unit_id:
            return unit
    raise ConversionError(f"Unit '{unit_id}' tidak dikenal untuk kategori '{category.title}'.")


def _temp_to_c(value: float, unit_id: str) -> float:
    if unit_id == "c":
        return value
    if unit_id == "f":
        return (value - 32.0) * 5.0 / 9.0
    if unit_id == "k":
        return value - 273.15
    if unit_id == "r":
        return value * 5.0 / 9.0 - 273.15
    raise ConversionError(f"Unit suhu '{unit_id}' tidak dikenal.")


def _c_to_temp(c: float, unit_id: str) -> float:
    if unit_id == "c":
        return c
    if unit_id == "f":
        return c * 9.0 / 5.0 + 32.0
    if unit_id == "k":
        return c + 273.15
    if unit_id == "r":
        return (c + 273.15) * 9.0 / 5.0
    raise ConversionError(f"Unit suhu '{unit_id}' tidak dikenal.")


_DIGITAL_SI = {"KB": 1, "MB": 2, "GB": 3, "TB": 4, "PB": 5}
_DIGITAL_IEC = {"KiB": 1, "MiB": 2, "GiB": 3, "TiB": 4}


def _digital_to_bits(value: float, unit_id: str, mode: str) -> float:
    if unit_id == "b":
        return value
    if unit_id == "B":
        return value * 8.0
    if unit_id in _DIGITAL_IEC:
        return value * (1024.0 ** _DIGITAL_IEC[unit_id]) * 8.0
    if unit_id in _DIGITAL_SI:
        base = 1024.0 if mode == "iec" else 1000.0
        return value * (base ** _DIGITAL_SI[unit_id]) * 8.0
    raise ConversionError(f"Unit data '{unit_id}' tidak dikenal.")


def _bits_to_digital(bits: float, unit_id: str, mode: str) -> float:
    if unit_id == "b":
        return bits
    if unit_id == "B":
        return bits / 8.0
    if unit_id in _DIGITAL_IEC:
        return bits / 8.0 / (1024.0 ** _DIGITAL_IEC[unit_id])
    if unit_id in _DIGITAL_SI:
        base = 1024.0 if mode == "iec" else 1000.0
        return bits / 8.0 / (base ** _DIGITAL_SI[unit_id])
    raise ConversionError(f"Unit data '{unit_id}' tidak dikenal.")


def convert_value(
    value: float,
    from_unit: str,
    to_unit: str,
    category: str,
    *,
    mode: str | None = None,
) -> float:
    """Konversi nilai antar unit dalam satu kategori."""
    if not math.isfinite(value):
        raise ConversionError("Nilai tidak valid.")
    cat = get_category(category)
    if cat is None:
        raise ConversionError(f"Kategori '{category}' tidak dikenal.")

    if cat.kind == "temperature":
        return _c_to_temp(_temp_to_c(value, from_unit), to_unit)

    if cat.kind == "digital":
        m = (mode or "si").lower()
        if m not in {"si", "iec"}:
            m = "si"
        return _bits_to_digital(_digital_to_bits(value, from_unit, m), to_unit, m)

    src = _find_unit(cat, from_unit)
    dst = _find_unit(cat, to_unit)
    if src.to_base is None or dst.to_base is None:
        raise ConversionError("Definisi unit tidak lengkap.")
    base = value * src.to_base
    return base / dst.to_base


def convert_all(
    value: float,
    from_unit: str,
    category: str,
    *,
    mode: str | None = None,
) -> list[tuple[str, str, float]]:
    """Konversi ke semua unit dalam kategori. Return [(unit_id,label,result), ...]."""
    cat = get_category(category)
    if cat is None:
        raise ConversionError(f"Kategori '{category}' tidak dikenal.")
    return [(u.unit_id, u.label, convert_value(value, from_unit, u.unit_id, category, mode=mode)) for u in cat.units]
