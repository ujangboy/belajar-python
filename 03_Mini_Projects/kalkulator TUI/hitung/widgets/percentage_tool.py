"""Kalkulator persentase berbasis mode tombol."""

from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, Static

from ..engines.percentage_engine import (
    discount_price,
    percent_change,
    percent_of,
    tax_amount,
)
from ..engines.util import EngineError
from ..format import format_number
from ..history import HistoryRecord

MODES = (
    ("X% dari Y", "of"),
    ("Perubahan %", "change"),
    ("Diskon", "discount"),
    ("Pajak", "tax"),
)


class PercentageTool(Vertical):
    """Empat mode persentase dengan input nilai dan satu tombol Hitung."""

    DEFAULT_CSS = """
    PercentageTool { height: 1fr; padding: 1 2; }
    """

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self.mode = "discount"

    @property
    def host(self):
        return self.app

    def compose(self) -> ComposeResult:
        yield Static("Persentase", id="pct-title")
        with Horizontal(id="pct-modes"):
            for label, mode in MODES:
                yield Button(label, id=f"pct-mode-{mode}", classes="pct-mode")
        yield Label("Nilai / harga")
        yield Input("100", id="pct-price")
        yield Label("Persen / nilai baru")
        yield Input("10", id="pct-percent")
        yield Button("Hitung", id="pct-run", variant="primary")
        yield Static("", id="pct-out", classes="out")

    def on_mount(self) -> None:
        self._sync_modes()

    def _sync_modes(self) -> None:
        for button in self.query(Button):
            button.set_class(button.id == f"pct-mode-{self.mode}", "-active")

    def _fmt(self, value: float) -> str:
        settings = self.host.settings
        return format_number(
            value,
            precision=settings.precision,
            thousands=settings.thousands,
            number_format=getattr(settings, "number_format", "id"),
        )

    def _num(self, widget_id: str) -> float:
        return float(
            self.query_one(f"#{widget_id}", Input).value.strip().replace(",", ".")
        )

    def calculate(self) -> None:
        out = self.query_one("#pct-out", Static)
        try:
            price = self._num("pct-price")
            percent = self._num("pct-percent")
            if self.mode == "of":
                value = percent_of(percent, price)
                text = f"{self._fmt(percent)}% dari {self._fmt(price)} = {self._fmt(value)}"
            elif self.mode == "change":
                value = percent_change(price, percent)
                text = f"Perubahan: {self._fmt(value)}%"
            elif self.mode == "discount":
                amount, value = discount_price(price, percent)
                text = (
                    f"Diskon {self._fmt(percent)}% = {self._fmt(amount)}"
                    f" · Harga akhir: {self._fmt(value)}"
                )
            else:
                amount, value = tax_amount(price, percent)
                text = (
                    f"Pajak {self._fmt(percent)}% = {self._fmt(amount)}"
                    f" · Total: {self._fmt(value)}"
                )
        except (EngineError, ValueError) as error:
            out.update(f"Error: {error}")
            return
        out.update(text)
        self._save(value)

    def _save(self, value: float) -> None:
        record = HistoryRecord(
            at=datetime.now().astimezone(),
            expression=f"percentage:{self.mode}",
            result=self._fmt(value),
            value=value,
            category="percentage",
        )
        try:
            self.host.storage.append_history(record)
        except OSError as error:
            self.app.log.error(f"Gagal menyimpan riwayat: {error}")
        self.host.records.append(record)
        self.host.refresh_dashboard_recent()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id.startswith("pct-mode-"):
            self.mode = button_id.removeprefix("pct-mode-")
            self._sync_modes()
            return
        if button_id == "pct-run":
            self.calculate()
