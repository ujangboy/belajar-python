"""Riwayat hitungan: record, agregasi harian, dan daftar panggil ulang."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

WEEKDAYS = ("Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min")


@dataclass(frozen=True, slots=True)
class HistoryRecord:
    """Satu perhitungan yang sudah disimpan."""

    at: datetime
    expression: str
    result: str
    value: float
    category: str = "standard"
    input_text: str | None = None
    output_text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "at": self.at.isoformat(),
            "expression": self.expression,
            "result": self.result,
            "value": self.value,
            "category": self.category,
        }
        if self.input_text is not None:
            payload["input"] = self.input_text
        if self.output_text is not None:
            payload["output"] = self.output_text
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HistoryRecord | None":
        try:
            at = datetime.fromisoformat(str(data["at"]))
            expression = str(data["expression"]).strip()
            result = str(data["result"]).strip()
            value = float(data["value"])
        except (KeyError, TypeError, ValueError):
            return None

        if not expression or not result:
            return None
        if not math.isfinite(value):
            return None

        raw_category = data.get("category", "standard")
        category = str(raw_category).strip() if raw_category is not None else "standard"
        if not category:
            category = "standard"

        def _text(key: str) -> str | None:
            raw = data.get(key)
            if raw is None:
                return None
            text = str(raw)
            return text if text != "" else None

        return cls(
            at=at,
            expression=expression,
            result=result,
            value=value,
            category=category,
            input_text=_text("input"),
            output_text=_text("output"),
        )


@dataclass(frozen=True, slots=True)
class DayStat:
    day: date
    label: str
    count: int


def _day(record: HistoryRecord) -> date:
    return record.at.date()


def today_count(
    records: Iterable[HistoryRecord],
    today: date | None = None,
) -> int:
    day = today or date.today()
    return sum(1 for record in records if _day(record) == day)


def total_count(records: Iterable[HistoryRecord]) -> int:
    return sum(1 for _ in records)


def last_seven_days(
    records: Iterable[HistoryRecord],
    today: date | None = None,
) -> list[DayStat]:
    day = today or date.today()
    by_day: dict[date, int] = {}
    for record in records:
        key = _day(record)
        by_day[key] = by_day.get(key, 0) + 1

    days: list[DayStat] = []
    for offset in range(6, -1, -1):
        current = day - timedelta(days=offset)
        days.append(
            DayStat(
                day=current,
                label=WEEKDAYS[current.weekday()],
                count=by_day.get(current, 0),
            )
        )
    return days


def week_total(
    records: Iterable[HistoryRecord],
    today: date | None = None,
) -> int:
    return sum(day.count for day in last_seven_days(records, today))


def recent_records(
    records: Iterable[HistoryRecord],
    limit: int = 5,
) -> list[HistoryRecord]:
    """Record terbaru lebih dulu."""
    ordered = sorted(records, key=lambda record: record.at, reverse=True)
    return ordered[:limit]


def recall_expressions(
    records: Iterable[HistoryRecord],
    limit: int = 50,
) -> list[str]:
    """Ekspresi unik terbaru lebih dulu, untuk tombol panah atas/bawah."""
    items = list(records)
    seen: set[str] = set()
    expressions: list[str] = []
    for record in recent_records(items, limit=len(items)):
        if record.expression in seen:
            continue
        seen.add(record.expression)
        expressions.append(record.expression)
        if len(expressions) >= limit:
            break
    return expressions
