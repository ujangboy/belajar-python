"""Modal pencarian alat global."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from ..navigation import default_tools, find_tool


class SearchScreen(ModalScreen[str | None]):
    BINDINGS = [("escape", "close", "Tutup")]

    def compose(self) -> ComposeResult:
        with Container(id="search-box"):
            yield Static("Cari Alat (Ctrl+K)", id="search-title")
            yield Input(placeholder="Ketik nama/kategori/fungsi…", id="search-input")
            with VerticalScroll(id="search-list-wrap"):
                yield Container(id="search-list")
            with Container(id="search-buttons"):
                yield Button("Tutup", id="search-close")

    def on_mount(self) -> None:
        self._tools = [t for t in default_tools() if t.tool_id != "dashboard"]
        self._render("")
        self.query_one("#search-input", Input).focus()

    def _render(self, query: str) -> None:
        container = self.query_one("#search-list", Container)
        container.remove_children()
        for tool in find_tool(self._tools, query):
            hint = f" · {tool.shortcut}" if tool.shortcut else ""
            container.mount(Button(f"{tool.title}{hint} — {tool.category}", id=f"open-{tool.tool_id}", classes="search-item"))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self._render(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "search-close":
            self.dismiss(None)
        elif bid.startswith("open-"):
            self.dismiss(bid.removeprefix("open-"))

    def action_close(self) -> None:
        self.dismiss(None)
