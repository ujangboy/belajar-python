"""Layar kalkulator ilmiah."""

from __future__ import annotations

from datetime import date, datetime

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.widgets import Button, Input, Static

from ..engine import CalcError, evaluate
from ..format import format_number
from ..history import HistoryRecord, today_count
from ..widgets.calc_card import CalcCard

FUNCTION_PAD = [
    ("sin", "sin(", "sin"), ("cos", "cos(", "cos"), ("tan", "tan(", "tan"), ("sqrt", "sqrt(", "sqrt"),
    ("asin", "asin(", "asin"), ("acos", "acos(", "acos"), ("atan", "atan(", "atan"), ("cbrt", "cbrt(", "cbrt"),
    ("log", "log(", "log"), ("ln", "ln(", "ln"), ("logn", "logn(2;", "logn"), ("abs", "abs(", "abs"),
    ("ncr", "ncr(", "nCr"), ("npr", "npr(", "nPr"), ("exp", "exp(", "exp"), ("fact", "!", "!"),
    ("pi", "pi", "pi"), ("e", "e", "e"), ("lpar", "(", "("), ("rpar", ")", ")"),
]


class ScientificTool(Vertical):
    DEFAULT_CSS = """
    ScientificTool { height: 1fr; layout: vertical; padding: 1 2; }
    #sci-header { height: 1; layout: horizontal; }
    #sci-title { width: 1fr; color: $primary; text-style: bold; }
    #sci-angle { width: auto; color: $text-muted; }
    #sci-body { height: 1fr; layout: horizontal; align: center top; }
    #sci-card { width: 1fr; max-width: 72; height: auto; border: round $border; background: $surface; padding: 1 2; }
    #sci-pad { width: 30; height: auto; margin-left: 2; border: round $border; background: $panel; padding: 1; }
    #sci-pad-grid { layout: grid; grid-size: 4; grid-gutter: 0 1; height: auto; }
    .pad-btn { min-width: 6; }
    #sci-hint { height: 1; color: $text-muted; }
    """

    BINDINGS = [
        Binding("escape", "clear_or_back", "Bersihkan/Kembali", key_display="Esc", show=False),
        Binding("ctrl+y", "copy_result", "Salin", show=False),
        Binding("f6", "toggle_angle", "DEG/RAD", key_display="F6"),
    ]

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self._pending_input: str | None = None
        self._last_result: str | None = None

    @property
    def host(self):
        return self.app

    def compose(self) -> ComposeResult:
        with Horizontal(id="sci-header"):
            yield Static("Kalkulator Ilmiah", id="sci-title")
            yield Static("", id="sci-angle")
        with Container(id="sci-body"):
            with Vertical(id="sci-card"):
                yield Static("HASIL", id="result-label")
                yield Static("0", id="result")
                yield Static("", id="last")
                yield Static("EKSPRESI", id="expr-label")
                yield Input(placeholder="mis. sin(30) + ncr(5;2) · logn(2;8)", id="expr")
                yield Static("", id="status")
            with Vertical(id="sci-pad"):
                yield Static("FUNGSI", id="pad-title")
                with Container(id="sci-pad-grid"):
                    for key, _insert, label in FUNCTION_PAD:
                        yield Button(label, id=f"pad-{key}", classes="pad-btn")
                yield Button("DEG/RAD (F6)", id="pad-angle", classes="pad-btn")
                yield Button("Salin (Ctrl+Y)", id="pad-copy", classes="pad-btn")
                yield Button("Dashboard (Ctrl+H)", id="pad-home", classes="pad-btn")
        yield Static("Enter hitung · F6 DEG/RAD · Ctrl+Y salin · Esc bersihkan · Ctrl+H dashboard", id="sci-hint")

    def on_mount(self) -> None:
        self._refresh_angle()
        self._refresh_preview()
        try:
            self.query_one("#expr", Input).focus()
        except NoMatches:
            pass

    def _refresh_angle(self) -> None:
        angle = getattr(self.host.settings, "angle", "deg")
        self.query_one("#sci-angle", Static).update(f"Mode sudut: {angle.upper()}")

    def _format(self, value: float) -> str:
        s = self.host.settings
        return format_number(value, precision=s.precision, thousands=s.thousands, number_format=getattr(s, "number_format", "id"))

    def _input(self) -> Input:
        return self.query_one("#expr", Input)

    def _set_input(self, value: str) -> None:
        field = self._input()
        self._pending_input = value
        field.value = value
        try:
            field.cursor_position = len(value)
        except Exception:
            pass
        field.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if self._pending_input is not None and event.value == self._pending_input:
            self._pending_input = None
            return
        self._pending_input = None
        self._refresh_preview()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.calculate()

    def _refresh_preview(self) -> None:
        raw = self._input().value.strip()
        result = self.query_one("#result", Static)
        status = self.query_one("#status", Static)
        if not raw:
            result.update(self._last_result or "0")
            result.set_class(False, "-preview")
            status.update("Ketik ekspresi ilmiah lalu Enter.")
            status.set_class(False, "-error")
            return
        try:
            value = evaluate(raw, angle=self.host.settings.angle, ans=self.host.ans)
        except CalcError:
            status.update("Periksa ekspresi. Fungsi multi-argumen: ncr(5;2), logn(2;8).")
            status.set_class(False, "-error")
            return
        result.update(self._format(value))
        result.set_class(True, "-preview")
        status.update("Enter untuk menyimpan hasil ini.")
        status.set_class(False, "-error")

    def calculate(self) -> None:
        raw = self._input().value.strip()
        status = self.query_one("#status", Static)
        result = self.query_one("#result", Static)
        if not raw:
            status.update("Ekspresi masih kosong.",)
            status.set_class(True, "-error")
            return
        try:
            value = evaluate(raw, angle=self.host.settings.angle, ans=self.host.ans)
        except CalcError as error:
            status.update(str(error))
            status.set_class(True, "-error")
            if self.host.settings.sound:
                self.app.bell()
            return
        formatted = self._format(value)
        record = HistoryRecord(
            at=datetime.now().astimezone(),
            expression=raw,
            result=formatted,
            value=value,
            category="scientific",
        )
        try:
            self.host.storage.append_history(record)
        except OSError as error:
            self.app.notify(f"Gagal menyimpan riwayat: {error}", severity="error", timeout=8)
        self.host.records.append(record)
        self.host.ans = value
        self.host.last_expression = raw
        self.host.last_result = formatted
        self._last_result = formatted
        self.query_one("#last", Static).update(f"terakhir: {raw} = {formatted}")
        result.update(formatted)
        result.set_class(False, "-preview")
        status.update("Tersimpan (kategori scientific).")
        status.set_class(False, "-error")
        self._set_input("")
        try:
            self.app.refresh_dashboard_recent()
        except Exception:
            pass
        if self.host.settings.sound:
            self.app.bell()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "pad-angle":
            self.action_toggle_angle()
        elif bid == "pad-copy":
            self.action_copy_result()
        elif bid == "pad-home":
            self.app.action_go_dashboard()
        elif bid.startswith("pad-"):
            key = bid.removeprefix("pad-")
            insert = next((ins for k, ins, _ in FUNCTION_PAD if k == key), "")
            if not insert:
                return
            field = self._input()
            val = field.value
            pos = len(val)
            try:
                pos = field.cursor_position
            except Exception:
                pass
            self._set_input(val[:pos] + insert + val[pos:])

    def action_toggle_angle(self) -> None:
        from ..config import Settings

        s = self.host.settings
        new_angle = "rad" if s.angle == "deg" else "deg"
        self.host.settings = Settings(
            precision=s.precision, thousands=s.thousands, angle=new_angle, sound=s.sound,
            theme=s.theme, accent=s.accent, number_format=s.number_format,
            history_limit=s.history_limit, favorites=list(s.favorites),
        )
        try:
            self.host.storage.save_settings(self.host.settings)
        except OSError:
            pass
        self._refresh_angle()
        self._refresh_preview()
        self.app.notify(f"Mode sudut: {new_angle.upper()}", timeout=2)

    def action_copy_result(self) -> None:
        raw = self._input().value.strip()
        text = self._last_result
        if raw:
            try:
                text = self._format(evaluate(raw, angle=self.host.settings.angle, ans=self.host.ans))
            except CalcError:
                pass
        if not text:
            self.app.notify("Belum ada hasil untuk disalin.", timeout=2)
            return
        self.app.copy_to_clipboard(text)
        self.app.notify(f"Disalin: {text}", timeout=2)

    def action_clear_or_back(self) -> None:
        field = self._input()
        if field.value:
            self._set_input("")
            self._refresh_preview()
        else:
            self.app.action_go_dashboard()
