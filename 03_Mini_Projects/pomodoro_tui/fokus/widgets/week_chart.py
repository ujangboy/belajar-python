"""Grafik batang 7 hari dengan Rich Text."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from ..stats import DayStat
from ..theme import FOCUS, MUTED, TEXT

MAX_BAR = 28


class WeekChart(Static):
    def update_days(self, days: list[DayStat]) -> None:
        max_sessions = max((day.sessions for day in days), default=0)
        text = Text()
        for index, day in enumerate(days):
            width = 0
            if max_sessions > 0 and day.sessions > 0:
                width = max(1, round(day.sessions / max_sessions * MAX_BAR))

            label_style = f"bold {FOCUS}" if index == len(days) - 1 else MUTED
            text.append(f"{day.label}  ", style=label_style)

            if day.sessions:
                text.append("█" * width, style=FOCUS)
                text.append(" " * (MAX_BAR - width + 2))
            else:
                text.append("·", style=MUTED)
                text.append(" " * (MAX_BAR + 1))

            text.append(f"{day.sessions:>2}", style=TEXT)
            if index < len(days) - 1:
                text.append("\n")

        self.update(text)
