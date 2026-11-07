"""Modal pengaturan."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static, Switch

from ..config import (
    ACCENT_CHOICES,
    ANGLE_CHOICES,
    NUMBER_FORMAT_CHOICES,
    PRECISION_RANGE,
    THEME_CHOICES,
    Settings,
)


class SettingsScreen(ModalScreen[Settings | None]):
    BINDINGS = [
        ("escape", "cancel", "Batal"),
        ("f3", "cancel", "Tutup"),
    ]

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def compose(self) -> ComposeResult:
        low, high = PRECISION_RANGE
        with VerticalScroll(id="settings-box"):
            yield Static("Pengaturan", id="settings-title")

            with Grid(id="settings-fields"):
                with Vertical(classes="field"):
                    yield Label(f"Presisi ({low}–{high} desimal)", classes="field-label")
                    yield Input(str(self._settings.precision), id="precision", type="integer", classes="field-input", compact=True)
                with Vertical(classes="field"):
                    yield Label("Mode sudut", classes="field-label")
                    yield Select([("Derajat (deg)", "deg"), ("Radian (rad)", "rad")], value=self._settings.angle, allow_blank=False, id="angle", classes="field-select")
                with Vertical(classes="field"):
                    yield Label("Tema", classes="field-label")
                    yield Select([("Gelap", "dark"), ("Terang", "light")], value=self._settings.theme, allow_blank=False, id="theme", classes="field-select")
                with Vertical(classes="field"):
                    yield Label("Aksen", classes="field-label")
                    yield Select([("Mint", "mint"), ("Biru", "blue"), ("Amber", "amber"), ("Rose", "rose")], value=self._settings.accent, allow_blank=False, id="accent", classes="field-select")
                with Vertical(classes="field"):
                    yield Label("Format angka", classes="field-label")
                    yield Select([("Indonesia (1.234,56)", "id"), ("Plain (1234.56)", "plain")], value=self._settings.number_format, allow_blank=False, id="number_format", classes="field-select")

            with Horizontal(id="toggles"):
                with Vertical(classes="toggle-field"):
                    yield Label("Pemisah ribuan", classes="field-label")
                    yield Switch(value=self._settings.thousands, id="thousands")
                with Vertical(classes="toggle-field"):
                    yield Label("Suara (bell)", classes="field-label")
                    yield Switch(value=self._settings.sound, id="sound")

            yield Static(
                "Tema, aksen, dan format angka langsung dipakai. "
                "Tekan Ctrl+D di alat mana pun untuk menambah/menghapus favorit.",
                id="settings-hint",
            )

            with Horizontal(id="settings-buttons"):
                yield Button("Simpan", id="save", variant="primary")
                yield Button("Batal", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            self._save()

    def _save(self) -> None:
        raw = self.query_one("#precision", Input).value.strip()
        try:
            precision = int(raw)
        except ValueError:
            self.query_one("#precision", Input).focus()
            self.notify("Presisi harus berupa angka.", severity="error")
            return

        low, high = PRECISION_RANGE
        if not low <= precision <= high:
            self.query_one("#precision", Input).focus()
            self.notify(
                f"Presisi harus antara {low} dan {high}.",
                severity="error",
            )
            return

        angle = str(self.query_one("#angle", Select).value or self._settings.angle)
        if angle not in ANGLE_CHOICES:
            angle = self._settings.angle
        theme = str(self.query_one("#theme", Select).value or self._settings.theme)
        if theme not in THEME_CHOICES:
            theme = self._settings.theme
        accent = str(self.query_one("#accent", Select).value or self._settings.accent)
        if accent not in ACCENT_CHOICES:
            accent = self._settings.accent
        number_format = str(self.query_one("#number_format", Select).value or self._settings.number_format)
        if number_format not in NUMBER_FORMAT_CHOICES:
            number_format = self._settings.number_format

        self.dismiss(
            Settings(
                precision=precision,
                thousands=self.query_one("#thousands", Switch).value,
                angle=angle,
                sound=self.query_one("#sound", Switch).value,
                theme=theme,
                accent=accent,
                number_format=number_format,
                history_limit=self._settings.history_limit,
                favorites=list(self._settings.favorites),
            )
        )

    def action_cancel(self) -> None:
        self.dismiss(None)
