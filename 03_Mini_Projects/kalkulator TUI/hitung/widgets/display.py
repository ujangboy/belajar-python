"""Display kalkulator — hanya baca, dipakai tombol keypad."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class CalculatorDisplay(Vertical):
    """Empat baris: mode sudut, ekspresi, hasil, dan status."""

    def __init__(
        self,
        *,
        prefix: str = "",
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self._prefix = prefix

    def _sel(self, name: str) -> str:
        return f"#{self._prefix}{name}"

    def compose(self) -> ComposeResult:
        yield Static("", id=f"{self._prefix}calc-angle", classes="calc-angle")
        yield Static("", id=f"{self._prefix}calc-expression", classes="calc-expression")
        yield Static("0", id=f"{self._prefix}calc-result", classes="calc-result")
        yield Static("", id=f"{self._prefix}calc-status", classes="calc-status")

    def set_expression(self, text: str) -> None:
        self.query_one(self._sel("calc-expression"), Static).update(text)

    def set_result(self, text: str, preview: bool = False) -> None:
        result = self.query_one(self._sel("calc-result"), Static)
        result.update(text)
        result.set_class(preview, "-preview")

    def set_status(self, text: str, error: bool = False) -> None:
        status = self.query_one(self._sel("calc-status"), Static)
        status.update(text)
        status.set_class(error, "-error")

    def set_angle(self, mode: str) -> None:
        self.query_one(self._sel("calc-angle"), Static).update(mode.upper())

    @property
    def result_text(self) -> str:
        return str(self.query_one(self._sel("calc-result"), Static).content)
