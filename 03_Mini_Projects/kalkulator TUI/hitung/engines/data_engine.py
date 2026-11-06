"""Mesin data & sistem angka (murni)."""

from __future__ import annotations

from .util import EngineError, to_int

_MASK32 = 0xFFFFFFFF


def number_bases(value: str, from_base: int) -> dict[str, str]:
    bases = {2, 8, 10, 16}
    if from_base not in bases:
        raise EngineError("Basis asal harus 2, 8, 10, atau 16.")
    raw = value.strip().lower().replace("_", "").replace(" ", "")
    if not raw:
        raise EngineError("Nilai tidak boleh kosong.")
    sign = "-" if raw.startswith("-") else ""
    if raw[:1] in "+-":
        raw = raw[1:]
    try:
        n = int(raw, from_base)
    except ValueError as e:
        raise EngineError(f"Nilai '{value}' tidak valid untuk basis {from_base}.") from e
    if sign:
        n = -n
    def fmt(x: int, base: int, prefix: str) -> str:
        neg = "-" if x < 0 else ""
        x = abs(x)
        if base == 2:
            return f"{neg}{prefix}{x:b}"
        if base == 8:
            return f"{neg}{prefix}{x:o}"
        if base == 10:
            return f"{neg}{x}"
        return f"{neg}{prefix}{x:X}"
    return {
        "bin": fmt(n, 2, "0b"),
        "oct": fmt(n, 8, "0o"),
        "dec": fmt(n, 10, ""),
        "hex": fmt(n, 16, "0x"),
        "value": n,
    }


def bitwise(a: int, op: str, b: int | None = None) -> dict[str, object]:
    x = to_int(a, "a") & _MASK32
    operation = op.strip().upper()
    if operation == "NOT":
        r = (~x) & _MASK32
        label = f"NOT {x}"
    else:
        if b is None:
            raise EngineError(f"Operasi {operation} butuh dua nilai.")
        y = to_int(b, "b") & _MASK32
        if operation == "AND":
            r = x & y
        elif operation == "OR":
            r = x | y
        elif operation == "XOR":
            r = x ^ y
        elif operation in {"SHL", "LSHIFT", "<<"}:
            shift = to_int(b, "shift")
            if shift < 0 or shift > 31:
                raise EngineError("Shift harus 0-31.")
            r = (x << shift) & _MASK32
            label = f"{x} << {shift}"
            return _bit_result(label, r)
        elif operation in {"SHR", "RSHIFT", ">>"}:
            shift = to_int(b, "shift")
            if shift < 0 or shift > 31:
                raise EngineError("Shift harus 0-31.")
            r = (x >> shift) & _MASK32
            label = f"{x} >> {shift}"
            return _bit_result(label, r)
        else:
            raise EngineError("Operasi bitwise tidak dikenal.")
        label = f"{x} {operation} {y}"
    return _bit_result(label, r)


def _bit_result(label: str, r: int) -> dict[str, object]:
    return {"label": label, "dec": r, "hex": f"0x{r:X}", "bin": f"0b{r:b}"}
