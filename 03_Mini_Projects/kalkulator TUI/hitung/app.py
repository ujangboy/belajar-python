"""Aplikasi Textual HITUNG / Calculator Pro."""

from __future__ import annotations

from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.events import Resize
from textual.widgets import ContentSwitcher, Static

from .config import Settings
from .history import HistoryRecord
from .navigation import default_tools
from .screens.help_screen import HelpScreen
from .screens.history_screen import HistoryScreen
from .screens.search_screen import SearchScreen
from .screens.settings_screen import SettingsScreen
from .storage import Storage
from .theme import HITUNG_THEME, build_theme
from .widgets.converter_tool import ConverterTool
from .widgets.dashboard_tool import DashboardTool
from .widgets.data_tool import DataTool
from .widgets.date_tool import DateTool
from .widgets.electrical_tool import ElectricalTool
from .widgets.finance_tool import FinanceTool
from .widgets.math_tool import MathTool
from .widgets.percentage_tool import PercentageTool
from .widgets.tip_tool import TipTool
from .widgets.scientific_tool import ScientificTool
from .widgets.sidebar import Sidebar
from .widgets.standard_tool import StandardTool

# Di bawah lebar ini sidebar disembunyikan supaya kartu hitung tetap lega.
SIDEBAR_MIN_WIDTH = 90
MIN_WIDTH = 60
MIN_HEIGHT = 18


class HitungApp(App[None]):
    TITLE = "Calculator Pro"
    SUB_TITLE = "HITUNG"
    CSS_PATH = "hitung.tcss"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("ctrl+q", "quit_app", "Keluar", key_display="^Q", priority=True),
        Binding("ctrl+h", "go_dashboard", "Dashboard", key_display="^H", priority=True),
        Binding("ctrl+k", "focus_search", "Cari", key_display="^K", priority=True),
        Binding("ctrl+d", "toggle_favorite", "Favorit", key_display="^D", priority=True),
        Binding("ctrl+1", "open_standard", "Standar", key_display="^1", priority=True),
        Binding("ctrl+2", "open_scientific", "Ilmiah", key_display="^2", priority=True),
        Binding("ctrl+3", "open_converter", "Konverter", key_display="^3", priority=True),
        Binding("f1", "show_help", "Bantuan", show=False, key_display="F1"),
        Binding("f2", "show_history", "Riwayat", key_display="F2"),
        Binding("f3", "show_settings", "Atur", key_display="F3"),
        Binding("escape", "back_or_clear", "Kembali/Bersihkan", key_display="Esc"),
        Binding("up", "recall_previous", show=False),
        Binding("down", "recall_next", show=False),
        Binding("ctrl+y", "copy_result", show=False),
    ]

    def __init__(self, data_dir: Path | None = None) -> None:
        super().__init__()
        self.storage = Storage(data_dir)
        self.settings = self.storage.load_settings()
        self.records = self.storage.load_history()
        self.tools = default_tools()

        self.ans = 0.0
        self.last_expression: str | None = None
        self.last_result: str | None = None
        self._active_tool = "standard"

        self._theme_name = "hitung"
        self._apply_theme_settings(register=True)

    def _apply_theme_settings(self, *, register: bool = False) -> None:
        theme = build_theme(mode=getattr(self.settings, "theme", "dark"), accent=getattr(self.settings, "accent", "mint"))
        self._theme_name = theme.name
        if register or theme.name not in getattr(self, "available_themes", {}):
            self.register_theme(theme)
        self.theme = theme.name

    # ---- akses tool standar ----
    def _standard_tool(self) -> StandardTool | None:
        try:
            return self.query_one("#tool-standard", StandardTool)
        except NoMatches:
            return None

    # ---- layout ----
    def compose(self) -> ComposeResult:
        with Horizontal(id="shell"):
            yield Sidebar(id="sidebar")
            with ContentSwitcher(initial="tool-standard", id="tools"):
                yield DashboardTool(id="tool-dashboard")
                yield StandardTool(id="tool-standard")
                yield ScientificTool(id="tool-scientific")
                yield ConverterTool(id="tool-converter")
                yield PercentageTool(id="tool-percentage")
                yield TipTool(id="tool-tip")
                yield DateTool(id="tool-date")
                yield FinanceTool(id="tool-finance")
                yield MathTool(id="tool-math")
                yield DataTool(id="tool-data")
                yield ElectricalTool(id="tool-electrical")
        yield Static("Terminal terlalu kecil — minimal 60 × 18", id="too-small")

    def on_mount(self) -> None:
        self._sync_layout(self.size)
        self.open_tool("standard")

    @on(Resize)
    def _on_app_resize(self, event: Resize) -> None:
        self._sync_layout(event.size)

    def _sync_layout(self, size) -> None:
        self._sync_sidebar_width(size.width)
        fits = size.width >= MIN_WIDTH and size.height >= MIN_HEIGHT
        try:
            self.query_one("#shell").display = fits
            self.query_one("#too-small", Static).display = not fits
        except NoMatches:
            pass

    def _sync_sidebar_width(self, width: int) -> None:
        try:
            sidebar = self.query_one(Sidebar)
        except NoMatches:
            return
        sidebar.display = width >= SIDEBAR_MIN_WIDTH

    def _modal_open(self) -> bool:
        return len(self.screen_stack) > 1

    def open_tool(self, tool_id: str) -> None:
        valid = {f"tool-{t.tool_id}" for t in self.tools}
        valid.update(
            {
                "tool-standard",
                "tool-scientific",
                "tool-converter",
                "tool-percentage",
                "tool-date",
                "tool-finance",
                "tool-math",
                "tool-data",
                "tool-electrical",
            }
        )
        target = f"tool-{tool_id}" if not tool_id.startswith("tool-") else tool_id
        if target not in valid:
            target = "tool-standard"
        try:
            self.query_one("#tools", ContentSwitcher).current = target
        except NoMatches:
            return
        self._active_tool = target.removeprefix("tool-")
        try:
            self.query_one(Sidebar).set_active(self._active_tool)
        except NoMatches:
            pass
        if self._active_tool == "standard":
            tool = self._standard_tool()
            if tool:
                tool.refresh_display()
        if self._active_tool == "scientific":
            try:
                sci = self.query_one("#tool-scientific", ScientificTool)
                sci.refresh_display()
            except NoMatches:
                pass
        if self._active_tool == "converter":
            try:
                self.query_one("#tool-converter", ConverterTool).focus_default()
            except NoMatches:
                pass
        if self._active_tool == "dashboard":
            self.refresh_dashboard_recent()

    def refresh_dashboard_recent(self) -> None:
        try:
            dash = self.query_one("#tool-dashboard", DashboardTool)
        except NoMatches:
            return
        try:
            dash.refresh_recent()
        except Exception:
            pass

    # ---- global actions ----
    def action_quit_app(self) -> None:
        if self._modal_open():
            return
        self.exit()

    def action_go_dashboard(self) -> None:
        if self._modal_open():
            return
        self.open_tool("dashboard")

    def action_focus_search(self) -> None:
        if self._modal_open():
            return
        self.push_screen(SearchScreen(), self._after_search)

    def _after_search(self, tool_id: str | None) -> None:
        if tool_id:
            self.open_tool(tool_id)

    def action_toggle_favorite(self) -> None:
        if self._modal_open():
            return
        tool_id = getattr(self, "_active_tool", "standard")
        if tool_id in {"dashboard", ""}:
            self.notify("Buka alat dulu untuk menambah favorit.", timeout=2)
            return
        favs = list(getattr(self.settings, "favorites", []) or [])
        if tool_id in favs:
            favs = [f for f in favs if f != tool_id]
            msg = f"Dihapus dari favorit: {tool_id}"
        else:
            favs.append(tool_id)
            msg = f"Ditambah ke favorit: {tool_id}"
        self.settings = Settings(
            precision=self.settings.precision, thousands=self.settings.thousands, angle=self.settings.angle,
            sound=self.settings.sound, theme=self.settings.theme, accent=self.settings.accent,
            number_format=self.settings.number_format, history_limit=self.settings.history_limit, favorites=favs,
        )
        try:
            self.storage.save_settings(self.settings)
        except OSError:
            pass
        self.refresh_dashboard_recent()
        self.notify(msg, timeout=2)

    def action_open_standard(self) -> None:
        if self._modal_open():
            return
        self.open_tool("standard")

    def action_open_scientific(self) -> None:
        if self._modal_open():
            return
        self.open_tool("scientific")

    def action_open_converter(self) -> None:
        if self._modal_open():
            return
        self.open_tool("converter")

    def action_back_or_clear(self) -> None:
        if self._modal_open():
            return
        if self._active_tool == "standard":
            tool = self._standard_tool()
            if tool:
                tool.action_clear_entry()
            return
        if self._active_tool == "scientific":
            try:
                self.query_one("#tool-scientific", ScientificTool).action_clear_or_back()
            except NoMatches:
                self.open_tool("dashboard")
            return
        self.open_tool("dashboard")

    def action_clear_entry(self) -> None:
        if self._active_tool == "standard":
            tool = self._standard_tool()
            if tool:
                tool.action_clear_entry()
        elif not self._modal_open():
            self.open_tool("dashboard")

    def action_recall_previous(self) -> None:
        tool = self._standard_tool()
        if self._active_tool == "standard" and tool:
            tool.action_recall_previous()

    def action_recall_next(self) -> None:
        tool = self._standard_tool()
        if self._active_tool == "standard" and tool:
            tool.action_recall_next()

    def action_copy_result(self) -> None:
        tool = self._standard_tool()
        if self._active_tool == "standard" and tool:
            tool.action_copy_result()

    def action_calculate(self) -> None:
        tool = self._standard_tool()
        if self._active_tool == "standard" and tool:
            tool.calculate()

    def action_show_history(self) -> None:
        if self._modal_open():
            return
        self.push_screen(HistoryScreen(self.records), self._after_history)

    def _after_history(self, result) -> None:
        if result is True:
            self.records = []
            tool = self._standard_tool()
            if tool:
                tool.rebuild_recall()
                tool.refresh_display()
            self.notify("Riwayat dihapus.", timeout=2)
        elif hasattr(result, "expression") and hasattr(result, "category"):
            # Optional: history screens may return a record to reuse.
            tool = self._standard_tool()
            cat = getattr(result, "category", "standard") or "standard"
            if tool and cat in {"standard", "scientific"}:
                self.open_tool("standard" if cat == "standard" else "scientific")
                try:
                    if cat == "standard":
                        tool.set_expression(result.expression)
                    else:
                        sci = self.query_one("#tool-scientific", ScientificTool)
                        sci.set_expression(result.expression)
                except Exception:
                    pass
            self.notify("Ekspresi dimuat dari riwayat.", timeout=2)
        else:
            tool = self._standard_tool()
            if tool:
                tool.refresh_display()

    def action_show_settings(self) -> None:
        if self._modal_open():
            return
        self.push_screen(SettingsScreen(self.settings), self._after_settings)

    def _after_settings(self, result: Settings | None) -> None:
        if result is None:
            return
        try:
            self.storage.save_settings(result)
        except OSError as error:
            self.log.error(f"Gagal menyimpan pengaturan: {error}")
            self.notify(
                "Pengaturan dipakai, tetapi gagal disimpan ke disk.",
                title="Penyimpanan gagal",
                severity="error",
                timeout=8,
            )
        self.settings = result
        self._apply_theme_settings()
        tool = self._standard_tool()
        if tool:
            tool.refresh_display()
        try:
            sci = self.query_one("#tool-scientific", ScientificTool)
            sci.refresh_display()
        except Exception:
            pass
        self.notify("Pengaturan disimpan.", timeout=2)

    def action_show_help(self) -> None:
        if self._modal_open():
            return
        self.push_screen(HelpScreen())


def main() -> None:
    HitungApp().run()


if __name__ == "__main__":
    main()
