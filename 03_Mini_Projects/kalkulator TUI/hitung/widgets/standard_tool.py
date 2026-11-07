"""Layar kalkulator standar berbasis tombol."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical

from ..engine import CalcError, evaluate
from ..format import format_number
from ..history import HistoryRecord, recall_expressions
from ..widgets.display import CalculatorDisplay
from ..widgets.keypad import STANDARD_KEYS, KeyPressed, ScientificKeypad

_TRAILING_NUMBER = re.compile(r"(\d+(?:[.,]\d+)?)$")


def _last_additive_index(text: str) -> int | None:
    """Indeks operator + atau - terakhir pada level kurung teratas."""
    depth = 0
    last: int | None = None
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char in "+-" and depth == 0:
            previous = text[:index].rstrip()
            if previous and previous[-1] not in "+-*/^(":
                last = index
    return last


def _plain_number(value: float) -> str:
    """Angka tanpa notasi ilmiah supaya bisa dibaca ulang oleh engine."""
    return format(Decimal(repr(value)).normalize(), "f")


def preprocess_percent(expression: str, *, angle: str, ans: float) -> str:
    """Persentase kontekstual: ``200 + 10%`` menjadi ``200 + 20``.

    ``10%`` dihitung dari nilai di sisi kiri operator +/− terakhir. Tanpa
    operator aditif, ekspresi dibiarkan agar engine memakai ``/100``.
    """
    result = expression
    for _ in range(8):
        marker = result.find("%")
        if marker < 0:
            return result
        match = _TRAILING_NUMBER.search(result[:marker])
        if match is None:
            return result
        before = result[: match.start()]
        op_index = _last_additive_index(before)
        if op_index is None or before[op_index + 1 :].strip():
            return result
        left = before[:op_index].strip()
        if not left:
            return result
        try:
            base = evaluate(left, angle=angle, ans=ans)
        except CalcError:
            return result
        amount = base * float(match.group(1).replace(",", ".")) / 100.0
        result = (
            f"{left} {before[op_index]} {_plain_number(amount)}"
            f"{result[marker + 1:]}"
        )
    return result


class StandardTool(Vertical):
    """Display baca-saja + keypad tombol untuk hitungan harian."""

    DEFAULT_CSS = """
    StandardTool { height: 1fr; layout: vertical; }
    """

    BINDINGS = [
        Binding("escape", "clear_entry", "Bersihkan", key_display="Esc", show=False),
        Binding("up", "recall_previous", show=False),
        Binding("down", "recall_next", show=False),
        Binding("ctrl+y", "copy_result", show=False),
    ]

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self.expression = ""
        self.last_result: float | None = None
        self._recall: list[str] = []
        self._recall_index: int | None = None

    @property
    def host(self):
        return self.app

    def compose(self) -> ComposeResult:
        yield CalculatorDisplay(id="calc-display")
        yield ScientificKeypad(STANDARD_KEYS, columns=4, id="standard-keypad")

    def on_mount(self) -> None:
        self.rebuild_recall()
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
        return "Tekan tombol angka, lalu = untuk menghitung"

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
                preprocess_percent(
                    self.expression,
                    angle=self.host.settings.angle,
                    ans=self.host.ans,
                ),
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
        self._recall_index = None
        self.refresh_display()

    def _show(self, value: str) -> None:
        self.expression = value
        self.refresh_display()

    def _append(self, text: str) -> None:
        self.expression += text
        self._recall_index = None
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
                preprocess_percent(
                    expression,
                    angle=self.host.settings.angle,
                    ans=self.host.ans,
                ),
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
            category="standard",
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
        self.rebuild_recall()
        display.set_expression("")
        display.set_result(formatted)
        display.set_status("Tersimpan ke riwayat")
        if self.host.settings.sound:
            self.app.bell()

    # ---- aksi ----
    def action_clear_entry(self) -> None:
        self.set_expression("")
        self._display().set_status(self._default_hint())

    def action_copy_result(self) -> None:
        text: str | None = None
        if self.expression.strip():
            try:
                value = evaluate(
                    preprocess_percent(
                        self.expression,
                        angle=self.host.settings.angle,
                        ans=self.host.ans,
                    ),
                    angle=self.host.settings.angle,
                    ans=self.host.ans,
                )
            except CalcError:
                text = None
            else:
                text = self._format(value)
        if text is None:
            text = self.host.last_result
        if text is None:
            self.app.notify("Belum ada hasil untuk disalin.", timeout=2)
            return
        self.app.copy_to_clipboard(text)
        self.app.notify(f"Disalin: {text}", timeout=2)

    def rebuild_recall(self) -> None:
        self._recall = recall_expressions(self.host.records)
        self._recall_index = None

    def action_recall_previous(self) -> None:
        if not self._recall:
            self.app.notify("Belum ada riwayat untuk dipanggil.", timeout=2)
            return
        if self._recall_index is None:
            index = 0
        elif self._recall_index < len(self._recall) - 1:
            index = self._recall_index + 1
        else:
            return
        self._recall_index = index
        self._show(self._recall[index])

    def action_recall_next(self) -> None:
        if self._recall_index is None:
            return
        if self._recall_index == 0:
            self._recall_index = None
            self._show("")
        else:
            self._recall_index -= 1
            self._show(self._recall[self._recall_index])
