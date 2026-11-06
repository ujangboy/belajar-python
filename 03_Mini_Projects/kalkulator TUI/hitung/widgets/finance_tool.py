"""Tool keuangan."""

from __future__ import annotations

from decimal import Decimal

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Select, Static

from ..engines.finance_engine import compound_interest, loan_payment, savings_future, simple_interest
from ..engines.util import EngineError
from ..format import format_number
from datetime import datetime
from ..history import HistoryRecord

MODES = [("Bunga sederhana", "simple"), ("Bunga majemuk", "compound"), ("Pinjaman/cicilan bulanan", "loan"), ("Tabungan masa depan", "savings")]


class FinanceTool(Vertical):
    DEFAULT_CSS = "FinanceTool{height:1fr;padding:1 2;} #fin-title{color:$primary;text-style:bold;} .row{height:auto;margin-top:1;} .out{border:round $border;background:$surface;padding:1;margin-top:1;height:auto;} .hint{color:$text-muted;}"

    BINDINGS = [Binding("escape", "go", "Dashboard", show=False)]

    def compose(self) -> ComposeResult:
        yield Static("Keuangan (perhitungan Decimal)", id="fin-title")
        yield Static("Hasil numerik, bukan nasihat keuangan.", classes="hint")
        yield Select(MODES, value="simple", allow_blank=False, id="fin-mode")
        with VerticalScroll():
            yield Label("Pokok / pinjaman / setoran bulanan", classes="row")
            yield Input("1000000", id="fin-a")
            yield Label("Bunga % per tahun", classes="row")
            yield Input("10", id="fin-b")
            yield Label("Waktu (tahun) atau bulan (pinjaman/tabungan)", classes="row")
            yield Input("1", id="fin-c")
            yield Label("Periode majemuk/tahun (khusus bunga majemuk)", classes="row")
            yield Input("12", id="fin-d")
            with Horizontal(classes="row"):
                yield Button("Hitung", id="fin-run", variant="primary")
                yield Button("Dashboard", id="fin-home")
            yield Static("", id="fin-out", classes="out")

    def _fmt(self, v):
        s = self.app.settings
        if isinstance(v, Decimal):
            v = float(v)
        return format_number(float(v), precision=s.precision, thousands=s.thousands, number_format=getattr(s, "number_format", "id"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "fin-home": self.app.action_go_dashboard(); return
        if event.button.id != "fin-run": return
        mode = str(self.query_one("#fin-mode", Select).value)
        a = self.query_one("#fin-a", Input).value.strip().replace(",", ".")
        b = self.query_one("#fin-b", Input).value.strip().replace(",", ".")
        c = self.query_one("#fin-c", Input).value.strip().replace(",", ".")
        d = self.query_one("#fin-d", Input).value.strip().replace(",", ".")
        out = self.query_one("#fin-out", Static)
        try:
            if mode == "simple": r = simple_interest(a,b,c)
            elif mode == "compound": r = compound_interest(a,b,c,d)
            elif mode == "loan": r = loan_payment(a,b,c)
            else: r = savings_future(a,b,c)
            lines = [f"{k}: {self._fmt(v)}" if isinstance(v, (Decimal, float, int)) else f"{k}: {v}" for k,v in r.items()]
            text = "\n".join(lines)
            out.update(text)
            key = next((v for v in r.values() if isinstance(v, Decimal)), Decimal(0))
            rec = HistoryRecord(at=datetime.now().astimezone(), expression=f"finance:{mode}", result=str(key), value=float(key), category="finance")
            self.app.storage.append_history(rec); self.app.records.append(rec); self.app.refresh_dashboard_recent()
        except (EngineError, ValueError) as e:
            out.update(f"Error: {e}")

    def action_go(self): self.app.action_go_dashboard()
