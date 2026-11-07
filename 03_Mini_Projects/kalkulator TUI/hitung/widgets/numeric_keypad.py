"""Keypad angka untuk konverter."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Button

# (button_id, label, insert_text) — insert kosong berarti aksi khusus.
NUMERIC_KEYS: tuple[tuple[str, str, str], ...] = (
    ("key-7", "7", "7"),
    ("key-8", "8", "8"),
    ("key-9", "9", "9"),
    ("key-backspace", "←", ""),
    ("key-4", "4", "4"),
    ("key-5", "5", "5"),
    ("key-6", "6", "6"),
    ("key-clear", "C", ""),
    ("key-1", "1", "1"),
    ("key-2", "2", "2"),
    ("key-3", "3", "3"),
    ("key-up", "↑", ""),
    ("key-sign", "+/−", ""),
    ("key-0", "0", "0"),
    ("key-dot", ".", "."),
    ("key-down", "↓", ""),
    ("key-equals", "=", ""),
)


class NumericKey(Message):
    """Tombol keypad angka ditekan; ``key`` adalah id logis (tanpa prefix)."""

    def __init__(self, key: str) -> None:
        super().__init__()
        self.key = key


class NumericKeypad(Vertical):
    KEYS: tuple[tuple[str, str, str], ...] = NUMERIC_KEYS

    def __init__(
        self,
        *,
        prefix: str = "",
        columns: int = 4,
        keys: tuple[tuple[str, str, str], ...] | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.prefix = prefix
        self.keys = tuple(self.KEYS if keys is None else keys)
        self.add_class(f"cols-{columns}")

    @property
    def insert_texts(self) -> dict[str, str]:
        return {key_id: insert for key_id, _label, insert in self.keys}

    @staticmethod
    def _type_class(key_id: str) -> str:
        if key_id in {"key-clear"}:
            return "key-clear"
        if key_id in {"key-backspace"}:
            return "key-backspace"
        if key_id in {"key-equals"}:
            return "key-equals"
        if key_id in {"key-up", "key-down"}:
            return "key-utility"
        if key_id.startswith("key-") and key_id.removeprefix("key-").isdigit():
            return "key-numeric"
        return "key-utility"

    _TOOLTIPS = {
        "key-backspace": "Hapus 1 karakter",
        "key-clear": "Bersihkan",
        "key-equals": "Simpan konversi",
        "key-up": "Fokus DARI",
        "key-down": "Fokus KE",
    }

    def compose(self) -> ComposeResult:
        for key_id, label, _insert in self.keys:
            classes = f"key {self._type_class(key_id)}"
            button = Button(
                label,
                id=f"{self.prefix}{key_id}",
                classes=classes,
                tooltip=self._TOOLTIPS.get(key_id),
            )
            # Tanpa animasi tekan: klik cepat berulang (mis. "100") tidak boleh hilang.
            button.active_effect_duration = 0
            yield button

    def on_mount(self) -> None:
        self._sync_size_class()

    def on_resize(self, event) -> None:
        self._sync_size_class()

    def _sync_size_class(self) -> None:
        try:
            width = self.size.width or self.app.size.width
        except Exception:
            width = 120
        self.set_class(width < 72, "keypad-sm")
        self.set_class(72 <= width < 110, "keypad-md")
        self.set_class(width >= 110, "keypad-lg")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id:
            event.stop()
            key = event.button.id.removeprefix(self.prefix)
            self.post_message(NumericKey(key))
