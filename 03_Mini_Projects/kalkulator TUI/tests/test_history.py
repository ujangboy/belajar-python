from __future__ import annotations

from datetime import date, datetime, timedelta

from hitung.history import (
    WEEKDAYS,
    HistoryRecord,
    last_seven_days,
    recall_expressions,
    recent_records,
    today_count,
    total_count,
    week_total,
)

TODAY = date(2026, 10, 25)


def make(days_ago: int = 0, hour: int = 9, expression: str = "1+1") -> HistoryRecord:
    at = datetime(2026, 10, 25, hour, 0).astimezone() - timedelta(days=days_ago)
    return HistoryRecord(at=at, expression=expression, result="2", value=2.0)


def test_today_count() -> None:
    records = [make(), make(), make(days_ago=1)]
    assert today_count(records, TODAY) == 2
    assert total_count(records) == 3


def test_last_seven_days() -> None:
    records = [make(), make(), make(days_ago=1)]
    days = last_seven_days(records, TODAY)

    assert len(days) == 7
    assert days[-1].day == TODAY
    assert days[-1].label == WEEKDAYS[TODAY.weekday()]
    assert days[-1].count == 2
    assert days[-2].count == 1
    assert week_total(records, TODAY) == 3


def test_week_total_ignores_older_records() -> None:
    records = [make(days_ago=30)]
    assert week_total(records, TODAY) == 0


def test_recent_records_newest_first() -> None:
    early = make(hour=9, expression="1+1")
    middle = make(hour=10, expression="2+2")
    late = make(hour=11, expression="3+3")

    assert recent_records([early, middle, late], 2) == [late, middle]


def test_recall_expressions_unique_newest_first() -> None:
    records = [
        make(hour=9, expression="1+1"),
        make(hour=10, expression="2+2"),
        make(hour=11, expression="1+1"),
    ]
    assert recall_expressions(records) == ["1+1", "2+2"]


def test_recall_expressions_limit() -> None:
    records = [make(hour=hour, expression=f"{hour}+1") for hour in (9, 10, 11)]
    assert recall_expressions(records, limit=2) == ["11+1", "10+1"]


def test_record_round_trip() -> None:
    record = make()
    restored = HistoryRecord.from_dict(record.to_dict())
    assert restored == record
    assert restored is not None
    assert restored.category == "standard"


def test_record_v1_without_category_is_tolerated() -> None:
    at = make().at.isoformat()
    restored = HistoryRecord.from_dict(
        {"at": at, "expression": "1+1", "result": "2", "value": 2}
    )
    assert restored is not None
    assert restored.category == "standard"
    assert restored.input_text is None
    assert restored.output_text is None


def test_record_from_dict_is_tolerant() -> None:
    assert HistoryRecord.from_dict({}) is None
    assert HistoryRecord.from_dict({"at": "bukan tanggal"}) is None
    assert HistoryRecord.from_dict(
        {"at": make().at.isoformat(), "expression": "", "result": "2", "value": 2}
    ) is None
    assert HistoryRecord.from_dict(
        {"at": make().at.isoformat(), "expression": "1+1", "result": "2", "value": "x"}
    ) is None
    assert HistoryRecord.from_dict(
        {"at": make().at.isoformat(), "expression": "1+1", "result": "2", "value": float("nan")}
    ) is None
