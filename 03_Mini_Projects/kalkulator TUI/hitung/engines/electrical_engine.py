"""Mesin kelistrikan (Hukum Ohm, murni)."""

from __future__ import annotations

from .util import EngineError, to_float


def ohms_law(*, voltage: float | None = None, current: float | None = None, resistance: float | None = None) -> dict[str, object]:
    known = [voltage is not None, current is not None, resistance is not None]
    if sum(1 for k in known if k) != 2:
        raise EngineError("Isi tepat 2 dari: tegangan (V), arus (I), hambatan (R).")
    v = to_float(voltage, "tegangan") if voltage is not None else None
    i = to_float(current, "arus") if current is not None else None
    r = to_float(resistance, "hambatan") if resistance is not None else None
    if v is None:
        assert i is not None and r is not None
        v = i * r
        formula = "V = I × R"
    elif i is None:
        assert v is not None and r is not None
        if r == 0:
            raise EngineError("Hambatan nol menyebabkan arus tak terdefinisi.")
        i = v / r
        formula = "I = V / R"
    else:
        assert v is not None and i is not None
        if i == 0:
            raise EngineError("Arus nol menyebabkan hambatan tak terdefinisi.")
        r = v / i
        formula = "R = V / I"
    p = v * i
    return {"voltage": v, "current": i, "resistance": r, "power": p, "formula": formula, "units": "V, A, Ω, W"}


def power(*, voltage: float | None = None, current: float | None = None, resistance: float | None = None) -> float:
    res = ohms_law(voltage=voltage, current=current, resistance=resistance)
    return float(res["power"])
