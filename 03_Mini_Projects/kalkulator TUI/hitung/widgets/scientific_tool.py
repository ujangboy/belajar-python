"""Layar kalkulator ilmiah berbasis tombol."""

from __future__ import annotations

import re
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Vertical

from ..engine import CalcError, evaluate
from ..format import format_number
from ..history import HistoryRecord
from ..widgets.display import CalculatorDisplay
from ..widgets.keypad import SCIENTIFIC_KEYS, KeyPressed, ScientificKeypad

_TRAILING_NUMBER = re.compile(r"(\d+(?:[.,]\d+)?)$")


class ScientificTool(Vertical):
    """Display baca-saja + keypad 7 kolom, termasuk DEG/RAD dan ANS."""

    DEFAULT_CSS = """
    ScientificTool { height: 1fr; layout: vertical; }
    """

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self.expression = ""
        self.last_result: float | None = None

    @property
    def host(self):
        return self.app

    def compose(self) -> ComposeResult:
        yield CalculatorDisplay(prefix="sci-", id="sci-display")
        yield ScientificKeypad(
            SCIENTIFIC_KEYS,
            columns=7,
            prefix="sci-",
            id="sci-keypad",
        )

    def on_mount(self) -> None:
        self.refresh_display()

    def _display(self) -> CalculatorDisplay:
        return self.query_one(CalculatorDisplay)

    def _format(self, value: float) -> str:
        settings = self.host.settings
        return format_number(
            value,
            precision=settings.precision,
            thousands=settings.thousands,
            number_format=getattr(settings, "number_format", "id"),
        )

    def _default_hint(self) -> str:
        return "Tekan tombol fungsi atau angka, lalu = untuk menghitung"

    # ---- state tampilan ----
    def refresh_display(self) -> None:
        display = self._display()
        display.set_expression(self.expression)
        display.set_angle(self.host.settings.angle)
        if not self.expression.strip():
            display.set_result(self.host.last_result or "0")
            display.set_status(self._default_hint())
            return
        try:
            value = evaluate(
                self.expression,
                angle=self.host.settings.angle,
                ans=self.host.ans,
            )
        except CalcError:
            display.set_result(self.host.last_result or "0")
            display.set_status(self._default_hint())
            return
        display.set_result(self._format(value), preview=True)
        display.set_status("Tekan = untuk menghitung")

    def set_expression(self, value: str) -> None:
        self.expression = value
        self.refresh_display()

    def _append(self, text: str) -> None:
        self.expression += text
        self.refresh_display()

    def _toggle_sign(self) -> None:
        match = _TRAILING_NUMBER.search(self.expression)
        if match is None:
            self._append("-")
            return
        start = match.start()
        if start > 0 and self.expression[start - 1] == "-":
            self.set_expression(self.expression[: start - 1] + self.expression[start:])
        else:
            self.set_expression(self.expression[:start] + "-" + self.expression[start:])

    def toggle_angle(self) -> None:
        mode = "rad" if self.host.settings.angle == "deg" else "deg"
        self.host.settings.angle = mode
        try:
            self.host.storage.save_settings(self.host.settings)
        except OSError as error:
            self.app.log.error(f"Gagal menyimpan pengaturan: {error}")
        self.refresh_display()

    def _swap(self) -> None:
        answer = self.host.ans
        current = self.expression.strip()
        if current:
            try:
                self.host.ans = evaluate(
                    current,
                    angle=self.host.settings.angle,
                    ans=answer,
                )
            except CalcError:
                pass
        self.set_expression(self._format(answer))

    def _reciprocal(self) -> None:
        if self.expression.strip():
            self.set_expression(f"1/({self.expression})")
        else:
            self._append("1/")

    # ---- keypad ----
    def on_key_pressed(self, event: KeyPressed) -> None:
        event.stop()
        key = event.key
        if key == "key-equals":
            self.calculate()
        elif key == "key-clear":
            self.action_clear_entry()
        elif key == "key-backspace":
            self.set_expression(self.expression[:-1])
        elif key == "key-angle":
            self.toggle_angle()
        elif key == "key-swap":
            self._swap()
        elif key == "key-recip":
            self._reciprocal()
        elif key == "key-sign":
            self._toggle_sign()
        else:
            insert = self.query_one(ScientificKeypad).insert_texts.get(key)
            if insert:
                self._append(insert)

    def calculate(self) -> None:
        display = self._display()
        expression = self.expression.strip()
        if not expression:
            display.set_status("Ekspresi masih kosong — tekan angka dulu", error=True)
            return
        try:
            value = evaluate(
                expression,
                angle=self.host.settings.angle,
                ans=self.host.ans,
            )
        except CalcError as error:
            display.set_result(self.host.last_result or "0")
            display.set_status(str(error), error=True)
            if self.host.settings.sound:
                self.app.bell()
            return
        formatted = self._format(value)
        record = HistoryRecord(
            at=datetime.now().astimezone(),
            expression=expression,
            result=formatted,
            value=value,
            category="scientific",
        )
        try:
            self.host.storage.append_history(record)
        except OSError as error:
            self.app.log.error(f"Gagal menyimpan riwayat: {error}")
            self.app.notify(
                "Hasil dihitung, tetapi gagal disimpan ke disk.",
                title="Penyimpanan gagal",
                severity="error",
                timeout=8,
            )
        self.host.records.append(record)
        self.host.ans = value
        self.host.last_expression = expression
        self.host.last_result = formatted
        self.last_result = value
        self.expression = ""
        display.set_expression("")
        display.set_result(formatted)
        display.set_status("Tersimpan ke riwayat")
        if self.host.settings.sound:
            self.app.bell()

    # ---- aksi ----
    def action_clear_entry(self) -> None:
        self.set_expression("")
        self._display().set_status(self._default_hint())

    def action_clear_or_back(self) -> None:
        if self.expression:
            self.action_clear_entry()
        else:
            self.host.open_tool("dashboard")
