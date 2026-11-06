"""Tool registry untuk navigasi Calculator Pro."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from textual.widget import Widget


@dataclass(frozen=True, slots=True)
class ToolSpec:
    tool_id: str
    title: str
    category: str
    description: str
    shortcut: str | None = None
    keywords: tuple[str, ...] = ()


def default_tools() -> list[ToolSpec]:
    return [
        ToolSpec("dashboard", "Dashboard", "Sistem", "Beranda semua alat", "Ctrl+H", ("home", "beranda")),
        ToolSpec("standard", "Kalkulator Standar", "Kalkulator", "Ekspresi harian, riwayat, ans", "Ctrl+1", ("hitung", "basic")),
        ToolSpec("scientific", "Kalkulator Ilmiah", "Kalkulator", "Fungsi trigonometri, log, faktorial", "Ctrl+2", ("sin", "cos", "log")),
        ToolSpec("converter", "Konverter Unit", "Konverter", "Suhu, panjang, berat, volume, data, dll.", "Ctrl+3", ("unit", "convert")),
        ToolSpec("percentage", "Persentase", "Sehari-hari", "Diskon, pajak, tip, perubahan", None, ("discount", "tax")),
        ToolSpec("date", "Tanggal & Waktu", "Waktu", "Selisih hari, usia, timestamp", None, ("age", "unix")),
        ToolSpec("finance", "Keuangan", "Keuangan", "Bunga, pinjaman, cicilan", None, ("loan", "interest")),
        ToolSpec("math", "Matematika", "Matematika", "FPB, KPK, prima, statistik", None, ("gcd", "prime")),
        ToolSpec("data", "Data & Sistem Angka", "Data", "Bin/Des/Hex, bitwise, ukuran data", None, ("binary", "hex")),
        ToolSpec("electrical", "Kelistrikan", "Teknik", "Hukum Ohm dan daya", None, ("ohm", "volt")),
    ]


def find_tool(tools: list[ToolSpec], query: str) -> list[ToolSpec]:
    q = query.strip().lower()
    if not q:
        return list(tools)
    matches: list[ToolSpec] = []
    for tool in tools:
        hay = " ".join((tool.tool_id, tool.title, tool.category, tool.description, *tool.keywords)).lower()
        if q in hay:
            matches.append(tool)
    return matches
