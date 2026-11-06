from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from hitung.config import Settings
from hitung.history import HistoryRecord
from hitung.storage import Storage


def make(hour: int = 9) -> HistoryRecord:
    return HistoryRecord(
        at=datetime(2026, 10, 25, hour, 0).astimezone(),
        expression=f"{hour}+1",
        result=str(hour + 1),
        value=float(hour + 1),
    )


def test_missing_files_return_defaults(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    assert storage.load_settings() == Settings()
    assert storage.load_history() == []


def test_settings_round_trip(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    settings = Settings(precision=2, thousands=False, angle="rad", sound=False)
    storage.save_settings(settings)

    assert storage.load_settings() == settings
    assert not (tmp_path / "config.json.tmp").exists()


def test_corrupt_config_is_backed_up(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    (tmp_path / "config.json").write_text("bukan json", encoding="utf-8")

    assert storage.load_settings() == Settings()
    assert (tmp_path / "config.json.bak").exists()


def test_config_must_be_object(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    (tmp_path / "config.json").write_text("[1, 2, 3]", encoding="utf-8")

    assert storage.load_settings() == Settings()
    assert (tmp_path / "config.json.bak").exists()


def test_history_append_and_load(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    first = make(9)
    second = make(10)

    storage.append_history(first)
    storage.append_history(second)

    assert storage.load_history() == [first, second]
    assert (tmp_path / "history.jsonl").exists()


def test_history_skips_broken_lines(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    first = make(9)
    second = make(10)
    content = "\n".join(
        [
            json.dumps(first.to_dict()),
            "bukan json",
            json.dumps({"at": "bukan tanggal"}),
            "",
            json.dumps(second.to_dict()),
        ]
    )
    (tmp_path / "history.jsonl").write_text(content + "\n", encoding="utf-8")

    assert storage.load_history() == [first, second]


def test_clear_history(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    storage.append_history(make())
    storage.clear_history()

    assert not (tmp_path / "history.jsonl").exists()
    assert storage.load_history() == []


def test_clear_history_is_idempotent(tmp_path: Path) -> None:
    Storage(tmp_path).clear_history()
