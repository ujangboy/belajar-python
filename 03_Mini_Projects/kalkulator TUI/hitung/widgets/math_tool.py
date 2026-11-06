"""Tool matematika & statistik."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Select, Static

from ..engines.math_engine import combinations, gcd, is_prime, lcm, permutations, prime_factors, stats
from ..engines.util import EngineError
from ..format import format_number
from datetime import datetime
from ..history import HistoryRecord

MODES = [("FPB (GCD)", "gcd"), ("KPK (LCM)", "lcm"), ("Prima?", "prime"), ("Faktorisasi prima", "factor"), ("Statistik (pisah spasi/koma)", "stats"), ("Permutasi nPr", "npr"), ("Kombinasi nCr", "ncr")]


class MathTool(Vertical):
    DEFAULT_CSS = "MathTool{height:1fr;padding:1 2;} #math-title{color:$primary;text-style:bold;} .row{height:auto;margin-top:1;} .out{border:round $border;background:$surface;padding:1;margin-top:1;height:auto;}"

    BINDINGS = [Binding("escape", "go", "Dashboard", show=False)]

    def compose(self) -> ComposeResult:
        yield Static("Matematika & Statistik", id="math-title")
        yield Select(MODES, value="gcd", allow_blank=False, id="math-mode")
        with VerticalScroll():
            yield Label("A / n / data", classes="row")
            yield Input("12", id="math-a")
            yield Label("B / r (jika perlu)", classes="row")
            yield Input("18", id="math-b")
            with Horizontal(classes="row"):
                yield Button("Hitung", id="math-run", variant="primary")
                yield Button("Dashboard", id="math-home")
            yield Static("", id="math-out", classes="out")

    def _fmt(self, v):
        s = self.app.settings
        return format_number(float(v), precision=s.precision, thousands=s.thousands, number_format=getattr(s, "number_format", "id"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "math-home": self.app.action_go_dashboard(); return
        if event.button.id != "math-run": return
        out = self.query_one("#math-out", Static)
        mode = str(self.query_one("#math-mode", Select).value)
        a_raw = self.query_one("#math-a", Input).value.strip().replace(",", ".")
        b_raw = self.query_one("#math-b", Input).value.strip().replace(",", ".")
        try:
            text = ""; val = 0.0
            if mode in {"gcd", "lcm", "npr", "ncr"}:
                a, b = int(float(a_raw)), int(float(b_raw))
                if mode == "gcd": val = gcd(a,b); text = f"FPB({a},{b}) = {val}"
                elif mode == "lcm": val = lcm(a,b); text = f"KPK({a},{b}) = {val}"
                elif mode == "npr": val = permutations(a,b); text = f"P({a},{b}) = {val}"
                else: val = combinations(a,b); text = f"C({a},{b}) = {val}"
            elif mode == "prime":
                n = int(float(a_raw)); ok = is_prime(n); val = 1 if ok else 0
                text = f"{n} {'adalah bilangan prima' if ok else 'bukan bilangan prima'}"
            elif mode == "factor":
                n = int(float(a_raw)); f = prime_factors(n); val = n; text = f"Faktor prima {n}: {' × '.join(map(str,f))}"
            else:
                parts = [p for p in a_raw.replace(";", " ").replace(",", " ").split() if p]
                nums = [float(p) for p in parts]
                s = stats(nums); val = float(s["mean"])
                text = "\n".join([f"n={int(s['count'])}", f"mean={self._fmt(s['mean'])}", f"median={self._fmt(s['median'])}", f"mode={s['mode']}", f"min={self._fmt(s['min'])}", f"max={self._fmt(s['max'])}", f"stdev={self._fmt(s['stdev'])}"])
            out.update(text)
            rec = HistoryRecord(at=datetime.now().astimezone(), expression=f"math:{mode} {a_raw} {b_raw}".strip(), result=str(val)[:80], value=float(val), category="math")
            self.app.storage.append_history(rec); self.app.records.append(rec); self.app.refresh_dashboard_recent()
        except (EngineError, ValueError, OverflowError) as e:
            out.update(f"Error: {e}")

    def action_go(self): self.app.action_go_dashboard()
