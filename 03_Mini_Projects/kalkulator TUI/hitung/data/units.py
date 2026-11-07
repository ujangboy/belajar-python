"""Definisi unit untuk konverter (murni, tanpa UI)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UnitDef:
    unit_id: str
    label: str
    to_base: float | None = None  # faktor linear ke unit dasar; None jika khusus
    from_base: float | None = None
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CategoryDef:
    category_id: str
    title: str
    base_unit: str
    units: tuple[UnitDef, ...]
    kind: str = "linear"  # linear | temperature | digital
    note: str = ""


def _lin(uid: str, label: str, to_base: float, *aliases: str) -> UnitDef:
    return UnitDef(uid, label, to_base=to_base, aliases=aliases)


CATEGORIES: dict[str, CategoryDef] = {}


def _add(cat: CategoryDef) -> None:
    CATEGORIES[cat.category_id] = cat


_add(CategoryDef(
    "area", "Luas", "m2",
    (
        _lin("mm2", "mm²", 1e-6),
        _lin("cm2", "cm²", 0.0001),
        _lin("m2", "m²", 1.0),
        _lin("km2", "km²", 1_000_000.0),
        _lin("in2", "Inci persegi (in²)", 0.00064516),
        _lin("ft2", "ft²", 0.09290304),
        _lin("yd2", "Yard persegi (yd²)", 0.83612736),
        _lin("mi2", "Mil persegi (mi²)", 2_589_988.110336),
        _lin("ha", "Hektar (ha)", 10_000.0),
        _lin("acre", "Acre", 4046.8564224),
    ),
))
_add(CategoryDef(
    "length", "Panjang", "m",
    (
        _lin("mm", "Milimeter (mm)", 0.001),
        _lin("cm", "Sentimeter (cm)", 0.01),
        _lin("m", "Meter (m)", 1.0),
        _lin("km", "Kilometer (km)", 1000.0),
        _lin("in", "Inci (in)", 0.0254),
        _lin("ft", "Kaki (ft)", 0.3048),
        _lin("yd", "Yard (yd)", 0.9144),
        _lin("mi", "Mil (mi)", 1609.344),
        _lin("nmi", "Mil laut (nmi)", 1852.0),
    ),
))
_add(CategoryDef(
    "temperature", "Suhu", "c",
    (
        UnitDef("c", "Celsius (°C)"),
        UnitDef("f", "Fahrenheit (°F)"),
        UnitDef("k", "Kelvin (K)"),
        UnitDef("r", "Rankine (°R)"),
    ),
    kind="temperature",
))
_add(CategoryDef(
    "volume", "Volume", "l",
    (
        _lin("ml", "Mililiter (mL)", 0.001),
        _lin("l", "Liter (L)", 1.0),
        _lin("m3", "Meter kubik (m³)", 1000.0),
        _lin("tsp", "Sendok teh (tsp)", 0.00492892159375),
        _lin("tbsp", "Sendok makan (tbsp)", 0.01478676478125),
        _lin("cup", "Cup (US)", 0.2365882365),
        _lin("floz", "Fluid ounce (US fl oz)", 0.0295735295625),
        _lin("gal", "Galon (US)", 3.785411784),
        _lin("imgal", "Galon imperial (imgal)", 4.54609),
    ),
))
_add(CategoryDef(
    "mass", "Massa", "kg",
    (
        _lin("mg", "Miligram (mg)", 1e-6),
        _lin("g", "Gram (g)", 0.001),
        _lin("kg", "Kilogram (kg)", 1.0),
        _lin("t", "Ton metrik (t)", 1000.0),
        _lin("oz", "Ons (oz)", 0.028349523125),
        _lin("lb", "Pon (lb)", 0.45359237),
        _lin("st", "Stone (st)", 6.35029318),
    ),
))
_add(CategoryDef(
    "data", "Data", "b",
    (
        UnitDef("b", "Bit (b)"),
        UnitDef("B", "Byte (B)"),
        UnitDef("KB", "Kilobyte (KB)"),
        UnitDef("MB", "Megabyte (MB)"),
        UnitDef("GB", "Gigabyte (GB)"),
        UnitDef("TB", "Terabyte (TB)"),
        UnitDef("PB", "Petabyte (PB)"),
        UnitDef("KiB", "Kibibyte (KiB)"),
        UnitDef("MiB", "Mebibyte (MiB)"),
        UnitDef("GiB", "Gibibyte (GiB)"),
        UnitDef("TiB", "Tebibyte (TiB)"),
    ),
    kind="digital",
    note="SI: 1 KB = 1000 B. IEC: 1 KiB = 1024 B.",
))
_add(CategoryDef(
    "speed", "Kecepatan", "mps",
    (
        _lin("mps", "m/s", 1.0),
        _lin("kmh", "km/jam", 1 / 3.6),
        _lin("mph", "mil/jam (mph)", 0.44704),
        _lin("fts", "kaki/detik (ft/s)", 0.3048),
        _lin("kn", "knot", 0.5144444444444445),
    ),
))
_add(CategoryDef(
    "time", "Waktu", "s",
    (
        _lin("ms", "Milidetik (ms)", 0.001),
        _lin("s", "Detik (s)", 1.0),
        _lin("min", "Menit", 60.0),
        _lin("h", "Jam", 3600.0),
        _lin("day", "Hari", 86400.0),
        _lin("week", "Minggu", 604800.0),
        _lin("month", "Bulan (30 hari)", 2_592_000.0),
        _lin("year", "Tahun (365 hari)", 31_536_000.0),
    ),
    note="Asumsi: 1 bulan = 30 hari, 1 tahun = 365 hari.",
))


def get_category(category_id: str) -> CategoryDef | None:
    return CATEGORIES.get(category_id)


def list_categories() -> list[CategoryDef]:
    order = ["area", "length", "temperature", "volume", "mass", "data", "speed", "time"]
    return [CATEGORIES[k] for k in order if k in CATEGORIES]
