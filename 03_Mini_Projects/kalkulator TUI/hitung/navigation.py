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
        ToolSpec("standard", "Kalkulator Standar", "Kalkulator", "Tombol angka dan operator harian", "Ctrl+1", ("hitung", "basic")),
        ToolSpec("scientific", "Kalkulator Ilmiah", "Kalkulator", "Trigonometri, log, pangkat, faktorial", "Ctrl+2", ("sin", "cos", "log")),
        ToolSpec("converter", "Konverter Unit", "Konverter", "Suhu, panjang, berat, volume, data, dll.", "Ctrl+3", ("unit", "convert")),
        ToolSpec("percentage", "Persentase", "Sehari-hari", "X% dari Y, perubahan, diskon, pajak", None, ("discount", "tax")),
        ToolSpec("tip", "Tip", "Sehari-hari", "Tip, total tagihan, pembagian per orang", None, ("tip", "gratuity")),
        ToolSpec("history", "Riwayat", "Sistem", "Semua hitungan tersimpan", "F2", ("history", "riwayat")),
        ToolSpec("favorites", "Favorit", "Sistem", "Alat yang ditandai favorit", "Ctrl+F", ("favorite", "favorit")),
        ToolSpec("settings", "Pengaturan", "Sistem", "Presisi, sudut, tema, suara", "F3", ("settings", "pengaturan")),
        ToolSpec("help", "Bantuan", "Bantuan", "Cara pakai dan peta tombol", "F1", ("help", "bantuan")),
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
