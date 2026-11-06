"""Pengaturan aplikasi dan lokasi data."""

from __future__ import annotations

import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

APP_NAME = "Hitung"

DEFAULT_PRECISION = 6
PRECISION_RANGE = (0, 10)

DEFAULT_ANGLE = "deg"
ANGLE_CHOICES = ("deg", "rad")
ANGLE_LABELS = {"deg": "derajat (deg)", "rad": "radian (rad)"}

DEFAULT_THEME = "dark"
THEME_CHOICES = ("dark", "light")

DEFAULT_ACCENT = "blue"
ACCENT_CHOICES = ("mint", "blue", "amber", "rose")

DEFAULT_NUMBER_FORMAT = "id"
NUMBER_FORMAT_CHOICES = ("id", "plain")

DEFAULT_HISTORY_LIMIT = 0  # 0 = tanpa batas (kompatibel dengan perilaku lama)


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


def _as_angle(value: Any, default: str) -> str:
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"deg", "derajat", "degree", "degrees"}:
            return "deg"
        if normalized in {"rad", "radian", "radians"}:
            return "rad"
    return default


def _as_choice(value: Any, choices: tuple[str, ...], default: str) -> str:
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in choices:
            return normalized
    return default


def _as_favorites(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    seen: set[str] = set()
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        tool_id = item.strip()
        if not tool_id or tool_id in seen:
            continue
        seen.add(tool_id)
        items.append(tool_id)
    return items


@dataclass(slots=True)
class Settings:
    """Semua pengaturan yang bisa diubah pengguna."""

    precision: int = DEFAULT_PRECISION
    thousands: bool = True
    angle: str = DEFAULT_ANGLE
    sound: bool = True
    theme: str = DEFAULT_THEME
    accent: str = DEFAULT_ACCENT
    number_format: str = DEFAULT_NUMBER_FORMAT
    history_limit: int = DEFAULT_HISTORY_LIMIT
    favorites: list[str] = field(default_factory=list)
    version: int = 2

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Settings":
        return cls(
            precision=_clamp(
                data.get("precision"),
                *PRECISION_RANGE,
                DEFAULT_PRECISION,
            ),
            thousands=_as_bool(data.get("thousands"), True),
            angle=_as_angle(data.get("angle"), DEFAULT_ANGLE),
            sound=_as_bool(data.get("sound"), True),
            theme=_as_choice(data.get("theme"), THEME_CHOICES, DEFAULT_THEME),
            accent=_as_choice(data.get("accent"), ACCENT_CHOICES, DEFAULT_ACCENT),
            number_format=_as_choice(
                data.get("number_format"),
                NUMBER_FORMAT_CHOICES,
                DEFAULT_NUMBER_FORMAT,
            ),
            history_limit=max(0, _as_int(data.get("history_limit"), DEFAULT_HISTORY_LIMIT)),
            favorites=_as_favorites(data.get("favorites")),
            version=2,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_data_dir() -> Path:
    """Lokasi data yang mengikuti konvensi tiap OS."""
    override = os.environ.get("HITUNG_DATA_DIR")
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
        return Path(base) / "hitung"
    return Path.home() / ".local" / "share" / "hitung"
