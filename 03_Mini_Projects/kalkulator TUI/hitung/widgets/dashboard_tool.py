"""Dashboard awal Calculator Pro."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Static

from ..history import recent_records
from ..navigation import ToolSpec, default_tools, find_tool


class DashboardTool(Vertical):
    DEFAULT_CSS = """
    DashboardTool { height: 1fr; padding: 1 2; }
    #dash-title { color: $primary; text-style: bold; }
    #dash-sub { color: $text-muted; margin-bottom: 1; }
    #dash-search { margin-bottom: 1; }
    #dash-columns { height: 1fr; layout: horizontal; }
    #dash-main { width: 1fr; height: 1fr; }
    #dash-side { width: 38; height: 1fr; margin-left: 2; }
    .section { margin-top: 1; color: $text-muted; text-style: bold; }
    .tool-list { height: auto; }
    .dash-item { width: 100%; margin: 0 0 1 0; }
    #recent-box, #fav-box { height: auto; border: round $border; padding: 1; background: $panel; }
    """

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self._tools = [t for t in default_tools() if t.tool_id != "dashboard"]
        self._query = ""

    def compose(self) -> ComposeResult:
        yield Static("Calculator Pro", id="dash-title")
        yield Static("Pilih alat, cari cepat, atau buka favorit. Ctrl+K cari, Ctrl+H dashboard.", id="dash-sub")
        yield Input(placeholder="Cari alat… (Ctrl+K)", id="dash-search")
        with Horizontal(id="dash-columns"):
            with VerticalScroll(id="dash-main"):
                yield Static("ALAT", classes="section")
                yield Vertical(id="tool-list", classes="tool-list")
            with Vertical(id="dash-side"):
                yield Static("AKSES CEPAT", classes="section")
                yield Vertical(
                    Button("Standar (Ctrl+1)", id="open-standard", classes="dash-item"),
                    Button("Ilmiah (Ctrl+2)", id="open-scientific", classes="dash-item"),
                    Button("Konverter (Ctrl+3)", id="open-converter", classes="dash-item"),
                    Button("Riwayat (F2)", id="open-history", classes="dash-item"),
                    Button("Pengaturan (F3)", id="open-settings", classes="dash-item"),
                )
                yield Static("TERAKHIR", classes="section")
                yield Static("", id="recent-box")
                yield Static("FAVORIT (klik alat + ★)", classes="section")
                yield Vertical(id="fav-box", classes="tool-list")

    def on_mount(self) -> None:
        self.refresh_tools()
        self.refresh_recent()
        self.refresh_favorites()

    def refresh_tools(self) -> None:
        container = self.query_one("#tool-list", Vertical)
        container.remove_children()
        favs = set(getattr(self.app.settings, "favorites", []) or [])
        for tool in find_tool(self._tools, self._query):
            hint = f" · {tool.shortcut}" if tool.shortcut else ""
            star = "★" if tool.tool_id in favs else "☆"
            label = f"{star} {tool.title}{hint}\n{tool.description}"
            btn = Button(label, id=f"tool-{tool.tool_id}", classes="dash-item")
            container.mount(btn)

    def refresh_favorites(self) -> None:
        try:
            container = self.query_one("#fav-box", Vertical)
        except Exception:
            return
        container.remove_children()
        favs = list(getattr(self.app.settings, "favorites", []) or [])
        by_id = {t.tool_id: t for t in self._tools}
        shown = [by_id[f] for f in favs if f in by_id]
        if not shown:
            container.mount(Static("Belum ada favorit. Buka alat dari daftar lalu simpan via config (sementara)."))
            return
        for tool in shown[:8]:
            container.mount(Button(f"★ {tool.title}", id=f"fav-{tool.tool_id}", classes="dash-item"))

    def refresh_recent(self) -> None:
        try:
            box = self.query_one("#recent-box", Static)
        except Exception:
            return
        records = getattr(self.app, "records", [])
        recent = recent_records(records, 5)
        if not recent:
            box.update("Belum ada hitungan.")
            return
        lines = []
        for r in recent:
            expr = (r.expression[:28] + "…") if len(r.expression) > 28 else r.expression
            lines.append(f"{expr} = {r.result}")
        box.update("\n".join(lines))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "dash-search":
            self._query = event.value
            self.refresh_tools()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        app = self.app
        if bid == "open-standard":
            app.action_open_standard()
        elif bid == "open-scientific":
            app.action_open_scientific()
        elif bid == "open-converter":
            app.action_open_converter()
        elif bid == "open-history":
            app.action_show_history()
        elif bid == "open-settings":
            app.action_show_settings()
        elif bid.startswith("fav-"):
            app.open_tool(bid.removeprefix("fav-"))
        elif bid.startswith("tool-"):
            tool_id = bid.removeprefix("tool-")
            # Shift-like behavior not available on simple button press; use Ctrl+F via app action? Keep open.
            app.open_tool(tool_id)
