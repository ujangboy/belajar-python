"""Tab kategori konverter — tombol horizontal."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button


class ConverterTabs(Horizontal):
    """Satu tombol per kategori; tombol aktif ditandai ``-active``."""

    class CategoryChanged(Message):
        def __init__(self, category_id: str) -> None:
            super().__init__()
            self.category_id = category_id

    def __init__(
        self,
        categories: list[tuple[str, str]] | tuple[tuple[str, str], ...] = (),
        *,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self._categories = list(categories)
        self._value = self._categories[0][1] if self._categories else ""

    def set_categories(self, categories: list[tuple[str, str]]) -> None:
        """Isi tab dengan pasangan (label, category_id). Panggil sebelum mount."""
        self._categories = list(categories)
        self._value = self._categories[0][1] if self._categories else ""

    @property
    def value(self) -> str:
        return self._value

    def compose(self) -> ComposeResult:
        for label, category_id in self._categories:
            yield Button(label, id=f"tab-{category_id}", classes="tab")

    def on_mount(self) -> None:
        self._sync_active()

    def _sync_active(self) -> None:
        for button in self.query(Button):
            button.set_class(button.id == f"tab-{self._value}", "-active")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if not button_id.startswith("tab-"):
            return
        event.stop()
        self._value = button_id.removeprefix("tab-")
        self._sync_active()
        self.post_message(self.CategoryChanged(self._value))
