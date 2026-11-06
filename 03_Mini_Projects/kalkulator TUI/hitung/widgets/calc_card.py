"""Kartu utama: hasil besar, input ekspresi, dan baris status."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Static

from ..text import shorten
from ..theme import MUTED

MAX_LAST_EXPRESSION = 44


class CalcCard(Vertical):
    can_focus = False

    def compose(self) -> ComposeResult:
        yield Static("HASIL", id="result-label")
        yield Static("0", id="result")
        yield Static("", id="last")
        yield Static("EKSPRESI", id="expr-label")
        yield Input(
            placeholder="mis. 12 + 3 * (4 - 1)   ·   ans * 2",
            id="expr",
        )
        yield Static("", id="status")

    def show_result(self, text: str, *, preview: bool = False) -> None:
        result = self.query_one("#result", Static)
        result.update(text)
        result.set_class(preview, "-preview")

    def show_last(self, expression: str, result: str) -> None:
        short = shorten(expression, MAX_LAST_EXPRESSION)
        self.query_one("#last", Static).update(
            Text(f"terakhir: {short} = {result}", style=MUTED)
        )

    def show_status(self, text: str, *, error: bool = False) -> None:
        status = self.query_one("#status", Static)
        status.update(text)
        status.set_class(error, "-error")
