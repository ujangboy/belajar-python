"""Keypad kalkulator berbasis tombol — memancarkan KeyPressed ke tool induk."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Button

# (button_id, label, insert_text) — insert_text kosong berarti aksi khusus.
# Layout 4 kolom × 6 baris (PRD 4.0 §5).
STANDARD_KEYS: tuple[tuple[str, str, str], ...] = (
    ("key-clear", "C", ""),
    ("key-backspace", "←", ""),
    ("key-lparen", "(", "("),
    ("key-rparen", ")", ")"),
    ("key-7", "7", "7"),
    ("key-8", "8", "8"),
    ("key-9", "9", "9"),
    ("key-divide", "÷", "/"),
    ("key-4", "4", "4"),
    ("key-5", "5", "5"),
    ("key-6", "6", "6"),
    ("key-multiply", "×", "*"),
    ("key-1", "1", "1"),
    ("key-2", "2", "2"),
    ("key-3", "3", "3"),
    ("key-minus", "−", "-"),
    ("key-sign", "+/−", ""),
    ("key-0", "0", "0"),
    ("key-dot", ".", "."),
    ("key-plus", "+", "+"),
    ("key-percent", "%", "%"),
    ("key-ans", "ANS", "ans"),
    ("key-pow", "xʸ", "^"),
    ("key-equals", "=", ""),
)

# Grid 7 kolom × 6 baris. Fungsi/ikon utama PRD v3.0 tercakup.
# Backspace: gunakan tombol keyboard; Clear tersedia.
SCIENTIFIC_KEYS: tuple[tuple[str, str, str], ...] = (
    ("key-swap", "⇄", ""),
    ("key-angle", "DEG", ""),
    ("key-sqrt", "√", "sqrt("),
    ("key-cbrt", "∛", "cbrt("),
    ("key-sq", "x²", "^2"),
    ("key-pow", "xʸ", "^"),
    ("key-clear", "C", ""),
    ("key-sin", "sin", "sin("),
    ("key-cos", "cos", "cos("),
    ("key-tan", "tan", "tan("),
    ("key-lparen", "(", "("),
    ("key-rparen", ")", ")"),
    ("key-fact", "x!", "!"),
    ("key-divide", "÷", "/"),
    ("key-ln", "ln", "ln("),
    ("key-log", "log", "log("),
    ("key-exp", "eˣ", "exp("),
    ("key-7", "7", "7"),
    ("key-8", "8", "8"),
    ("key-9", "9", "9"),
    ("key-multiply", "×", "*"),
    ("key-recip", "1/x", ""),
    ("key-abs", "|x|", "abs("),
    ("key-pi", "π", "pi"),
    ("key-4", "4", "4"),
    ("key-5", "5", "5"),
    ("key-6", "6", "6"),
    ("key-minus", "−", "-"),
    ("key-ans", "ANS", "ans"),
    ("key-e", "e", "e"),
    ("key-backspace", "←", ""),
    ("key-1", "1", "1"),
    ("key-2", "2", "2"),
    ("key-3", "3", "3"),
    ("key-plus", "+", "+"),
    ("key-sign", "+/−", ""),
    ("key-0", "0", "0"),
    ("key-dot", ".", "."),
    ("key-percent", "%", "%"),
    ("key-equals", "=", ""),
)


class KeyPressed(Message):
    """Tombol keypad ditekan. ``key`` adalah button_id (mis. ``key-7``)."""

    def __init__(self, key: str) -> None:
        super().__init__()
        self.key = key


class ScientificKeypad(Vertical):
    """Grid tombol; setiap tekan memancarkan ``KeyPressed`` ke induknya."""

    KEYS: tuple[tuple[str, str, str], ...] = ()

    def __init__(
        self,
        keys: tuple[tuple[str, str, str], ...] | None = None,
        *,
        columns: int = 4,
        prefix: str = "",
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.keys = tuple(self.KEYS if keys is None else keys)
        self.columns = columns
        self.prefix = prefix
        self.add_class(f"cols-{columns}")

    @property
    def insert_texts(self) -> dict[str, str]:
        """Peta button_id → teks yang disisipkan ("" untuk aksi khusus)."""
        return {key_id: insert for key_id, _label, insert in self.keys}

    @staticmethod
    def _type_class(key_id: str) -> str:
        digits = {f"key-{d}" for d in "0123456789"}
        operators = {"key-divide", "key-multiply", "key-minus", "key-plus"}
        if key_id in digits or key_id == "key-dot":
            return "key-numeric"
        if key_id in operators:
            return "key-operator"
        if key_id == "key-equals":
            return "key-equals"
        if key_id == "key-clear":
            return "key-clear"
        if key_id == "key-backspace":
            return "key-backspace"
        scientific = {
            "key-sin", "key-cos", "key-tan", "key-ln", "key-log", "key-sqrt", "key-cbrt",
            "key-sq", "key-pow", "key-exp", "key-fact", "key-recip", "key-abs", "key-pi",
            "key-e", "key-angle", "key-swap",
        }
        if key_id in scientific:
            return "key-scientific"
        return "key-utility"

    _TOOLTIPS = {
        "key-backspace": "Hapus 1 karakter (Backspace)",
        "key-clear": "Bersihkan ekspresi",
        "key-equals": "Hitung",
        "key-ans": "Hasil sebelumnya (ANS)",
        "key-angle": "Ganti DEG/RAD",
        "key-swap": "Tukar nilai/ANS",
    }

    def compose(self) -> ComposeResult:
        for key_id, label, _insert in self.keys:
            if not label and not key_id:
                continue
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
        self.set_class(width < 84, "keypad-sm")
        self.set_class(84 <= width < 120, "keypad-md")
        self.set_class(width >= 120, "keypad-lg")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id:
            key = event.button.id.removeprefix(self.prefix)
            self.post_message(KeyPressed(key))
