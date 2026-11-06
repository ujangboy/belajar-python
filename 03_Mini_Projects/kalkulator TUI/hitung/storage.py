"""Penyimpanan lokal: config.json dan history.jsonl."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from .config import Settings, default_data_dir
from .history import HistoryRecord


class Storage:
    """Akses file data dengan tulis atomik dan baca yang toleran."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir is not None else default_data_dir()
        self.config_path = self.data_dir / "config.json"
        self.history_path = self.data_dir / "history.jsonl"

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

    # ----------------------------------------------------------------- history
    def append_history(self, record: HistoryRecord) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record.to_dict(), ensure_ascii=False) + "\n"
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())

    def load_history(self) -> list[HistoryRecord]:
        if not self.history_path.exists():
            return []

        records: list[HistoryRecord] = []
        try:
            with self.history_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(raw, dict):
                        record = HistoryRecord.from_dict(raw)
                        if record is not None:
                            records.append(record)
        except OSError:
            return []
        return records

    def save_history(self, records: list[HistoryRecord]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        temp_path = self.history_path.with_suffix(".jsonl.tmp")
        payload = "".join(json.dumps(r.to_dict(), ensure_ascii=False) + "\n" for r in records)
        temp_path.write_text(payload, encoding="utf-8")
        os.replace(temp_path, self.history_path)

    def clear_history(self) -> None:
        """Hapus seluruh riwayat. Tidak error kalau file belum ada."""
        try:
            self.history_path.unlink()
        except FileNotFoundError:
            pass
