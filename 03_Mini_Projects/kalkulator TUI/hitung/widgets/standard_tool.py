"""Layar kalkulator standar (pembungkus perilaku HITUNG v1)."""

from __future__ import annotations

from datetime import date, datetime

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Footer, Input, Static

from ..engine import CalcError, evaluate
from ..format import format_number
from ..history import HistoryRecord, recall_expressions, today_count
from ..widgets.calc_card import CalcCard
from ..widgets.display import CalculatorDisplay
from ..widgets.history_panel import HistoryPanel
from ..widgets.topbar import TopBar

MIN_WIDTH = 60
MIN_HEIGHT = 18
SIDE_PANEL_MIN_WIDTH = 86


class StandardTool(Vertical):
    """Tool kalkulator standar yang kompatibel dengan perilaku lama."""

    DEFAULT_CSS = """
    StandardTool { height: 1fr; layout: vertical; }
    """

    BINDINGS = [
        Binding("escape", "clear_entry", "Bersihkan", key_display="Esc", show=False),
        Binding("up", "recall_previous", show=False),
        Binding("down", "recall_next", show=False),
        Binding("ctrl+y", "copy_result", "Salin", show=False),
        Binding("f2", "show_history", "Riwayat", key_display="F2", show=False),
        Binding("f3", "show_settings", "Atur", key_display="F3", show=False),
        Binding("f4", "toggle_compact", "Ringkas", key_display="F4", show=False),
        Binding("f1", "show_help", "Bantuan", show=False, key_display="F1"),
    ]

    compact = reactive(False, init=False)

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self._recall: list[str] = []
        self._recall_index: int | None = None
        self._pending_input: str | None = None

    @property
    def host(self):
        return self.app

    def compose(self) -> ComposeResult:
        yield TopBar(id="topbar")
        with Container(id="body"):
            yield CalcCard(id="calc-card")
            yield HistoryPanel(id="history-panel")
        # Display tombol baru sudah ada; sampai Task 4 mengganti CalcCard,
        # ia disembunyikan agar tampilan v1 tidak berubah.
        yield CalculatorDisplay(id="calc-display")
        yield Static("Terminal terlalu kecil — minimal 60 × 18", id="too-small")
        yield Static(
            "F4 keluar mode ringkas · Esc bersihkan · F1 bantuan · Ctrl+H dashboard",
            id="compact-hint",
        )
        yield Footer(compact=True, id="footer", show_command_palette=False)

    def on_mount(self) -> None:
        self.rebuild_recall()
        self.refresh_history_panel()
        self.refresh_today()
        self.update_size()
        self.refresh_preview()
        self.query_one("#expr", Input).focus()
        self.set_interval(30.0, self.refresh_today)

    def on_resize(self, event) -> None:
        self.update_size(event.size)

    def _modal_open(self) -> bool:
        return len(self.app.screen_stack) > 1

    def _format(self, value: float) -> str:
        s = self.host.settings
        return format_number(
            value,
            precision=s.precision,
            thousands=s.thousands,
            number_format=getattr(s, "number_format", "id"),
        )

    def _input(self) -> Input:
        return self.query_one("#expr", Input)

    def _card(self) -> CalcCard | None:
        try:
            return self.query_one(CalcCard)
        except NoMatches:
            return None

    def _default_hint(self) -> str:
        if self.host.last_result is None:
            return "Ketik ekspresi lalu Enter · F1 bantuan · Ctrl+H dashboard"
        return "Enter hitung · ↑ ekspresi sebelumnya · Esc bersihkan · Ctrl+H dashboard"

    def update_size(self, size=None) -> None:
        try:
            body = self.query_one("#body")
            topbar = self.query_one("#topbar")
            panel = self.query_one("#history-panel")
            footer = self.query_one("#footer")
            too_small = self.query_one("#too-small", Static)
            compact_hint = self.query_one("#compact-hint", Static)
        except NoMatches:
            return
        size = size or self.size
        is_small = size.width < MIN_WIDTH or size.height < MIN_HEIGHT
        show_panel = not self.compact and size.width >= SIDE_PANEL_MIN_WIDTH
        body.display = not is_small
        too_small.display = is_small
        topbar.display = not is_small and not self.compact
        panel.display = not is_small and show_panel
        footer.display = not is_small and not self.compact
        compact_hint.display = not is_small and self.compact

    def rebuild_recall(self) -> None:
        self._recall = recall_expressions(self.host.records)
        self._recall_index = None

    def refresh_history_panel(self) -> None:
        try:
            panel = self.query_one(HistoryPanel)
        except NoMatches:
            return
        panel.update_view(self.host.records)

    def refresh_today(self) -> None:
        try:
            topbar = self.query_one(TopBar)
        except NoMatches:
            return
        topbar.update_today(today_count(self.host.records, date.today()))

    def refresh_preview(self) -> None:
        card = self._card()
        if card is None:
            return
        raw = self._input().value.strip()
        if not raw:
            card.show_result(self.host.last_result or "0")
            card.show_status(self._default_hint())
            return
        try:
            value = evaluate(raw, angle=self.host.settings.angle, ans=self.host.ans)
        except CalcError:
            card.show_result(self.host.last_result or "0")
            card.show_status(self._default_hint())
            return
        card.show_result(self._format(value), preview=True)
        card.show_status("Enter untuk menyimpan hasil ini")

    def on_input_changed(self, event: Input.Changed) -> None:
        if self._pending_input is not None and event.value == self._pending_input:
            self._pending_input = None
            return
        self._pending_input = None
        self._recall_index = None
        self.refresh_preview()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.calculate()

    def calculate(self) -> None:
        if self._modal_open():
            return
        card = self._card()
        if card is None:
            return
        expression = self._input().value.strip()
        if not expression:
            card.show_status("Ekspresi masih kosong — ketik angka dulu", error=True)
            return
        try:
            value = evaluate(expression, angle=self.host.settings.angle, ans=self.host.ans)
        except CalcError as error:
            card.show_status(str(error), error=True)
            if self.host.settings.sound:
                self.app.bell()
            return
        formatted = self._format(value)
        record = HistoryRecord(
            at=datetime.now().astimezone(),
            expression=expression,
            result=formatted,
            value=value,
            category="standard",
        )
        try:
            self.host.storage.append_history(record)
        except OSError as error:
            self.app.log.error(f"Gagal menyimpan riwayat: {error}")
            self.app.notify(
                "Hasil dihitung, tetapi gagal disimpan ke disk.",
                title="Penyimpanan gagal",
                severity="error",
                timeout=8,
            )
        self.host.records.append(record)
        self.host.ans = value
        self.host.last_expression = expression
        self.host.last_result = formatted
        self.rebuild_recall()
        self.refresh_history_panel()
        self.refresh_today()
        card.show_last(expression, formatted)
        card.show_result(formatted)
        card.show_status("Tersimpan ke riwayat · Esc bersihkan · Ctrl+H dashboard")
        self._set_input("")
        if self.host.settings.sound:
            self.app.bell()
        self._input().focus()
        # Dashboard recent refresh is best-effort; avoid blocking calculator flow.
        # (UI can refresh when dashboard is opened.)

    def _set_input(self, value: str) -> None:
        field = self._input()
        if field.value == value:
            self._pending_input = None
            try:
                field.cursor_position = len(value)
            except Exception:
                pass
            return
        self._pending_input = value
        field.value = value
        try:
            field.cursor_position = len(value)
        except Exception:
            pass

    def action_calculate(self) -> None:
        self.calculate()

    def action_clear_entry(self) -> None:
        if self._modal_open():
            return
        self._set_input("")
        self._recall_index = None
        self.refresh_preview()
        self._input().focus()

    def action_recall_previous(self) -> None:
        if self._modal_open():
            return
        if not self._recall:
            self.app.notify("Belum ada riwayat untuk dipanggil.", timeout=2)
            return
        if self._recall_index is None:
            index = 0
        elif self._recall_index < len(self._recall) - 1:
            index = self._recall_index + 1
        else:
            return
        self._recall_index = index
        self._set_input(self._recall[index])
        self.refresh_preview()

    def action_recall_next(self) -> None:
        if self._modal_open() or self._recall_index is None:
            return
        if self._recall_index == 0:
            self._recall_index = None
            self._set_input("")
        else:
            self._recall_index -= 1
            self._set_input(self._recall[self._recall_index])
        self.refresh_preview()

    def action_copy_result(self) -> None:
        if self._modal_open():
            return
        raw = self._input().value.strip()
        text: str | None = None
        if raw:
            try:
                text = self._format(evaluate(raw, angle=self.host.settings.angle, ans=self.host.ans))
            except CalcError:
                text = None
        if text is None:
            text = self.host.last_result
        if text is None:
            self.app.notify("Belum ada hasil untuk disalin.", timeout=2)
            return
        self.app.copy_to_clipboard(text)
        self.app.notify(f"Disalin: {text}", timeout=2)

    def action_show_history(self) -> None:
        self.app.action_show_history()

    def action_show_settings(self) -> None:
        self.app.action_show_settings()

    def action_show_help(self) -> None:
        self.app.action_show_help()

    def action_toggle_compact(self) -> None:
        if self._modal_open():
            return
        self.compact = not self.compact
        self.update_size()
