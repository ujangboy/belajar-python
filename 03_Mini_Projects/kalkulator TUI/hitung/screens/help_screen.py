"""Modal bantuan: tombol, operator, fungsi, dan contoh."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from ..theme import MUTED, PRIMARY, TEXT

KEYS = (
    ("Tombol", "klik angka/operator; = menghitung dan menyimpan"),
    ("Esc", "bersihkan entri atau kembali ke dashboard"),
    ("↑ / ↓", "riwayat ekspresi; di konverter pindah FROM/TO"),
    ("Ctrl+Y", "salin hasil ke clipboard"),
    ("Ctrl+1/2/3", "kalkulator standar / ilmiah / konverter"),
    ("Ctrl+H", "dashboard"),
    ("Ctrl+K", "cari alat"),
    ("Ctrl+F", "lihat favorit"),
    ("Ctrl+D", "tandai alat aktif sebagai favorit"),
    ("F1/F2/F3", "bantuan / riwayat / pengaturan"),
    ("Ctrl+Q", "keluar"),
)

SHORTCUTS = "Semua angka dan fungsi bisa diklik; keyboard tetap bisa dipakai."

FUNCTIONS = (
    "sqrt  cbrt  abs  sin  cos  tan  asin  acos  atan\n"
    "log   ln   log10  exp  floor  ceil  round  ncr  npr"
)

CONSTANTS = "pi = 3,14159…   e = 2,71828…   tau = 6,28318…   ans = hasil terakhir"


class HelpScreen(ModalScreen[None]):
    BINDINGS = [
        ("escape", "close", "Kembali"),
        ("f1", "close", "Tutup"),
    ]

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="help-box"):
            yield Static("Bantuan", id="help-title")
            yield Static(self._help_text(), id="help-text")

    def _help_text(self) -> Text:
        text = Text()

        text.append("TOMBOL & PINTASAN\n", style=f"bold {PRIMARY}")
        for key, description in KEYS:
            text.append(f"{key:<11}", style=f"bold {TEXT}")
            text.append(description, style=MUTED)
            text.append("\n")
        text.append(SHORTCUTS, style=MUTED)

        text.append("\nOPERATOR & SIMBOL\n", style=f"bold {PRIMARY}")
        text.append(
            "+  −  ×  ÷  ^  %  !  (  )  ← hapus  ⇄ tukar\n"
            "Desimal boleh koma atau titik (1,5 atau 1.5).",
            style=MUTED,
        )

        text.append("\nFUNGSI\n", style=f"bold {PRIMARY}")
        text.append(FUNCTIONS, style=MUTED)

        text.append("\nKONSTANTA\n", style=f"bold {PRIMARY}")
        text.append(CONSTANTS, style=MUTED)

        text.append("\nCONTOH\n", style=f"bold {PRIMARY}")
        text.append(
            "12 × 3 + (4 − 1)  = 35\n"
            "200 + 10%         = 220  (persen kontekstual)\n"
            "sin 30            = 0,5  (mode derajat)\n"
            "5!                = 120\n"
            "∛27               = 3\n"
            "Rp150.000 · 15%   = tip Rp22.500",
            style=MUTED,
        )
        return text

    def action_close(self) -> None:
        self.dismiss(None)
