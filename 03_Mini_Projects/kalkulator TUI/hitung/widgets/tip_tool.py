"""Kalkulator tip dengan tombol persen cepat dan pembagian per orang."""

from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Button, Input, Label, Static

from ..engines.percentage_engine import tip_amount
from ..engines.util import EngineError
from ..format import format_number
from ..history import HistoryRecord

QUICK_PERCENTS = ("5", "10", "15", "20")


class TipTool(Vertical):
    """Tagihan, persen tip, jumlah orang, dan empat hasil."""

    DEFAULT_CSS = """
    TipTool { height: 1fr; padding: 1 2; }
    """

    @property
    def host(self):
        return self.app

    def compose(self) -> ComposeResult:
        yield Static("Tip", id="tip-title")
        yield Label("Bill amount")
        yield Input("0", id="tip-bill")
        yield Label("Tip percentage")
        with Horizontal(id="tip-quick"):
            for percent in QUICK_PERCENTS:
                yield Button(f"{percent}%", id=f"tip-{percent}", classes="tip-quick")
            yield Button("Custom", id="tip-custom", classes="tip-quick")
        yield Input("10", id="tip-percent")
        yield Label("Number of people")
        with Horizontal(id="tip-people-row"):
            yield Button("−", id="tip-people-minus")
            yield Input("1", id="tip-people")
            yield Button("+", id="tip-people-plus")
        yield Button("Hitung", id="tip-calc", variant="primary")
        with Grid(id="tip-results"):
            with Vertical(classes="tip-result"):
                yield Static("Tip Amount", classes="tip-label")
                yield Static("0", id="tip-amount", classes="tip-value")
            with Vertical(classes="tip-result"):
                yield Static("Total Bill", classes="tip-label")
                yield Static("0", id="tip-total", classes="tip-value")
            with Vertical(classes="tip-result"):
                yield Static("Per Person", classes="tip-label")
                yield Static("0", id="tip-per-person", classes="tip-value")
            with Vertical(classes="tip-result"):
                yield Static("Tip per Person", classes="tip-label")
                yield Static("0", id="tip-pp-tip", classes="tip-value")

    def on_mount(self) -> None:
        self._sync_quick()

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

    def _sync_quick(self) -> None:
        current = self.query_one("#tip-percent", Input).value.strip()
        for button in self.query("#tip-quick Button"):
            button.set_class(button.id == f"tip-{current}", "-active")

    def set_percent(self, text: str) -> None:
        self.query_one("#tip-percent", Input).value = text
        self._sync_quick()

    def _adjust_people(self, delta: int) -> None:
        field = self.query_one("#tip-people", Input)
        try:
            people = int(float(field.value.strip().replace(",", ".")))
        except ValueError:
            people = 1
        field.value = str(max(1, people + delta))

    def calculate(self) -> None:
        try:
            bill = self._num("tip-bill")
            percent = self._num("tip-percent")
            people = int(self._num("tip-people"))
            amount, total, per_person = tip_amount(bill, percent, people)
        except (EngineError, ValueError) as error:
            self.query_one("#tip-amount", Static).update(f"Error: {error}")
            for widget_id in ("tip-total", "tip-per-person", "tip-pp-tip"):
                self.query_one(f"#{widget_id}", Static).update("")
            return
        self.query_one("#tip-amount", Static).update(self._fmt(amount))
        self.query_one("#tip-total", Static).update(self._fmt(total))
        self.query_one("#tip-per-person", Static).update(self._fmt(per_person))
        self.query_one("#tip-pp-tip", Static).update(self._fmt(amount / people))
        self._save(bill, percent, people, total)

    def _save(self, bill: float, percent: float, people: int, total: float) -> None:
        record = HistoryRecord(
            at=datetime.now().astimezone(),
            expression=f"tip {self._fmt(bill)} · {self._fmt(percent)}% · {people} orang",
            result=self._fmt(total),
            value=total,
            category="tip",
        )
        try:
            self.host.storage.append_history(record)
        except OSError as error:
            self.app.log.error(f"Gagal menyimpan riwayat: {error}")
        self.host.records.append(record)
        self.host.refresh_dashboard_recent()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id.startswith("tip-") and button_id.removeprefix("tip-") in QUICK_PERCENTS:
            self.set_percent(button_id.removeprefix("tip-"))
            return
        if button_id == "tip-custom":
            self.query_one("#tip-percent", Input).focus()
            return
        if button_id == "tip-people-minus":
            self._adjust_people(-1)
            return
        if button_id == "tip-people-plus":
            self._adjust_people(1)
            return
        if button_id == "tip-calc":
            self.calculate()
