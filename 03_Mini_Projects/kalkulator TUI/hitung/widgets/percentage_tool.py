"""Tool persentase sehari-hari."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Select, Static

from ..engines.percentage_engine import discount_price, percent_change, percent_of, tax_amount, tip_amount, what_percent
from ..engines.util import EngineError
from ..format import format_number
from ..history import HistoryRecord
from datetime import datetime

MODES = [
    ("X% dari Y", "of"),
    ("X adalah berapa % dari Y", "what"),
    ("Perubahan % (awal -> baru)", "change"),
    ("Diskon", "discount"),
    ("Pajak", "tax"),
    ("Tip / bagi orang", "tip"),
]


class PercentageTool(Vertical):
    DEFAULT_CSS = "PercentageTool { height:1fr; padding:1 2; } #pct-title{color:$primary;text-style:bold;} .row{height:auto; margin-top:1;} .out{border:round $border; background:$surface; padding:1; margin-top:1; height:auto;}"

    BINDINGS = [Binding("escape", "go", "Dashboard", show=False)]

    def compose(self) -> ComposeResult:
        yield Static("Persentase & Sehari-hari", id="pct-title")
        yield Label("Mode")
        yield Select(MODES, value="of", allow_blank=False, id="pct-mode")
        with VerticalScroll():
            yield Label("Nilai A / persen / awal / harga / tagihan", classes="row")
            yield Input("100", id="pct-a")
            yield Label("Nilai B / total / baru / persen / orang (untuk tip)", classes="row")
            yield Input("10", id="pct-b")
            yield Label("Orang (khusus tip, opsional)", classes="row")
            yield Input("1", id="pct-c")
            with Horizontal(classes="row"):
                yield Button("Hitung", id="pct-run", variant="primary")
                yield Button("Dashboard", id="pct-home")
            yield Static("", id="pct-out", classes="out")

    def _fmt(self, v: float) -> str:
        s = self.app.settings
        return format_number(v, precision=s.precision, thousands=s.thousands, number_format=getattr(s, "number_format", "id"))

    def _num(self, wid: str) -> float:
        return float(self.query_one(f"#{wid}", Input).value.strip().replace(",", "."))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "pct-home":
            self.app.action_go_dashboard(); return
        if event.button.id != "pct-run":
            return
        out = self.query_one("#pct-out", Static)
        try:
            mode = str(self.query_one("#pct-mode", Select).value)
            a, b = self._num("pct-a"), self._num("pct-b")
            text = ""
            val = 0.0
            if mode == "of":
                val = percent_of(a, b); text = f"{self._fmt(a)}% dari {self._fmt(b)} = {self._fmt(val)}"
            elif mode == "what":
                val = what_percent(a, b); text = f"{self._fmt(a)} adalah {self._fmt(val)}% dari {self._fmt(b)}"
            elif mode == "change":
                val = percent_change(a, b); text = f"Perubahan: {self._fmt(val)}%"
            elif mode == "discount":
                amt, final = discount_price(a, b); val = final; text = f"Diskon: {self._fmt(amt)} · Harga akhir: {self._fmt(final)}"
            elif mode == "tax":
                amt, final = tax_amount(a, b); val = final; text = f"Pajak: {self._fmt(amt)} · Total: {self._fmt(final)}"
            elif mode == "tip":
                c = self._num("pct-c")
                amt, total, per = tip_amount(a, b, int(c)); val = total
                text = f"Tip: {self._fmt(amt)} · Total: {self._fmt(total)} · Per orang: {self._fmt(per)}"
            out.update(text)
            rec = HistoryRecord(at=datetime.now().astimezone(), expression=f"percentage:{mode} {a},{b}", result=self._fmt(val), value=float(val), category="percentage")
            self.app.storage.append_history(rec); self.app.records.append(rec); self.app.refresh_dashboard_recent()
        except (EngineError, ValueError) as e:
            out.update(f"Error: {e}")

    def action_go(self) -> None:
        self.app.action_go_dashboard()
