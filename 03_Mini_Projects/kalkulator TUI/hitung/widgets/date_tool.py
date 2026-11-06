"""Tool tanggal & waktu."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Select, Static

from ..engines.date_engine import add_days, age, date_diff, from_unix, to_unix
from ..engines.util import EngineError
from datetime import datetime
from ..history import HistoryRecord

MODES = [("Selisih tanggal", "diff"), ("Tambah/kurang hari", "add"), ("Usia", "age"), ("Unix -> tanggal UTC", "fromunix"), ("Tanggal -> Unix", "tounix")]


class DateTool(Vertical):
    DEFAULT_CSS = "DateTool{height:1fr;padding:1 2;} #date-title{color:$primary;text-style:bold;} .row{height:auto;margin-top:1;} .out{border:round $border;background:$surface;padding:1;margin-top:1;height:auto;} .hint{color:$text-muted;}"

    BINDINGS = [Binding("escape", "go", "Dashboard", show=False)]

    def compose(self) -> ComposeResult:
        yield Static("Tanggal & Waktu", id="date-title")
        yield Select(MODES, value="diff", allow_blank=False, id="date-mode")
        yield Static("Format tanggal: YYYY-MM-DD atau DD/MM/YYYY.", classes="hint")
        with VerticalScroll():
            yield Label("A / tanggal awal / lahir / timestamp / datetime", classes="row")
            yield Input("2026-01-01", id="date-a")
            yield Label("B / hari (+/-) / acuan (opsional)", classes="row")
            yield Input("2026-11-05", id="date-b")
            with Horizontal(classes="row"):
                yield Button("Hitung", id="date-run", variant="primary")
                yield Button("Dashboard", id="date-home")
            yield Static("", id="date-out", classes="out")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "date-home": self.app.action_go_dashboard(); return
        if event.button.id != "date-run": return
        mode = str(self.query_one("#date-mode", Select).value)
        a = self.query_one("#date-a", Input).value.strip()
        b = self.query_one("#date-b", Input).value.strip()
        out = self.query_one("#date-out", Static)
        try:
            text = ""; val = 0.0
            if mode == "diff":
                r = date_diff(a,b); val=r["days"]; text = f"Selisih: {r['days']} hari ({r['weeks']} minggu {r['remaining_days']} hari)"
            elif mode == "add":
                r = add_days(a, int(float(b or 0))); val=1; text = f"Hasil: {r.isoformat()}"
            elif mode == "age":
                r = age(a, b or None); val=r["years"]; text = f"Usia: {r['years']} tahun, {r['months']} bulan, {r['days']} hari\nTotal: {r['total_days']} hari"
            elif mode == "fromunix":
                r = from_unix(int(float(a))); val=1; text = f"UTC: {r.isoformat()}"
            else:
                r = to_unix(a); val=r; text = f"Unix timestamp: {r}"
            out.update(text)
            rec = HistoryRecord(at=datetime.now().astimezone(), expression=f"date:{mode} {a}", result=str(text).splitlines()[0][:80], value=float(val), category="date")
            self.app.storage.append_history(rec); self.app.records.append(rec); self.app.refresh_dashboard_recent()
        except (EngineError, ValueError) as e:
            out.update(f"Error: {e}")

    def action_go(self): self.app.action_go_dashboard()
