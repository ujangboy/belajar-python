"""Panel riwayat singkat di samping kartu."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from ..history import HistoryRecord, recent_records
from ..text import shorten
from ..theme import MUTED, PRIMARY

ENTRY_LIMIT = 5
EXPRESSION_WIDTH = 15
RESULT_WIDTH = 9


class HistoryPanel(Vertical):
    can_focus = False

    def compose(self) -> ComposeResult:
        yield Static("RIWAYAT", id="history-title")
        yield Static("", id="history-list")
        yield Static("F2 lihat semua", id="history-hint")

    def update_view(self, records: list[HistoryRecord]) -> None:
        recent = recent_records(records, ENTRY_LIMIT)
        list_widget = self.query_one("#history-list", Static)

        if not recent:
            list_widget.update(Text("Belum ada hitungan.", style=MUTED))
            return

        text = Text()
        for index, record in enumerate(recent):
            expression = shorten(record.expression, EXPRESSION_WIDTH)
            result = shorten(record.result, RESULT_WIDTH)
            text.append(f"{expression:<{EXPRESSION_WIDTH}} ", style=MUTED)
            text.append(f"= {result}", style=f"bold {PRIMARY}")
            if index < len(recent) - 1:
                text.append("\n")
        list_widget.update(text)
