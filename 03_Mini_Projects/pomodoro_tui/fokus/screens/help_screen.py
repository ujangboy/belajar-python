"""Modal bantuan dan keybinding."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static

from ..theme import MUTED, TEXT

KEYS = (
    ("Space", "mulai / jeda"),
    ("s", "lewati fase"),
    ("r", "reset timer"),
    ("z", "mode zen"),
    ("t", "statistik"),
    ("c", "pengaturan"),
    ("?", "bantuan"),
    ("q", "keluar"),
)


class HelpScreen(ModalScreen[None]):
    BINDINGS = [
        ("escape", "close", "Kembali"),
        ("question_mark", "close", "Tutup"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="help-box"):
            yield Static("Bantuan", id="help-title")
            yield Static(self._help_text(), id="help-text")
            yield Static("esc kembali", id="help-hint")

    def _help_text(self) -> Text:
        text = Text()
        for key, description in KEYS:
            text.append(f"{key:<7}", style=f"bold {TEXT}")
            text.append(description, style=MUTED)
            text.append("\n")

        text.append("\n")
        text.append("Alur default", style=f"bold {TEXT}")
        text.append("\n")
        text.append(
            "25 menit fokus → 5 menit istirahat\n"
            "Setelah 4 sesi fokus → 15 menit istirahat panjang\n"
            "Istirahat dimulai otomatis; fokus selalu dimulai manual.",
            style=MUTED,
        )
        return text

    def action_close(self) -> None:
        self.dismiss(None)
