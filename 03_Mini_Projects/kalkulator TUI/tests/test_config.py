from __future__ import annotations

from pathlib import Path

from hitung.config import (
    DEFAULT_ANGLE,
    DEFAULT_PRECISION,
    PRECISION_RANGE,
    Settings,
    default_data_dir,
)


def test_defaults() -> None:
    settings = Settings()
    assert settings.precision == DEFAULT_PRECISION
    assert settings.thousands is True
    assert settings.angle == DEFAULT_ANGLE
    assert settings.sound is True
    assert settings.theme == "dark"
    assert settings.accent == "blue"
    assert settings.number_format == "id"
    assert settings.history_limit == 0
    assert settings.favorites == []
    assert settings.version == 2


def test_precision_is_clamped() -> None:
    assert Settings.from_dict({"precision": -3}).precision == PRECISION_RANGE[0]
    assert Settings.from_dict({"precision": 99}).precision == PRECISION_RANGE[1]
    assert Settings.from_dict({"precision": "7"}).precision == 7
    assert Settings.from_dict({"precision": "abc"}).precision == DEFAULT_PRECISION
    assert Settings.from_dict({"precision": True}).precision == DEFAULT_PRECISION


def test_angle_is_tolerant() -> None:
    assert Settings.from_dict({"angle": "RAD"}).angle == "rad"
    assert Settings.from_dict({"angle": " radian "}).angle == "rad"
    assert Settings.from_dict({"angle": "derajat"}).angle == "deg"
    assert Settings.from_dict({"angle": "gon"}).angle == DEFAULT_ANGLE
    assert Settings.from_dict({"angle": 1}).angle == DEFAULT_ANGLE


def test_booleans_are_tolerant() -> None:
    assert Settings.from_dict({"thousands": "off"}).thousands is False
    assert Settings.from_dict({"thousands": "ya"}).thousands is True
    assert Settings.from_dict({"sound": 0}).sound is False
    assert Settings.from_dict({"sound": True}).sound is True


def test_round_trip() -> None:
    settings = Settings(
        precision=3,
        thousands=False,
        angle="rad",
        sound=False,
        theme="light",
        accent="blue",
        number_format="plain",
        history_limit=500,
        favorites=["standard", "converter:temperature"],
    )
    assert Settings.from_dict(settings.to_dict()) == settings


def test_data_dir_env_override(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HITUNG_DATA_DIR", str(tmp_path))
    assert default_data_dir() == tmp_path


def test_v1_config_loads_with_defaults() -> None:
    settings = Settings.from_dict(
        {"precision": 4, "thousands": False, "angle": "rad", "sound": True, "version": 1}
    )
    assert settings.precision == 4
    assert settings.thousands is False
    assert settings.angle == "rad"
    assert settings.theme == "dark"
    assert settings.favorites == []


def test_unknown_fields_and_bad_favorites_are_ignored() -> None:
    settings = Settings.from_dict(
        {
            "favorites": ["standard", 123, "standard", "", " scientific "],
            "unknown_future_field": {"x": 1},
            "theme": "neon",
        }
    )
    assert settings.favorites == ["standard", "scientific"]
    assert settings.theme == "dark"
