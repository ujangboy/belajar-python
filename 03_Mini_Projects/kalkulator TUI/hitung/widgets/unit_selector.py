"""Panel satuan konverter: pemilih unit inline + nilai besar.

Menggunakan OptionList yang expand/collapse di dalam panel (bukan overlay
menutup keypad), sesuai kebutuhan PRD v3.0.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Button, OptionList, Static
from textual.widgets.option_list import Option


class UnitSelector(Vertical):
    """Satu sisi konverter (DARI/KE); bisa difokuskan untuk keypad angka."""

    can_focus = True

    BINDINGS = [
        Binding("escape", "close_picker", show=False),
        Binding("enter", "toggle_picker", show=False),
    ]

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
        self._select_id = select_id  # dipertahankan untuk kompatibilitas
        self._value_id = value_id
        self._options = list(options)
        self._default_index = default_index
        self._current = ""

    def _label_for(self, unit_id: str) -> str:
        for label, uid in self._options:
            if uid == unit_id:
                return label
        return unit_id

    def _ensure_current(self) -> None:
        if not self._options:
            self._current = ""
            return
        valid = {uid for _label, uid in self._options}
        if self._current not in valid:
            index = min(self._default_index, len(self._options) - 1)
            self._current = self._options[index][1]

    def _sync_button(self) -> None:
        try:
            button = self.query_one(f"#{self._select_id}", Button)
        except Exception:
            return
        label = self._label_for(self._current) if self._current else "Pilih satuan"
        button.label = f"{label}  ▾"

    def _sync_list(self) -> None:
        try:
            option_list = self.query_one(f"#{self._select_id}-list", OptionList)
        except Exception:
            return
        option_list.clear_options()
        for label, uid in self._options:
            option_list.add_option(Option(label, id=uid))
        # Sorot unit aktif.
        if self._current:
            for index, (_label, uid) in enumerate(self._options):
                if uid == self._current:
                    option_list.highlighted = index
                    break

    def set_options(self, options: list[tuple[str, str]]) -> None:
        """Ganti daftar unit; unit pertama dipilih jika current tidak valid."""
        self._options = list(options)
        self._ensure_current()
        self._sync_button()
        self._sync_list()
        self.action_close_picker()

    @property
    def value(self) -> str:
        self._ensure_current()
        return self._current

    def select_unit(self, unit_id: str) -> None:
        valid = {uid for _label, uid in self._options}
        if unit_id in valid:
            self._current = unit_id
            self._sync_button()
            self._sync_list()

    def show_value(self, text: str) -> None:
        try:
            self.query_one(f"#{self._value_id}", Static).update(text)
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        self._ensure_current()
        label = self._label_for(self._current) if self._current else "Pilih satuan"
        yield Static(self._title, classes="unit-title")
        yield Button(f"{label}  ▾", id=self._select_id, classes="unit-pick")
        yield OptionList(id=f"{self._select_id}-list", classes="unit-list")
        yield Static("0", id=self._value_id, classes="unit-value")

    def on_mount(self) -> None:
        self._sync_list()
        self.action_close_picker()

    def _picker_open(self) -> bool:
        try:
            return self.query_one(f"#{self._select_id}-list", OptionList).display
        except Exception:
            return False

    def action_toggle_picker(self) -> None:
        if self._picker_open():
            self.action_close_picker()
        else:
            self.action_open_picker()

    def action_open_picker(self) -> None:
        try:
            option_list = self.query_one(f"#{self._select_id}-list", OptionList)
        except Exception:
            return
        option_list.display = True
        option_list.focus()

    def action_close_picker(self) -> None:
        try:
            option_list = self.query_one(f"#{self._select_id}-list", OptionList)
        except Exception:
            return
        option_list.display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == self._select_id:
            event.stop()
            self.action_toggle_picker()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option_list_id = f"{self._select_id}-list"
        if event.option_list.id != option_list_id:
            return
        event.stop()
        unit_id = event.option.id
        if unit_id is None:
            return
        self._current = str(unit_id)
        self._sync_button()
        self.action_close_picker()
        self.post_message(self.UnitChanged(self._current, self.id or ""))

    def on_descendant_blur(self, event) -> None:
        # Tutup picker ketika fokus keluar dari selector (aman, tidak menggeser).
        def _close_if_outside() -> None:
            focused = self.app.focused
            try:
                picker = self.query_one(f"#{self._select_id}-list", OptionList)
                button = self.query_one(f"#{self._select_id}", Button)
            except Exception:
                return
            if focused not in (picker, button) and not self._picker_open() is False:
                picker.display = False

        self.call_after_refresh(_close_if_outside)
