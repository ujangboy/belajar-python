"""Keypad kalkulator berbasis tombol — memancarkan KeyPressed ke tool induk."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Button

# (button_id, label, insert_text) — insert_text kosong berarti aksi khusus.
STANDARD_KEYS: tuple[tuple[str, str, str], ...] = (
    ("key-clear", "C", ""),
    ("key-backspace", "⌫", ""),
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
    ("key-0", "0", "0"),
    ("key-dot", ".", "."),
    ("key-percent", "%", "%"),
    ("key-plus", "+", "+"),
    ("key-sign", "+/−", ""),
    ("key-pow", "^", "^"),
    ("key-ans", "ANS", "ans"),
    ("key-equals", "=", ""),
)

# Grid 7 kolom × 5 baris sesuai desain §7. Tanpa tombol % (milik kalkulator
# standar); Backspace ilmiah dipetakan ke tombol keyboard.
SCIENTIFIC_KEYS: tuple[tuple[str, str, str], ...] = (
    ("key-swap", "⇄", ""),
    ("key-angle", "DEG", ""),
    ("key-sqrt", "√", "sqrt("),
    ("key-clear", "C", ""),
    ("key-lparen", "(", "("),
    ("key-rparen", ")", ")"),
    ("key-divide", "÷", "/"),
    ("key-sin", "sin", "sin("),
    ("key-cos", "cos", "cos("),
    ("key-tan", "tan", "tan("),
    ("key-7", "7", "7"),
    ("key-8", "8", "8"),
    ("key-9", "9", "9"),
    ("key-multiply", "×", "*"),
    ("key-ln", "ln", "ln("),
    ("key-log", "log", "log("),
    ("key-recip", "1/x", ""),
    ("key-4", "4", "4"),
    ("key-5", "5", "5"),
    ("key-6", "6", "6"),
    ("key-minus", "−", "-"),
    ("key-exp", "eˣ", "exp("),
    ("key-sq", "x²", "^2"),
    ("key-pow", "xʸ", "^"),
    ("key-1", "1", "1"),
    ("key-2", "2", "2"),
    ("key-3", "3", "3"),
    ("key-plus", "+", "+"),
    ("key-abs", "|x|", "abs("),
    ("key-pi", "π", "pi"),
    ("key-e", "e", "e"),
    ("key-sign", "+/−", ""),
    ("key-0", "0", "0"),
    ("key-dot", ".", "."),
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

    def compose(self) -> ComposeResult:
        for key_id, label, _insert in self.keys:
            button = Button(label, id=f"{self.prefix}{key_id}", classes="key")
            # Tanpa animasi tekan: klik cepat berulang (mis. "100") tidak boleh hilang.
            button.active_effect_duration = 0
            yield button

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id:
            key = event.button.id.removeprefix(self.prefix)
            self.post_message(KeyPressed(key))
