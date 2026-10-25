"""Layar statistik."""

from __future__ import annotations

from datetime import date, timedelta

from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static

from ..stats import (
    WEEKDAYS,
    last_seven_days,
    recent_sessions,
    streak,
    today_summary,
    week_summary,
)
from ..theme import MUTED, SUCCESS, TEXT
from ..widgets.week_chart import WeekChart


class StatsScreen(ModalScreen[None]):
    BINDINGS = [
        ("escape", "close", "Kembali"),
        ("t", "close", "Tutup"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="stats-box"):
            yield Static("Statistik", id="stats-title")
            yield Static(id="stats-summary")
            yield Static("7 HARI TERAKHIR", classes="section-label")
            yield WeekChart(id="week-chart")
            yield Static("SESI TERAKHIR", classes="section-label")
            yield Static(id="recent")
            yield Static("esc kembali", id="stats-hint")

    def on_mount(self) -> None:
        records = self.app.storage.load_sessions()
        today = date.today()

        sessions, minutes = today_summary(records, today)
        week_sessions, week_minutes = week_summary(records, today)
        streak_days = streak(records, today)

        summary = Table.grid(expand=True, padding=(0, 2))
        summary.add_column()
        summary.add_column()
        summary.add_column()
        summary.add_row(
            Text("Hari ini", style=MUTED),
            Text("7 hari", style=MUTED),
            Text("Streak", style=MUTED),
        )
        summary.add_row(
            Text.assemble(
                (f"{sessions} sesi", f"bold {TEXT}"),
                (f" · {minutes} mnt", MUTED),
            ),
            Text.assemble(
                (f"{week_sessions} sesi", f"bold {TEXT}"),
                (f" · {week_minutes} mnt", MUTED),
            ),
            Text.assemble((f"{streak_days} hari", f"bold {TEXT}")),
        )
        self.query_one("#stats-summary", Static).update(summary)

        self.query_one(WeekChart).update_days(last_seven_days(records, today))

        recent = recent_sessions(records, limit=3)
        if recent:
            text = Text()
            for index, record in enumerate(recent):
                ended = record.ended_at.astimezone()
                day = ended.date()
                if day == today:
                    day_label = "Hari ini"
                elif day == today - timedelta(days=1):
                    day_label = "Kemarin"
                else:
                    day_label = WEEKDAYS[day.weekday()]
                duration = record.actual_seconds // 60
                text.append(f"{day_label:<8} ", style=MUTED)
                text.append(f"{ended:%H:%M}  ", style=MUTED)
                text.append(f"Fokus {duration} mnt", style=TEXT)
                text.append("  ✓", style=SUCCESS)
                if index < len(recent) - 1:
                    text.append("\n")
            self.query_one("#recent", Static).update(text)
        else:
            self.query_one("#recent", Static).update(
                Text("Belum ada sesi. Mulai pomodoro pertamamu.", style=MUTED)
            )

    def action_close(self) -> None:
        self.dismiss(None)
