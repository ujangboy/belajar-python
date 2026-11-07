from __future__ import annotations

import pytest

from hitung.data.units import list_categories
from hitung.engines.conversion_engine import ConversionError, convert_all, convert_value


@pytest.mark.parametrize(("v","f","t","c","e"), [
    (0, "c", "f", "temperature", 32.0),
    (100, "c", "f", "temperature", 212.0),
    (273.15, "k", "c", "temperature", 0.0),
    (1, "km", "m", "length", 1000.0),
    (1, "mi", "km", "length", 1.609344),
    (1, "kg", "g", "mass", 1000.0),
    (1, "lb", "oz", "mass", 16.0),
    (1, "l", "ml", "volume", 1000.0),
    (1, "gal", "l", "volume", 3.785411784),
    (1, "m2", "cm2", "area", 10000.0),
    (1, "ha", "m2", "area", 10000.0),
    (100, "kmh", "mps", "speed", 27.7777777778),
    (60, "min", "s", "time", 3600.0),
    (1, "day", "h", "time", 24.0),
])
def test_conversions(v, f, t, c, e):
    assert convert_value(v, f, t, c) == pytest.approx(e)


def test_new_units():
    assert convert_value(1, "r", "c", "temperature") == pytest.approx(-272.5944444444)
    assert convert_value(1, "nmi", "m", "length") == pytest.approx(1852.0)
    assert convert_value(1, "st", "kg", "mass") == pytest.approx(6.35029318)
    assert convert_value(1, "imgal", "l", "volume") == pytest.approx(4.54609)
    assert convert_value(1, "in2", "m2", "area") == pytest.approx(0.00064516)
    assert convert_value(1, "yd2", "m2", "area") == pytest.approx(0.83612736)
    assert convert_value(1, "mi2", "m2", "area") == pytest.approx(2589988.110336)
    assert convert_value(1, "fts", "mps", "speed") == pytest.approx(0.3048)
    assert convert_value(1, "KiB", "B", "data", mode="iec") == 1024.0
    assert convert_value(1, "MiB", "KiB", "data", mode="iec") == 1024.0
    assert convert_value(1, "GiB", "MiB", "data") == 1024.0


def test_digital_si_vs_iec():
    assert convert_value(1, "KB", "B", "data", mode="si") == 1000.0
    assert convert_value(1, "KB", "B", "data", mode="iec") == 1024.0
    assert convert_value(8, "b", "B", "data") == 1.0
    assert convert_value(1, "MB", "KB", "data", mode="iec") == 1024.0


def test_category_order_matches_design():
    ids = [category.category_id for category in list_categories()]
    assert ids == [
        "area",
        "length",
        "temperature",
        "volume",
        "mass",
        "data",
        "speed",
        "time",
    ]


def test_convert_all_includes_units():
    rows = convert_all(1, "m", "length")
    assert any(uid == "cm" and val == pytest.approx(100.0) for uid, _l, val in rows)
    assert len(rows) == 9


@pytest.mark.parametrize(("v","f","t","c","msg"), [
    (1, "x", "m", "length", "tidak dikenal"),
    (1, "m", "m", "nope", "tidak dikenal"),
    (float("nan"), "m", "cm", "length", "tidak valid"),
])
def test_conversion_errors(v, f, t, c, msg):
    with pytest.raises(ConversionError) as info:
        convert_value(v, f, t, c)
    assert msg in str(info.value).lower()
