"""Agregasi statistik dari riwayat sesi."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta

from .storage import SessionRecord

WEEKDAYS = ("Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min")


@dataclass(frozen=True, slots=True)
class DayStat:
    day: date
    label: str
    sessions: int
    minutes: int


def completed_focus(records: Iterable[SessionRecord]) -> list[SessionRecord]:
    return [
        record
        for record in records
        if record.phase == "focus" and record.completed
    ]


def _session_day(record: SessionRecord) -> date:
    return record.ended_at.date()


def today_summary(
    records: Iterable[SessionRecord],
    today: date | None = None,
) -> tuple[int, int]:
    today = today or date.today()
    items = [record for record in completed_focus(records) if _session_day(record) == today]
    minutes = sum(record.actual_seconds for record in items) // 60
    return len(items), minutes


def last_seven_days(
    records: Iterable[SessionRecord],
    today: date | None = None,
) -> list[DayStat]:
    today = today or date.today()
    by_day: dict[date, list[SessionRecord]] = {}
    for record in completed_focus(records):
        by_day.setdefault(_session_day(record), []).append(record)

    days: list[DayStat] = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        items = by_day.get(day, [])
        minutes = sum(record.actual_seconds for record in items) // 60
        days.append(
            DayStat(
                day=day,
                label=WEEKDAYS[day.weekday()],
                sessions=len(items),
                minutes=minutes,
            )
        )
    return days


def week_summary(
    records: Iterable[SessionRecord],
    today: date | None = None,
) -> tuple[int, int]:
    days = last_seven_days(records, today)
    return (
        sum(day.sessions for day in days),
        sum(day.minutes for day in days),
    )


def streak(
    records: Iterable[SessionRecord],
    today: date | None = None,
) -> int:
    """Hari berturut-turut dengan minimal satu sesi fokus selesai."""
    today = today or date.today()
    days = {_session_day(record) for record in completed_focus(records)}
    if not days:
        return 0

    cursor = today if today in days else today - timedelta(days=1)
    count = 0
    while cursor in days:
        count += 1
        cursor -= timedelta(days=1)
    return count


def recent_sessions(
    records: Iterable[SessionRecord],
    limit: int = 5,
) -> list[SessionRecord]:
    ordered = sorted(
        completed_focus(records),
        key=lambda record: record.ended_at,
        reverse=True,
    )
    return ordered[:limit]
