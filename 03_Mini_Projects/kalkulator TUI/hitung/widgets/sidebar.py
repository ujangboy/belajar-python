"""Sidebar navigasi HITUNG — grup + indikator aktif + keyboard nav."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Button, Static

# (section_label, [(tool_id, icon, label), ...])
SECTIONS: tuple[tuple[str, tuple[tuple[str, str, str], ...]], ...] = (
    (
        "MAIN",
        (
            ("dashboard", "▸", "Dashboard"),
            ("standard", "▸", "Standard"),
            ("scientific", "▸", "Scientific"),
        ),
    ),
    ("CONVERTER", (("converter", "▸", "Unit Converter"),)),
    (
        "OTHER TOOLS",
        (
            ("percentage", "▸", "Percentage"),
            ("tip", "▸", "Tip"),
            ("history", "▸", "History"),
            ("favorites", "▸", "Favorites"),
        ),
    ),
    (
        "SETTINGS",
        (
            ("settings", "▸", "Settings"),
            ("help", "▸", "Help"),
        ),
    ),
)


class Sidebar(Vertical):
    """Daftar alat; tombol memanggil ``app.open_tool``."""

    can_focus = False

    BINDINGS = [
        Binding("up", "nav_up", show=False),
        Binding("down", "nav_down", show=False),
        Binding("enter", "nav_activate", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Static("HITUNG", id="side-brand-title", classes="side-brand")
        yield Static("Calculator Pro", id="side-brand-sub", classes="side-brand-sub")
        for section, items in SECTIONS:
            yield Static(section, classes="side-section")
            for tool_id, icon, label in items:
                yield Button(f"{icon}  {label}", id=f"side-{tool_id}", classes="side-btn")

    def _nav_buttons(self) -> list[Button]:
        buttons: list[Button] = []
        for button in self.query(".side-btn"):
            if isinstance(button, Button):
                buttons.append(button)
        return buttons

    def _focus_current(self) -> None:
        buttons = self._nav_buttons()
        for button in buttons:
            if button.has_class("-active"):
                button.focus()
                return
        if buttons:
            buttons[0].focus()

    def action_nav_up(self) -> None:
        buttons = self._nav_buttons()
        if not buttons:
            return
        focused = self.app.focused
        if focused not in buttons:
            self._focus_current()
            return
        idx = buttons.index(focused)
        buttons[(idx - 1) % len(buttons)].focus()

    def action_nav_down(self) -> None:
        buttons = self._nav_buttons()
        if not buttons:
            return
        focused = self.app.focused
        if focused not in buttons:
            self._focus_current()
            return
        idx = buttons.index(focused)
        buttons[(idx + 1) % len(buttons)].focus()

    def action_nav_activate(self) -> None:
        focused = self.app.focused
        if isinstance(focused, Button) and focused.id and focused.id.startswith("side-"):
            self.app.open_tool(focused.id.removeprefix("side-"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if not button_id.startswith("side-"):
            return
        event.stop()
        self.app.open_tool(button_id.removeprefix("side-"))

    def set_active(self, tool_id: str) -> None:
        """Tandai tombol alat yang sedang aktif (indikator tetap terlihat)."""
        for button in self.query(".side-btn"):
            if button.id:
                button.set_class(button.id == f"side-{tool_id}", "-active")
