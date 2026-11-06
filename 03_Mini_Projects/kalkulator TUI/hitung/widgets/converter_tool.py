"""Widget konverter unit generik (UI)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Select, Static, Switch

from ..data.units import CategoryDef, list_categories
from ..engines.conversion_engine import ConversionError, convert_all, convert_value
from ..format import format_number
from ..history import HistoryRecord
from datetime import datetime


class ConverterTool(Vertical):
    DEFAULT_CSS = """
    ConverterTool { height: 1fr; padding: 1 2; layout: vertical; }
    #conv-title { color: $primary; text-style: bold; }
    #conv-note { color: $text-muted; height: auto; }
    #conv-form { height: auto; layout: grid; grid-size: 2; grid-gutter: 1 2; margin-top: 1; }
    .conv-field { height: auto; }
    #conv-actions { height: auto; layout: horizontal; margin-top: 1; }
    #conv-actions Button { margin-right: 1; }
    #conv-result { margin-top: 1; border: round $border; background: $surface; padding: 1 2; height: auto; }
    #conv-all-title { margin-top: 1; color: $text-muted; text-style: bold; }
    #conv-all { height: 1fr; border: round $border; background: $panel; padding: 1; }
    #conv-digital-row { height: auto; layout: horizontal; margin-top: 1; }
    #conv-digital-row Label { width: auto; margin-right: 1; color: $text-muted; }
    """

    BINDINGS = [
        Binding("escape", "go_dashboard", "Dashboard", show=False),
    ]

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self._categories = list_categories()
        self._cat: CategoryDef = self._categories[0]

    @property
    def host(self):
        return self.app

    def compose(self) -> ComposeResult:
        cat_opts = [(c.title, c.category_id) for c in self._categories]
        unit_opts = [(u.label, u.unit_id) for u in self._cat.units]
        default_to = unit_opts[min(1, len(unit_opts) - 1)][1] if unit_opts else None
        yield Static("Konverter Unit", id="conv-title")
        yield Static("Pilih kategori, masukkan nilai, lalu konversi. Esc/Ctrl+H kembali.", id="conv-note")
        with VerticalScroll(id="conv-scroll"):
            yield Label("Kategori")
            yield Select(cat_opts, value=self._cat.category_id, allow_blank=False, id="conv-category")
            with Horizontal(id="conv-digital-row"):
                yield Label("Penyimpanan data: SI (1000)")
                yield Switch(value=False, id="conv-iec")
                yield Label("IEC (1024)")
            with Container(id="conv-form"):
                with Vertical(classes="conv-field"):
                    yield Label("Nilai")
                    yield Input("1", id="conv-value")
                with Vertical(classes="conv-field"):
                    yield Label("Dari")
                    yield Select(unit_opts, value=unit_opts[0][1], allow_blank=False, id="conv-from")
                with Vertical(classes="conv-field"):
                    yield Label("Ke")
                    yield Select(unit_opts, value=default_to, allow_blank=False, id="conv-to")
                with Vertical(classes="conv-field"):
                    yield Label("Aksi")
                    yield Button("Konversi", id="conv-run", variant="primary")
            with Horizontal(id="conv-actions"):
                yield Button("Tukar unit", id="conv-swap")
                yield Button("Salin hasil", id="conv-copy")
                yield Button("Dashboard", id="conv-home")
            yield Static("", id="conv-result")
            yield Static("SEMUA KONVERSI", id="conv-all-title")
            yield Static("", id="conv-all")

    def on_mount(self) -> None:
        self._load_category(self._cat.category_id)
        self._convert()
        try:
            self.query_one("#conv-value", Input).focus()
        except Exception:
            pass

    def _fmt(self, value: float) -> str:
        s = self.host.settings
        return format_number(value, precision=s.precision, thousands=s.thousands, number_format=getattr(s, "number_format", "id"))

    def _mode(self) -> str:
        try:
            return "iec" if self.query_one("#conv-iec", Switch).value else "si"
        except Exception:
            return "si"

    def _load_category(self, category_id: str) -> None:
        from ..data.units import get_category

        cat = get_category(category_id)
        if cat is None:
            return
        self._cat = cat
        opts = [(u.label, u.unit_id) for u in cat.units]
        try:
            self.query_one("#conv-from", Select).set_options(opts)
            self.query_one("#conv-to", Select).set_options(opts)
            self.query_one("#conv-from", Select).value = opts[0][1]
            self.query_one("#conv-to", Select).value = opts[min(1, len(opts) - 1)][1]
        except Exception:
            pass
        try:
            row = self.query_one("#conv-digital-row")
            row.display = cat.kind == "digital"
        except Exception:
            pass
        note = cat.note or ""
        self.query_one("#conv-note", Static).update(
            f"Kategori: {cat.title}. {note} Esc/Ctrl+H kembali.".strip()
        )
        self._convert()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "conv-category" and event.value:
            self._load_category(str(event.value))
        elif event.select.id in {"conv-from", "conv-to"}:
            self._convert()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "conv-value":
            self._convert()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "conv-iec":
            self._convert()

    def _parse_value(self) -> float | None:
        raw = self.query_one("#conv-value", Input).value.strip().replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            return None

    def _convert(self) -> None:
        result_box = self.query_one("#conv-result", Static)
        all_box = self.query_one("#conv-all", Static)
        value = self._parse_value()
        if value is None:
            result_box.update("Nilai tidak valid. Contoh: 12,5")
            all_box.update("")
            return
        try:
            from_id = str(self.query_one("#conv-from", Select).value)
            to_id = str(self.query_one("#conv-to", Select).value)
        except Exception:
            return
        mode = self._mode() if self._cat.kind == "digital" else None
        try:
            out = convert_value(value, from_id, to_id, self._cat.category_id, mode=mode)
            rows = convert_all(value, from_id, self._cat.category_id, mode=mode)
        except ConversionError as e:
            result_box.update(str(e))
            all_box.update("")
            return
        self._last_text = f"{self._fmt(value)} {from_id} = {self._fmt(out)} {to_id}"
        result_box.update(self._last_text)
        lines = [f"{label:<26} {self._fmt(val)}" for uid, label, val in rows]
        all_box.update("\n".join(lines))

    def _save_history(self) -> None:
        value = self._parse_value()
        if value is None or not getattr(self, "_last_text", None):
            return
        try:
            from_id = str(self.query_one("#conv-from", Select).value)
            to_id = str(self.query_one("#conv-to", Select).value)
            mode = self._mode() if self._cat.kind == "digital" else None
            out = convert_value(value, from_id, to_id, self._cat.category_id, mode=mode)
        except Exception:
            return
        record = HistoryRecord(
            at=datetime.now().astimezone(),
            expression=f"{value} {from_id} -> {to_id} [{self._cat.category_id}]",
            result=self._fmt(out),
            value=out,
            category=f"converter:{self._cat.category_id}",
            input_text=str(value),
            output_text=self._fmt(out),
        )
        try:
            self.host.storage.append_history(record)
            self.host.records.append(record)
            self.app.refresh_dashboard_recent()
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "conv-run":
            self._convert()
            self._save_history()
            self.app.notify("Konversi dihitung.", timeout=1)
        elif bid == "conv-swap":
            try:
                f = self.query_one("#conv-from", Select)
                t = self.query_one("#conv-to", Select)
                f.value, t.value = t.value, f.value
            except Exception:
                pass
            self._convert()
        elif bid == "conv-copy":
            text = getattr(self, "_last_text", "")
            if text:
                self.app.copy_to_clipboard(text)
                self.app.notify("Hasil disalin.", timeout=2)
        elif bid == "conv-home":
            self.app.action_go_dashboard()

    def action_go_dashboard(self) -> None:
        self.app.action_go_dashboard()
