"""Modal pengaturan."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static, Switch

from ..config import (
    FOCUS_RANGE,
    LONG_BREAK_RANGE,
    SESSIONS_RANGE,
    SHORT_BREAK_RANGE,
    Settings,
)


class SettingsScreen(ModalScreen[Settings | None]):
    BINDINGS = [("escape", "cancel", "Batal")]

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def compose(self) -> ComposeResult:
        with Container(id="settings-box"):
            yield Static("Pengaturan", id="settings-title")

            with Grid(id="durations"):
                yield from self._field(
                    "Durasi fokus",
                    "focus",
                    self._settings.focus_minutes,
                    FOCUS_RANGE,
                )
                yield from self._field(
                    "Istirahat pendek",
                    "short_break",
                    self._settings.short_break_minutes,
                    SHORT_BREAK_RANGE,
                )
                yield from self._field(
                    "Istirahat panjang",
                    "long_break",
                    self._settings.long_break_minutes,
                    LONG_BREAK_RANGE,
                )
                yield from self._field(
                    "Sesi per siklus",
                    "sessions",
                    self._settings.sessions_per_cycle,
                    SESSIONS_RANGE,
                )

            with Horizontal(id="toggles"):
                with Vertical(classes="toggle-field"):
                    yield Label("Auto-start istirahat", classes="field-label")
                    yield Switch(
                        value=self._settings.auto_start_breaks,
                        id="auto_breaks",
                    )
                with Vertical(classes="toggle-field"):
                    yield Label("Suara", classes="field-label")
                    yield Switch(value=self._settings.sound, id="sound")

            yield Static(
                "Fokus 5–90 · istirahat 1–30 / 5–60 · sesi 2–8",
                id="settings-hint",
            )

            with Horizontal(id="settings-buttons"):
                yield Button("Simpan", id="save", variant="primary")
                yield Button("Batal", id="cancel")

    def _field(
        self,
        label: str,
        field_id: str,
        value: int,
        limits: tuple[int, int],
    ) -> None:
        with Vertical(classes="field"):
            yield Label(
                f"{label}  ({limits[0]}–{limits[1]})",
                classes="field-label",
            )
            yield Input(
                str(value),
                id=field_id,
                type="integer",
                classes="field-input",
                compact=True,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            self._save()

    def _read_int(
        self,
        field_id: str,
        label: str,
        low: int,
        high: int,
    ) -> int | None:
        raw = self.query_one(f"#{field_id}", Input).value.strip()
        try:
            value = int(raw)
        except ValueError:
            self.query_one(f"#{field_id}", Input).focus()
            self.notify(f"{label} harus berupa angka.", severity="error")
            return None
        if not low <= value <= high:
            self.query_one(f"#{field_id}", Input).focus()
            self.notify(
                f"{label} harus antara {low} dan {high}.",
                severity="error",
            )
            return None
        return value

    def _save(self) -> None:
        focus = self._read_int("focus", "Durasi fokus", *FOCUS_RANGE)
        if focus is None:
            return
        short = self._read_int("short_break", "Istirahat pendek", *SHORT_BREAK_RANGE)
        if short is None:
            return
        long = self._read_int("long_break", "Istirahat panjang", *LONG_BREAK_RANGE)
        if long is None:
            return
        sessions = self._read_int("sessions", "Sesi per siklus", *SESSIONS_RANGE)
        if sessions is None:
            return

        self.dismiss(
            Settings(
                focus_minutes=focus,
                short_break_minutes=short,
                long_break_minutes=long,
                sessions_per_cycle=sessions,
                auto_start_breaks=self.query_one("#auto_breaks", Switch).value,
                sound=self.query_one("#sound", Switch).value,
            )
        )

    def action_cancel(self) -> None:
        self.dismiss(None)
