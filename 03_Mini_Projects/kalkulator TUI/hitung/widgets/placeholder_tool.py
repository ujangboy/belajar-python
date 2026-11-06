"""Placeholder untuk tool yang belum diimplementasikan."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.widgets import Button, Static


class PlaceholderTool(Vertical):
    DEFAULT_CSS = """
    PlaceholderTool { height: 1fr; align: center middle; padding: 2; }
    #ph-title { color: $primary; text-style: bold; }
    #ph-body { color: $text-muted; margin: 1 0; text-align: center; }
    """

    def __init__(self, title: str, body: str, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self._title = title
        self._body = body

    def compose(self) -> ComposeResult:
        with Center():
            yield Static(self._title, id="ph-title")
            yield Static(self._body, id="ph-body")
            yield Button("Kembali ke Dashboard (Ctrl+H)", id="ph-home", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ph-home":
            self.app.action_go_dashboard()
