from __future__ import annotations

import json
from pathlib import Path

from fokus.config import Settings, default_data_dir
from fokus.storage import SessionRecord, Storage
from datetime import datetime


def test_settings_defaults() -> None:
    settings = Settings()
    assert settings.focus_minutes == 25
    assert settings.short_break_minutes == 5
    assert settings.long_break_minutes == 15
    assert settings.sessions_per_cycle == 4
    assert settings.auto_start_breaks is True
    assert settings.sound is True


def test_settings_from_dict_clamps_invalid_values() -> None:
    settings = Settings.from_dict(
        {
            "focus_minutes": 500,
            "short_break_minutes": 0,
            "long_break_minutes": "10",
            "sessions_per_cycle": 99,
            "auto_start_breaks": "false",
            "sound": 0,
        }
    )
    assert settings.focus_minutes == 90
    assert settings.short_break_minutes == 1
    assert settings.long_break_minutes == 10
    assert settings.sessions_per_cycle == 8
    assert settings.auto_start_breaks is False
    assert settings.sound is False


def test_settings_from_dict_uses_defaults_for_garbage() -> None:
    settings = Settings.from_dict(
        {"focus_minutes": "abc", "sound": "maybe", "sessions_per_cycle": None}
    )
    assert settings.focus_minutes == 25
    assert settings.sound is True
    assert settings.sessions_per_cycle == 4


def test_default_data_dir_respects_override(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FOKUS_DATA_DIR", str(tmp_path / "data"))
    assert default_data_dir() == tmp_path / "data"


def test_storage_round_trip(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    settings = Settings(focus_minutes=30, sound=False)
    storage.save_settings(settings)

    loaded = storage.load_settings()
    assert loaded.focus_minutes == 30
    assert loaded.sound is False


def test_storage_missing_config_returns_defaults(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    assert storage.load_settings() == Settings()


def test_storage_broken_config_is_backed_up(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    storage.data_dir.mkdir(parents=True, exist_ok=True)
    storage.config_path.write_text("{ bukan json", encoding="utf-8")

    loaded = storage.load_settings()
    assert loaded == Settings()
    assert storage.config_path.with_suffix(".json.bak").exists()


def test_session_round_trip(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    record = SessionRecord(
        started_at=datetime.fromisoformat("2026-10-19T14:00:00+07:00"),
        ended_at=datetime.fromisoformat("2026-10-19T14:25:00+07:00"),
        phase="focus",
        planned_seconds=1500,
        actual_seconds=1500,
        completed=True,
    )
    storage.append_session(record)

    loaded = storage.load_sessions()
    assert loaded == [record]


def test_load_sessions_skips_bad_lines(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    storage.data_dir.mkdir(parents=True, exist_ok=True)
    good = {
        "started_at": "2026-10-19T14:00:00+07:00",
        "ended_at": "2026-10-19T14:25:00+07:00",
        "phase": "focus",
        "planned_seconds": 1500,
        "actual_seconds": 1500,
        "completed": True,
    }
    storage.sessions_path.write_text(
        "bukan json\n"
        + json.dumps(good)
        + "\n"
        + json.dumps({**good, "phase": "invalid"})
        + "\n",
        encoding="utf-8",
    )

    loaded = storage.load_sessions()
    assert len(loaded) == 1
    assert loaded[0].phase == "focus"


def test_completed_string_false_is_parsed_as_false(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    storage.data_dir.mkdir(parents=True, exist_ok=True)
    line = json.dumps(
        {
            "started_at": "2026-10-19T14:00:00+07:00",
            "ended_at": "2026-10-19T14:25:00+07:00",
            "phase": "focus",
            "planned_seconds": 1500,
            "actual_seconds": 1500,
            "completed": "False",
        }
    )
    storage.sessions_path.write_text(line + "\n", encoding="utf-8")

    loaded = storage.load_sessions()
    assert loaded[0].completed is False
