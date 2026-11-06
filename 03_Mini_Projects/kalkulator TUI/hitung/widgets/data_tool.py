"""Tool data & sistem angka."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Select, Static

from ..engines.data_engine import bitwise, number_bases
from ..engines.util import EngineError
from datetime import datetime
from ..history import HistoryRecord

BASES = [("Desimal (10)", "10"), ("Biner (2)", "2"), ("Oktal (8)", "8"), ("Heksadesimal (16)", "16")]
OPS = [("AND", "AND"), ("OR", "OR"), ("XOR", "XOR"), ("NOT", "NOT"), ("Shift Left", "SHL"), ("Shift Right", "SHR")]


class DataTool(Vertical):
    DEFAULT_CSS = "DataTool{height:1fr;padding:1 2;} #data-title{color:$primary;text-style:bold;} .row{height:auto;margin-top:1;} .out{border:round $border;background:$surface;padding:1;margin-top:1;height:auto;}"

    BINDINGS = [Binding("escape", "go", "Dashboard", show=False)]

    def compose(self) -> ComposeResult:
        yield Static("Data & Sistem Angka", id="data-title")
        with VerticalScroll():
            yield Label("Konversi basis - nilai & basis asal", classes="row")
            with Horizontal(classes="row"):
                yield Input("255", id="base-val")
                yield Select(BASES, value="10", allow_blank=False, id="base-from")
                yield Button("Konversi", id="base-run", variant="primary")
            yield Static("", id="base-out", classes="out")
            yield Label("Bitwise (integer 32-bit mask)", classes="row")
            with Horizontal(classes="row"):
                yield Input("6", id="bw-a")
                yield Select(OPS, value="AND", allow_blank=False, id="bw-op")
                yield Input("3", id="bw-b")
                yield Button("Hitung", id="bw-run", variant="primary")
            yield Static("", id="bw-out", classes="out")
            yield Button("Dashboard", id="data-home", classes="row")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "data-home": self.app.action_go_dashboard(); return
        if bid == "base-run":
            out = self.query_one("#base-out", Static)
            try:
                r = number_bases(self.query_one("#base-val", Input).value, int(str(self.query_one("#base-from", Select).value)))
                text = f"BIN {r['bin']}\nOCT {r['oct']}\nDEC {r['dec']}\nHEX {r['hex']}"
                out.update(text)
                self._save(f"base:{r['dec']}", str(r['hex']), float(r['value']))
            except (EngineError, ValueError) as e:
                out.update(f"Error: {e}")
        elif bid == "bw-run":
            out = self.query_one("#bw-out", Static)
            try:
                a = int(float(self.query_one("#bw-a", Input).value.replace(",",".")))
                b = int(float(self.query_one("#bw-b", Input).value.replace(",",".")))
                op = str(self.query_one("#bw-op", Select).value)
                r = bitwise(a, op, b)
                out.update(f"{r['label']}\nDEC {r['dec']}  HEX {r['hex']}  BIN {r['bin']}")
                self._save(f"bit:{op}", str(r['hex']), float(r['dec']))
            except (EngineError, ValueError) as e:
                out.update(f"Error: {e}")

    def _save(self, expr, result, value):
        rec = HistoryRecord(at=datetime.now().astimezone(), expression=expr, result=result, value=value, category="data")
        self.app.storage.append_history(rec); self.app.records.append(rec); self.app.refresh_dashboard_recent()

    def action_go(self): self.app.action_go_dashboard()
