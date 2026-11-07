"""Dashboard KALKULATOR PRO: akses cepat, riwayat, dan favorit."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Static

from ..history import recent_records
from ..navigation import default_tools, find_tool
from ..screens.confirm import ConfirmScreen

QUICK_ACCESS = (
    ("Scientific\nsin · cos · log", "scientific"),
    ("Unit Converter\n8 kategori", "converter"),
    ("Percentage\ndiskon · pajak", "percentage"),
    ("Tip\nbill · % · orang", "tip"),
)


class DashboardTool(Vertical):
    DEFAULT_CSS = """
    DashboardTool { height: 1fr; padding: 1 2; }
    """

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self._tools = [t for t in default_tools() if t.tool_id != "dashboard"]
        self._query = ""

    def compose(self) -> ComposeResult:
        yield Static("Welcome to KALKULATOR PRO", id="dash-title")
        yield Static("v2.0 — hitung, konversi, persentase, dan tip", id="dash-sub")
        yield Input(placeholder="Cari alat… (Ctrl+K)", id="dash-search")
        yield Static("AKSES CEPAT", classes="section")
        with Horizontal(id="quick-row"):
            for label, tool_id in QUICK_ACCESS:
                yield Button(label, id=f"quick-{tool_id}", classes="quick-card")
        with Horizontal(id="dash-columns"):
            with VerticalScroll(id="dash-main"):
                yield Static("SEMUA ALAT", classes="section")
                yield Vertical(id="tool-list", classes="tool-list")
            with Vertical(id="dash-side"):
                with Horizontal(id="recent-head"):
                    yield Static("RECENT CALCULATIONS", classes="section")
                    yield Button("Clear All", id="recent-clear", classes="mini")
                yield Static("Belum ada hitungan.", id="recent-box")
                yield Static("FAVORITE TOOLS", classes="section")
                yield Vertical(id="fav-box", classes="tool-list")

    def on_mount(self) -> None:
        self.refresh_tools()
        self.refresh_recent()
        self.refresh_favorites()

    # ---- daftar alat ----
    def refresh_tools(self) -> None:
        container = self.query_one("#tool-list", Vertical)
        container.remove_children()
        favs = set(getattr(self.app.settings, "favorites", []) or [])
        for tool in find_tool(self._tools, self._query):
            hint = f" · {tool.shortcut}" if tool.shortcut else ""
            star = "★" if tool.tool_id in favs else "☆"
            label = f"{star} {tool.title}{hint}\n{tool.description}"
            container.mount(
                Button(label, id=f"tool-{tool.tool_id}", classes="dash-item")
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "dash-search":
            self._query = event.value
            self.refresh_tools()

    # ---- riwayat ----
    def refresh_recent(self) -> None:
        try:
            box = self.query_one("#recent-box", Static)
        except Exception:
            return
        recent = recent_records(getattr(self.app, "records", []), 5)
        if not recent:
            box.update("Belum ada hitungan.")
            return
        lines = []
        for record in recent:
            expression = record.expression
            if len(expression) > 30:
                expression = expression[:30] + "…"
            lines.append(f"{expression} = {record.result}")
        box.update("\n".join(lines))

    def _confirm_clear(self) -> None:
        self.app.push_screen(
            ConfirmScreen(
                "Hapus semua riwayat?",
                "Semua riwayat hitungan di perangkat ini akan dihapus. "
                "Tindakan ini tidak bisa dibatalkan.",
                confirm_label="Hapus",
                destructive=True,
            ),
            self._after_clear,
        )

    def _after_clear(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        try:
            self.app.storage.clear_history()
        except OSError as error:
            self.notify(
                f"Gagal menghapus riwayat: {error}",
                title="Penyimpanan gagal",
                severity="error",
                timeout=8,
            )
            return
        self.app._after_history(True)
        self.refresh_recent()

    # ---- favorit ----
    def refresh_favorites(self) -> None:
        try:
            container = self.query_one("#fav-box", Vertical)
        except Exception:
            return
        container.remove_children()
        favorites = list(getattr(self.app.settings, "favorites", []) or [])
        by_id = {tool.tool_id: tool for tool in self._tools}
        shown = [by_id[favorite] for favorite in favorites if favorite in by_id]
        if not shown:
            container.mount(Static("Belum ada favorit. Tekan Ctrl+D di alat mana pun."))
            return
        for tool in shown[:8]:
            container.mount(
                Button(f"★ {tool.title}", id=f"fav-{tool.tool_id}", classes="dash-item")
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        app = self.app
        if button_id.startswith("quick-"):
            app.open_tool(button_id.removeprefix("quick-"))
        elif button_id == "recent-clear":
            self._confirm_clear()
        elif button_id.startswith("fav-"):
            app.open_tool(button_id.removeprefix("fav-"))
        elif button_id.startswith("tool-"):
            app.open_tool(button_id.removeprefix("tool-"))
