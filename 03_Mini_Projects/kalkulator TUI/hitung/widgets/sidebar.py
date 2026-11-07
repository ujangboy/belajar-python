"""Sidebar navigasi KALKULATOR PRO — satu tombol per alat."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Static

from ..navigation import default_tools

# Label pendek supaya muat di sidebar selebar 14 kolom.
SHORT_LABELS = {
    "dashboard": "Dashboard",
    "standard": "Standar",
    "scientific": "Ilmiah",
    "converter": "Konverter",
    "percentage": "Persentase",
    "tip": "Tip",
    "history": "Riwayat",
    "favorites": "Favorit",
    "settings": "Setelan",
    "help": "Bantuan",
}


class Sidebar(Vertical):
    """Daftar alat; tombol memanggil ``app.open_tool``."""

    def compose(self) -> ComposeResult:
        yield Static("KALKULATOR\nPRO", id="side-brand")
        for tool in default_tools():
            label = SHORT_LABELS.get(tool.tool_id, tool.title)
            yield Button(label, id=f"side-{tool.tool_id}", classes="side-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if not button_id.startswith("side-"):
            return
        self.app.open_tool(button_id.removeprefix("side-"))

    def set_active(self, tool_id: str) -> None:
        """Tandai tombol alat yang sedang aktif."""
        for button in self.query(Button):
            if button.id:
                button.set_class(button.id == f"side-{tool_id}", "-active")
