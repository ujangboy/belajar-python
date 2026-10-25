"""Penyimpanan lokal: config.json dan sessions.jsonl."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import Settings, default_data_dir

VALID_PHASES = {"focus", "short_break", "long_break"}


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "ya"}
    return bool(value)


@dataclass(frozen=True, slots=True)
class SessionRecord:
    started_at: datetime
    ended_at: datetime
    phase: str
    planned_seconds: int
    actual_seconds: int
    completed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat(),
            "phase": self.phase,
            "planned_seconds": self.planned_seconds,
            "actual_seconds": self.actual_seconds,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionRecord | None":
        try:
            started_at = datetime.fromisoformat(str(data["started_at"]))
            ended_at = datetime.fromisoformat(str(data["ended_at"]))
            phase = str(data["phase"])
            planned_seconds = int(data["planned_seconds"])
            actual_seconds = int(data["actual_seconds"])
        except (KeyError, TypeError, ValueError):
            return None

        if phase not in VALID_PHASES:
            return None
        if planned_seconds <= 0 or actual_seconds < 0:
            return None

        return cls(
            started_at=started_at,
            ended_at=ended_at,
            phase=phase,
            planned_seconds=planned_seconds,
            actual_seconds=actual_seconds,
            completed=_as_bool(data.get("completed", False)),
        )


class Storage:
    """Akses file data dengan tulis atomik dan baca yang toleran."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir is not None else default_data_dir()
        self.config_path = self.data_dir / "config.json"
        self.sessions_path = self.data_dir / "sessions.jsonl"

    # ------------------------------------------------------------------ config
    def load_settings(self) -> Settings:
        if not self.config_path.exists():
            return Settings()

        try:
            raw = json.loads(self.config_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("config harus berupa object JSON")
            return Settings.from_dict(raw)
        except (OSError, ValueError, json.JSONDecodeError):
            self._backup_broken_config()
            return Settings()

    def save_settings(self, settings: Settings) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        temp_path = self.config_path.with_suffix(".json.tmp")
        payload = json.dumps(settings.to_dict(), indent=2, ensure_ascii=False) + "\n"
        temp_path.write_text(payload, encoding="utf-8")
        os.replace(temp_path, self.config_path)

    def _backup_broken_config(self) -> None:
        if not self.config_path.exists():
            return
        try:
            backup = self.config_path.with_suffix(".json.bak")
            if backup.exists():
                backup.unlink()
            shutil.copy2(self.config_path, backup)
        except OSError:
            pass

    # ---------------------------------------------------------------- sessions
    def append_session(self, record: SessionRecord) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record.to_dict(), ensure_ascii=False) + "\n"
        with self.sessions_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())

    def load_sessions(self) -> list[SessionRecord]:
        if not self.sessions_path.exists():
            return []

        records: list[SessionRecord] = []
        try:
            with self.sessions_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(raw, dict):
                        record = SessionRecord.from_dict(raw)
                        if record is not None:
                            records.append(record)
        except OSError:
            return []
        return records
