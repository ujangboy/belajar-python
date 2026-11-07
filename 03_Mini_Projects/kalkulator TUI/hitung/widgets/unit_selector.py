"""Panel satuan konverter: dropdown + nilai besar."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Select, Static


class UnitSelector(Vertical):
    """Satu sisi konverter (DARI/KE); bisa difokuskan untuk keypad angka."""

    can_focus = True

    class UnitChanged(Message):
        def __init__(self, unit_id: str, selector_id: str = "") -> None:
            super().__init__()
            self.unit_id = unit_id
            self.selector_id = selector_id

    def __init__(
        self,
        title: str,
        *,
        select_id: str,
        value_id: str,
        options: list[tuple[str, str]] | tuple[tuple[str, str], ...] = (),
        default_index: int = 0,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self._title = title
        self._select_id = select_id
        self._value_id = value_id
        self._options = list(options)
        self._default_index = default_index

    def set_options(self, options: list[tuple[str, str]]) -> None:
        """Ganti daftar unit; unit pertama dipilih."""
        self._options = list(options)
        try:
            select = self.query_one(Select)
        except Exception:
            return
        select.set_options(self._options)
        if self._options:
            select.value = self._options[0][1]

    @property
    def value(self) -> str:
        return str(self.query_one(Select).value)

    def select_unit(self, unit_id: str) -> None:
        self.query_one(Select).value = unit_id

    def show_value(self, text: str) -> None:
        self.query_one(f"#{self._value_id}", Static).update(text)

    def compose(self) -> ComposeResult:
        selected = None
        if self._options:
            index = min(self._default_index, len(self._options) - 1)
            selected = self._options[index][1]
        yield Static(self._title, classes="unit-title")
        yield Select(
            self._options,
            value=selected,
            allow_blank=not self._options,
            id=self._select_id,
        )
        yield Static("0", id=self._value_id, classes="unit-value")

    def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()
        if event.select.value is not None:
            self.post_message(self.UnitChanged(str(event.select.value), self.id or ""))
