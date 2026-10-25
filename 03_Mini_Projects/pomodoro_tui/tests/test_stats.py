from __future__ import annotations

from datetime import date, datetime, timedelta

from fokus.stats import (
    completed_focus,
    last_seven_days,
    recent_sessions,
    streak,
    today_summary,
    week_summary,
)
from fokus.storage import SessionRecord


def record(
    day: date,
    *,
    minutes: int = 25,
    completed: bool = True,
    phase: str = "focus",
    hour: int = 10,
) -> SessionRecord:
    started = datetime.combine(day, datetime.min.time()).replace(hour=hour)
    ended = started + timedelta(minutes=minutes)
    return SessionRecord(
        started_at=started,
        ended_at=ended,
        phase=phase,
        planned_seconds=minutes * 60,
        actual_seconds=minutes * 60,
        completed=completed,
    )


TODAY = date(2026, 10, 19)


def test_completed_focus_filters_breaks_and_abandoned() -> None:
    records = [
        record(TODAY),
        record(TODAY, phase="short_break", minutes=5),
        record(TODAY, completed=False),
    ]
    assert len(completed_focus(records)) == 1


def test_today_summary() -> None:
    records = [
        record(TODAY, minutes=25),
        record(TODAY, minutes=30),
        record(TODAY - timedelta(days=1), minutes=50),
    ]
    sessions, minutes = today_summary(records, TODAY)
    assert sessions == 2
    assert minutes == 55


def test_last_seven_days_has_seven_ordered_days() -> None:
    records = [record(TODAY), record(TODAY - timedelta(days=2))]
    days = last_seven_days(records, TODAY)

    assert len(days) == 7
    assert days[-1].day == TODAY
    assert days[-1].sessions == 1
    assert days[-1].label == "Sen"
    assert days[4].sessions == 1
    assert sum(day.sessions for day in days) == 2


def test_week_summary() -> None:
    records = [record(TODAY), record(TODAY - timedelta(days=6), minutes=30)]
    sessions, minutes = week_summary(records, TODAY)
    assert sessions == 2
    assert minutes == 55


def test_streak_counts_consecutive_days() -> None:
    records = [
        record(TODAY),
        record(TODAY - timedelta(days=1)),
        record(TODAY - timedelta(days=2)),
        record(TODAY - timedelta(days=4)),
    ]
    assert streak(records, TODAY) == 3


def test_streak_uses_yesterday_when_today_empty() -> None:
    records = [
        record(TODAY - timedelta(days=1)),
        record(TODAY - timedelta(days=2)),
    ]
    assert streak(records, TODAY) == 2


def test_streak_is_zero_without_sessions() -> None:
    assert streak([], TODAY) == 0


def test_recent_sessions_sorted_descending() -> None:
    records = [
        record(TODAY, hour=9),
        record(TODAY, hour=14),
        record(TODAY, hour=11),
    ]
    recent = recent_sessions(records, limit=2)
    assert [item.ended_at.hour for item in recent] == [14, 11]
