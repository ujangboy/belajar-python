"""Grafik batang 7 hari (jumlah hitungan) dengan Rich Text."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from ..history import DayStat
from ..theme import MUTED, PRIMARY, TEXT

MAX_BAR = 26


class WeekChart(Static):
    def update_days(self, days: list[DayStat]) -> None:
        maximum = max((day.count for day in days), default=0)
        text = Text()
        for index, day in enumerate(days):
            width = 0
            if maximum > 0 and day.count > 0:
                width = max(1, round(day.count / maximum * MAX_BAR))

            label_style = f"bold {PRIMARY}" if index == len(days) - 1 else MUTED
            text.append(f"{day.label}  ", style=label_style)

            if day.count:
                text.append("█" * width, style=PRIMARY)
                text.append(" " * (MAX_BAR - width + 2))
            else:
                text.append("·", style=MUTED)
                text.append(" " * (MAX_BAR + 1))

            text.append(f"{day.count:>2}", style=TEXT)
            if index < len(days) - 1:
                text.append("\n")

        self.update(text)
