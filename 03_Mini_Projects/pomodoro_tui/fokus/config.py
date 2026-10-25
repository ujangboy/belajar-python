"""Pengaturan aplikasi dan lokasi data."""

from __future__ import annotations

import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

APP_NAME = "Fokus"

DEFAULT_FOCUS_MINUTES = 25
DEFAULT_SHORT_BREAK_MINUTES = 5
DEFAULT_LONG_BREAK_MINUTES = 15
DEFAULT_SESSIONS_PER_CYCLE = 4

FOCUS_RANGE = (5, 90)
SHORT_BREAK_RANGE = (1, 30)
LONG_BREAK_RANGE = (5, 60)
SESSIONS_RANGE = (2, 8)


def _as_int(value: Any, default: int) -> int:
    """Konversi longgar ke int; nilai aneh kembali ke default."""
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: Any, low: int, high: int, default: int) -> int:
    number = _as_int(value, default)
    return max(low, min(high, number))


def _as_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on", "ya"}:
            return True
        if normalized in {"0", "false", "no", "off", "tidak"}:
            return False
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    return default


@dataclass(slots=True)
class Settings:
    """Semua pengaturan yang bisa diubah pengguna."""

    focus_minutes: int = DEFAULT_FOCUS_MINUTES
    short_break_minutes: int = DEFAULT_SHORT_BREAK_MINUTES
    long_break_minutes: int = DEFAULT_LONG_BREAK_MINUTES
    sessions_per_cycle: int = DEFAULT_SESSIONS_PER_CYCLE
    auto_start_breaks: bool = True
    sound: bool = True
    version: int = 1

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Settings":
        return cls(
            focus_minutes=_clamp(
                data.get("focus_minutes"),
                *FOCUS_RANGE,
                DEFAULT_FOCUS_MINUTES,
            ),
            short_break_minutes=_clamp(
                data.get("short_break_minutes"),
                *SHORT_BREAK_RANGE,
                DEFAULT_SHORT_BREAK_MINUTES,
            ),
            long_break_minutes=_clamp(
                data.get("long_break_minutes"),
                *LONG_BREAK_RANGE,
                DEFAULT_LONG_BREAK_MINUTES,
            ),
            sessions_per_cycle=_clamp(
                data.get("sessions_per_cycle"),
                *SESSIONS_RANGE,
                DEFAULT_SESSIONS_PER_CYCLE,
            ),
            auto_start_breaks=_as_bool(data.get("auto_start_breaks"), True),
            sound=_as_bool(data.get("sound"), True),
            version=1,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_data_dir() -> Path:
    """Lokasi data yang mengikuti konvensi tiap OS."""
    override = os.environ.get("FOKUS_DATA_DIR")
    if override:
        return Path(override).expanduser()

    if sys.platform == "win32":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / APP_NAME
        return Path.home() / "AppData" / "Roaming" / APP_NAME

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME

    base = os.environ.get("XDG_DATA_HOME")
    if base:
        return Path(base) / "fokus"
    return Path.home() / ".local" / "share" / "fokus"
