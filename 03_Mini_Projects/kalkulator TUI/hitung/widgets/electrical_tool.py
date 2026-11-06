"""Tool kelistrikan (Hukum Ohm)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Static

from ..engines.electrical_engine import ohms_law
from ..engines.util import EngineError
from ..format import format_number
from datetime import datetime
from ..history import HistoryRecord


class ElectricalTool(Vertical):
    DEFAULT_CSS = "ElectricalTool{height:1fr;padding:1 2;} #el-title{color:$primary;text-style:bold;} .row{height:auto;margin-top:1;} .out{border:round $border;background:$surface;padding:1;margin-top:1;height:auto;} .hint{color:$text-muted;}"

    BINDINGS = [Binding("escape", "go", "Dashboard", show=False)]

    def compose(self) -> ComposeResult:
        yield Static("Kelistrikan — Hukum Ohm", id="el-title")
        yield Static("Isi tepat 2 nilai, kosongkan 1 nilai yang ingin dihitung.", classes="hint")
        with VerticalScroll():
            yield Label("Tegangan V (volt)", classes="row")
            yield Input("", id="el-v", placeholder="mis. 12")
            yield Label("Arus I (ampere)", classes="row")
            yield Input("", id="el-i", placeholder="mis. 2")
            yield Label("Hambatan R (ohm)", classes="row")
            yield Input("", id="el-r", placeholder="mis. 6")
            with Horizontal(classes="row"):
                yield Button("Hitung", id="el-run", variant="primary")
                yield Button("Dashboard", id="el-home")
            yield Static("", id="el-out", classes="out")

    def _fmt(self, v): s=self.app.settings; return format_number(float(v), precision=s.precision, thousands=s.thousands, number_format=getattr(s, "number_format", "id"))

    def _opt(self, wid: str):
        t = self.query_one(f"#{wid}", Input).value.strip().replace(",", ".")
        return float(t) if t else None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "el-home": self.app.action_go_dashboard(); return
        if event.button.id != "el-run": return
        out = self.query_one("#el-out", Static)
        try:
            r = ohms_law(voltage=self._opt("el-v"), current=self._opt("el-i"), resistance=self._opt("el-r"))
            text = (f"Rumus: {r['formula']}\nSatuan: {r['units']}\n\n"
                    f"V = {self._fmt(r['voltage'])} V\nI = {self._fmt(r['current'])} A\n"
                    f"R = {self._fmt(r['resistance'])} Ω\nP = {self._fmt(r['power'])} W")
            out.update(text)
            rec = HistoryRecord(at=datetime.now().astimezone(), expression=f"ohm:{r['formula']}", result=f"P={r['power']:.4g}W", value=float(r['power']), category="electrical")
            self.app.storage.append_history(rec); self.app.records.append(rec); self.app.refresh_dashboard_recent()
        except (EngineError, ValueError) as e:
            out.update(f"Error: {e}")

    def action_go(self): self.app.action_go_dashboard()
