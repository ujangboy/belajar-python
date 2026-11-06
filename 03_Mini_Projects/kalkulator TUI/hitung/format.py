"""Format angka gaya Indonesia: titik ribuan, koma desimal.

Contoh::

    1234567.5   ->  "1.234.567,5"
    1/3         ->  "0,333333"   (presisi 6)
    1500000000000 -> "1,5e+12"
"""

from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext

DEFAULT_PRECISION = 6
MAX_PRECISION = 10

# Di atas batas ini angka ditulis dalam notasi ilmiah supaya tetap terbaca.
SCIENTIFIC_HIGH = 10**12


def format_number(
    value: float,
    *,
    precision: int = DEFAULT_PRECISION,
    thousands: bool = True,
    number_format: str = "id",
) -> str:
    """Format angka untuk ditampilkan.

    ``precision`` = jumlah digit di belakang koma (0-10),
    ``thousands`` = pakai titik pemisah ribuan.
    ``number_format`` = "id" (1.234,56) atau "plain" (1234.56).
    """
    precision = max(0, min(MAX_PRECISION, int(precision)))
    if number_format == "plain":
        thousands = False

    if not math.isfinite(value):
        return "Tak terhingga"
    if value == 0:
        return "0"

    absolute = abs(value)
    if absolute >= SCIENTIFIC_HIGH:
        digits = max(1, precision)
        return f"{value:.{digits}g}".replace(".", ",")

    rounded = _round_half_up(value, precision)
    if rounded == 0:
        # Angka terlalu kecil untuk presisi ini: pakai notasi ilmiah.
        digits = max(1, precision)
        return f"{value:.{digits}g}".replace(".", ",")

    text = f"{rounded:f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")

    sign = ""
    if text.startswith("-"):
        sign, text = "-", text[1:]

    integer, _, fraction = text.partition(".")
    if thousands:
        integer = _group_thousands(integer)

    sep = "," if number_format != "plain" else "."
    if fraction:
        return f"{sign}{integer}{sep}{fraction}"
    return f"{sign}{integer}"


def _round_half_up(value: float, precision: int) -> Decimal:
    """Bulatkan setengah ke atas (2,5 -> 3), bukan banker's rounding."""
    quantum = Decimal(1).scaleb(-precision)
    with localcontext() as context:
        context.prec = 40
        try:
            return Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP)
        except InvalidOperation:
            return Decimal(str(value))


def _group_thousands(digits: str) -> str:
    if len(digits) <= 3:
        return digits
    groups: list[str] = []
    while digits:
        groups.append(digits[-3:])
        digits = digits[:-3]
    return ".".join(reversed(groups))
