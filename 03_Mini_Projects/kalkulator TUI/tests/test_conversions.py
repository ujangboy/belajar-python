from __future__ import annotations

import pytest

from hitung.engines.conversion_engine import ConversionError, convert_all, convert_value


@pytest.mark.parametrize(("v","f","t","c","e"), [
    (0, "c", "f", "temperature", 32.0),
    (100, "c", "f", "temperature", 212.0),
    (273.15, "k", "c", "temperature", 0.0),
    (1, "km", "m", "length", 1000.0),
    (1, "mi", "km", "length", 1.609344),
    (1, "kg", "g", "weight", 1000.0),
    (1, "lb", "oz", "weight", 16.0),
    (1, "l", "ml", "volume", 1000.0),
    (1, "gal", "l", "volume", 3.785411784),
    (1, "m2", "cm2", "area", 10000.0),
    (1, "ha", "m2", "area", 10000.0),
    (100, "kmh", "mps", "speed", 27.7777777778),
    (60, "min", "s", "time", 3600.0),
    (1, "day", "h", "time", 24.0),
    (1, "bar", "pa", "pressure", 100000.0),
    (1, "kwh", "j", "energy", 3_600_000.0),
    (1, "hp", "w", "power", 745.6998715822702),
    (180, "deg", "rad", "angle", 3.141592653589793),
])
def test_conversions(v, f, t, c, e):
    assert convert_value(v, f, t, c) == pytest.approx(e)


def test_digital_si_vs_iec():
    assert convert_value(1, "KB", "B", "digital", mode="si") == 1000.0
    assert convert_value(1, "KB", "B", "digital", mode="iec") == 1024.0
    assert convert_value(8, "b", "B", "digital") == 1.0
    assert convert_value(1, "MB", "KB", "digital", mode="iec") == 1024.0


def test_convert_all_includes_units():
    rows = convert_all(1, "m", "length")
    assert any(uid == "cm" and val == pytest.approx(100.0) for uid, _l, val in rows)
    assert len(rows) == 8


@pytest.mark.parametrize(("v","f","t","c","msg"), [
    (1, "x", "m", "length", "tidak dikenal"),
    (1, "m", "m", "nope", "tidak dikenal"),
    (float("nan"), "m", "cm", "length", "tidak valid"),
])
def test_conversion_errors(v, f, t, c, msg):
    with pytest.raises(ConversionError) as info:
        convert_value(v, f, t, c)
    assert msg in str(info.value).lower()
