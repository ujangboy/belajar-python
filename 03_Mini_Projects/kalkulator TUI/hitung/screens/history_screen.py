"""Layar riwayat: ringkasan, grafik 7 hari, dan daftar hitungan."""

from __future__ import annotations

from datetime import date, timedelta

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ..history import (
    WEEKDAYS,
    HistoryRecord,
    last_seven_days,
    recent_records,
    today_count,
    total_count,
    week_total,
)
from ..text import shorten
from ..theme import MUTED, PRIMARY, TEXT
from ..widgets.week_chart import WeekChart
from .confirm import ConfirmScreen

ENTRY_LIMIT = 50
EXPRESSION_WIDTH = 28


class HistoryScreen(ModalScreen[object]):
    BINDINGS = [
        ("escape", "close", "Kembali"),
        ("f2", "close", "Tutup"),
    ]

    def __init__(self, records: list[HistoryRecord], today: date | None = None) -> None:
        super().__init__()
        self._records = list(records)
        self._today = today or date.today()

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="history-box"):
            yield Static("Riwayat", id="history-title")
            yield Static(id="history-summary")
            yield Static("7 HARI TERAKHIR", classes="section-label")
            yield WeekChart(id="week-chart")
            yield Static("HITUNGAN TERBARU", classes="section-label")
            with VerticalScroll(id="history-scroll"):
                yield Static(id="history-entries")
            with Horizontal(id="history-buttons"):
                yield Button("Hapus semua", id="clear", variant="error")
                yield Button("Tutup", id="close", variant="primary")

    def on_mount(self) -> None:
        records = self._records
        today = self._today
        summary = Text(
            f"Total {total_count(records)} hitungan  -  Hari ini {today_count(records, today)} hitungan  -  7 hari {week_total(records, today)} hitungan",
            style=MUTED,
        )
        self.query_one("#history-summary", Static).update(summary)
        self.query_one(WeekChart).update_days(last_seven_days(records, today))
        entries_widget = self.query_one("#history-entries", Static)
        recent = list(reversed(records))[:ENTRY_LIMIT]
        if not recent:
            entries_widget.update(Text("Belum ada riwayat. Hitung sesuatu dulu.", style=MUTED))
            return
        text = Text()
        for index, record in enumerate(recent):
            ended = record.at.astimezone()
            day = ended.date()
            if day == today:
                day_label = "Hari ini"
            elif day == today - timedelta(days=1):
                day_label = "Kemarin"
            else:
                day_label = f"{WEEKDAYS[day.weekday()]} {day.day}/{day.month}"
            expression = shorten(record.expression, EXPRESSION_WIDTH)
            cat = getattr(record, "category", "standard") or "standard"
            text.append(f"{day_label:<10} {ended:%H:%M}  ", style=MUTED)
            text.append(f"[{cat}] ", style=MUTED)
            text.append(f"{expression:<{EXPRESSION_WIDTH}} ", style=TEXT)
            text.append(f"= {record.result}", style=f"bold {PRIMARY}")
            if index < len(recent) - 1:
                text.append("\n")
        entries_widget.update(text)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "clear":
            self.app.push_screen(
                ConfirmScreen(
                    "Hapus semua riwayat?",
                    "Semua riwayat hitungan di perangkat ini akan dihapus. Tindakan ini tidak bisa dibatalkan.",
                    confirm_label="Hapus",
                    destructive=True,
                ),
                self._after_clear,
            )
        elif event.button.id == "close":
            self.dismiss(None)

    def _after_clear(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        try:
            self.app.storage.clear_history()  # type: ignore[attr-defined]
        except OSError as error:
            self.notify(f"Gagal menghapus riwayat: {error}", title="Penyimpanan gagal", severity="error", timeout=8)
            return
        self.dismiss(True)

    def action_close(self) -> None:
        self.dismiss(None)
