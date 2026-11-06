"""Modal bantuan: tombol, operator, fungsi, dan contoh."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from ..theme import MUTED, PRIMARY, TEXT

KEYS = (
    ("Enter", "hitung dan simpan ke riwayat"),
    ("Esc", "bersihkan ekspresi"),
    ("↑ / ↓", "panggil ekspresi sebelumnya / berikutnya"),
    ("Ctrl+Y", "salin hasil ke clipboard"),
    ("Ctrl+Q", "keluar"),
)

SHORTCUTS = "F1 bantuan · F2 riwayat · F3 pengaturan · F4 mode ringkas"

FUNCTIONS = (
    "sqrt  abs  sin  cos  tan  asin  acos  atan\n"
    "log   ln   exp  floor  ceil  round"
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

        text.append("TOMBOL\n", style=f"bold {PRIMARY}")
        for key, description in KEYS:
            text.append(f"{key:<9}", style=f"bold {TEXT}")
            text.append(description, style=MUTED)
            text.append("\n")
        text.append(SHORTCUTS, style=MUTED)

        text.append("\nOPERATOR\n", style=f"bold {PRIMARY}")
        text.append(
            "+  -  *  /  ^  %  !  (  )\n"
            "Desimal boleh koma atau titik (1,5 atau 1.5).",
            style=MUTED,
        )

        text.append("\nFUNGSI\n", style=f"bold {PRIMARY}")
        text.append(FUNCTIONS, style=MUTED)

        text.append("\nKONSTANTA\n", style=f"bold {PRIMARY}")
        text.append(CONSTANTS, style=MUTED)

        text.append("\nCONTOH\n", style=f"bold {PRIMARY}")
        text.append(
            "12 + 3 * (4 - 1)  = 21\n"
            "sqrt(144) + 2^3   = 20\n"
            "200 * 15%         = 30\n"
            "sin(30)           = 0,5  (mode derajat)",
            style=MUTED,
        )
        return text

    def action_close(self) -> None:
        self.dismiss(None)
