"""Bar atas: nama app, subjudul, dan jam."""

from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

HARI = ("Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min")
BULAN = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "Mei",
    "Jun",
    "Jul",
    "Agu",
    "Sep",
    "Okt",
    "Nov",
    "Des",
)


class TopBar(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("FOKUS", id="brand")
        yield Static("pomodoro untuk belajar", id="subtitle")
        yield Static("", id="clock")

    def on_mount(self) -> None:
        self._update_clock()
        self.set_interval(1.0, self._update_clock)

    def _update_clock(self) -> None:
        now = datetime.now()
        text = (
            f"{HARI[now.weekday()]}, {now.day} {BULAN[now.month - 1]}"
            f" · {now:%H:%M}"
        )
        self.query_one("#clock", Static).update(text)
