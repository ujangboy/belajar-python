"""Aplikasi Textual FOKUS."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.css.query import NoMatches
from textual.widgets import Footer, Static

from .config import Settings
from .screens.confirm import ConfirmScreen
from .screens.help_screen import HelpScreen
from .screens.settings_screen import SettingsScreen
from .screens.stats_screen import StatsScreen
from .stats import today_summary
from .storage import SessionRecord, Storage
from .theme import FOKUS_THEME
from .timer import Phase, PomodoroTimer, State, Transition
from .widgets.timer_card import TimerCard
from .widgets.topbar import TopBar


class FokusApp(App[None]):
    TITLE = "FOKUS"
    SUB_TITLE = "pomodoro untuk belajar"
    CSS_PATH = "fokus.tcss"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("space", "toggle_timer", "Mulai/Jeda", key_display="Space"),
        Binding("s", "skip_phase", "Lewati", show=False),
        Binding("r", "reset_timer", "Reset", show=False),
        Binding("z", "toggle_zen", "Zen"),
        Binding("t", "show_stats", "Statistik"),
        Binding("c", "show_settings", "Atur"),
        Binding(
            "question_mark",
            "show_help",
            "Bantuan",
            show=False,
            key_display="?",
        ),
        Binding("q", "quit_app", "Keluar"),
        Binding("escape", "escape_action", "Kembali", show=False),
    ]

    def __init__(
        self,
        data_dir: Path | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        super().__init__()
        self.storage = Storage(data_dir)
        self.settings = self.storage.load_settings()
        self.timer = PomodoroTimer(self.settings, clock=clock)

        self._today_date = date.today()
        self._today_sessions = 0
        self._today_minutes = 0
        self._zen = False
        self._last_title = ""

        self.register_theme(FOKUS_THEME)
        self.theme = "fokus"

    # ------------------------------------------------------------------ layout
    def compose(self) -> ComposeResult:
        yield TopBar(id="topbar")
        with Container(id="body"):
            yield TimerCard(id="timer-card")
        yield Static(
            "Terminal terlalu kecil — minimal 60 × 18",
            id="too-small",
        )
        yield Static("z keluar zen · space jeda", id="zen-hint")
        yield Footer(compact=True, id="footer", show_command_palette=False)

    def on_mount(self) -> None:
        self._load_today_stats()
        self._refresh_view(force=True)
        self._update_size()
        self.set_interval(1.0, self._tick)

    def on_resize(self, event) -> None:
        self._update_size(event.size)

    # ------------------------------------------------------------------- state
    def _modal_open(self) -> bool:
        return len(self.screen_stack) > 1

    def _load_today_stats(self) -> None:
        records = self.storage.load_sessions()
        self._today_sessions, self._today_minutes = today_summary(
            records,
            self._today_date,
        )

    def _refresh_today_if_needed(self) -> None:
        today = date.today()
        if today != self._today_date:
            self._today_date = today
            self._load_today_stats()

    def _phase_title(self) -> str:
        return self.timer.phase.label

    def _refresh_view(self, force: bool = False) -> None:
        try:
            card = self.query_one(TimerCard)
        except NoMatches:
            return

        try:
            card.update_view(
                self.timer,
                self._today_sessions,
                self._today_minutes,
            )
        except NoMatches:
            pass

        title = f"{self.timer.display_time} · {self._phase_title()}"
        if force or title != self._last_title:
            self.title = title
            self._last_title = title

    def _update_size(self, size=None) -> None:
        try:
            body = self.query_one("#body")
            topbar = self.query_one("#topbar")
            footer = self.query_one("#footer")
            too_small = self.query_one("#too-small", Static)
            zen_hint = self.query_one("#zen-hint", Static)
        except NoMatches:
            return

        size = size or self.size
        is_small = size.width < 60 or size.height < 18
        body.display = not is_small
        too_small.display = is_small
        topbar.display = not is_small and not self._zen
        footer.display = not is_small and not self._zen
        zen_hint.display = not is_small and self._zen

    # -------------------------------------------------------------------- tick
    def _tick(self) -> None:
        self._refresh_today_if_needed()
        transition = self.timer.tick()
        if transition is not None:
            self._handle_transition(transition)
        self._refresh_view()

    def _handle_transition(self, transition: Transition) -> None:
        if transition.completed and transition.phase is Phase.FOCUS:
            record = SessionRecord(
                started_at=transition.started_at or transition.ended_at,
                ended_at=transition.ended_at,
                phase=transition.phase.value,
                planned_seconds=transition.planned_seconds,
                actual_seconds=transition.actual_seconds,
                completed=True,
            )
            try:
                self.storage.append_session(record)
            except OSError as error:
                self.log.error(f"Gagal menyimpan sesi: {error}")
                self.notify(
                    "Sesi selesai, tetapi gagal disimpan ke disk.",
                    title="Penyimpanan gagal",
                    severity="error",
                    timeout=8,
                )
            else:
                self._today_sessions += 1
                self._today_minutes += transition.actual_seconds // 60

        if transition.completed:
            if self.settings.sound:
                self.bell()

            if transition.phase is Phase.FOCUS:
                if self.timer.phase is Phase.LONG_BREAK:
                    break_minutes = self.settings.long_break_minutes
                    break_label = "Istirahat panjang"
                else:
                    break_minutes = self.settings.short_break_minutes
                    break_label = "Istirahat pendek"
                self.notify(
                    f"{break_label} {break_minutes} menit. "
                    "Jauhkan mata dari layar sebentar.",
                    title="Sesi fokus selesai",
                    severity="information",
                    timeout=8,
                )
            else:
                self.notify(
                    "Istirahat selesai. Siap fokus lagi?",
                    title="Istirahat selesai",
                    severity="information",
                    timeout=6,
                )

        if (
            transition.completed
            and transition.next_phase.is_break
            and self.settings.auto_start_breaks
        ):
            self.timer.start()

    # ----------------------------------------------------------------- actions
    def action_toggle_timer(self) -> None:
        if self._modal_open():
            return
        self.timer.toggle()
        self._refresh_view(force=True)

    def action_skip_phase(self) -> None:
        if self._modal_open() or self.timer.state is State.IDLE:
            return
        if self.timer.phase is Phase.FOCUS:
            self.push_screen(
                ConfirmScreen(
                    "Lewati sesi fokus?",
                    "Sesi ini tidak akan dihitung sebagai sesi selesai.",
                    confirm_label="Lewati",
                    destructive=True,
                ),
                self._after_skip,
            )
        else:
            self._do_skip()

    def _after_skip(self, confirmed: bool | None) -> None:
        if confirmed:
            self._do_skip()

    def _do_skip(self) -> None:
        transition = self.timer.skip()
        self.notify(
            f"{transition.phase.label} dilewati.",
            timeout=2,
        )
        self._refresh_view(force=True)

    def action_reset_timer(self) -> None:
        if self._modal_open():
            return
        if self.timer.state is State.RUNNING:
            self.push_screen(
                ConfirmScreen(
                    "Reset timer?",
                    "Sisa waktu fase ini akan kembali ke durasi penuh.",
                    confirm_label="Reset",
                    destructive=True,
                ),
                self._after_reset,
            )
        else:
            self._do_reset()

    def _after_reset(self, confirmed: bool | None) -> None:
        if confirmed:
            self._do_reset()

    def _do_reset(self) -> None:
        self.timer.reset()
        self.notify("Timer di-reset.", timeout=2)
        self._refresh_view(force=True)

    def action_show_stats(self) -> None:
        if self._modal_open():
            return
        self.push_screen(StatsScreen())

    def action_show_settings(self) -> None:
        if self._modal_open():
            return
        if self.timer.state is State.RUNNING:
            self.notify(
                "Jeda timer dulu untuk membuka pengaturan.",
                severity="warning",
                timeout=3,
            )
            return
        self.push_screen(SettingsScreen(self.settings), self._settings_saved)

    def _settings_saved(self, result: Settings | None) -> None:
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
        self.timer.update_settings(
            result,
            apply_current=self.timer.state is State.IDLE,
        )
        self.notify("Pengaturan disimpan.", timeout=2)
        self._refresh_view(force=True)

    def action_show_help(self) -> None:
        if self._modal_open():
            return
        self.push_screen(HelpScreen())

    def action_toggle_zen(self) -> None:
        if self._modal_open():
            return
        self._zen = not self._zen
        if self._zen:
            self.screen.add_class("zen")
        else:
            self.screen.remove_class("zen")
        self._update_size()

    def action_escape_action(self) -> None:
        if self._zen and not self._modal_open():
            self.action_toggle_zen()

    def action_quit_app(self) -> None:
        if self._modal_open():
            return
        if self.timer.state is State.RUNNING:
            self.push_screen(
                ConfirmScreen(
                    "Keluar dari FOKUS?",
                    "Timer masih berjalan. Sesi yang belum selesai "
                    "tidak akan dihitung.",
                    confirm_label="Keluar",
                    destructive=True,
                ),
                self._after_quit,
            )
        else:
            self.exit()

    def _after_quit(self, confirmed: bool | None) -> None:
        if confirmed:
            self.exit()


def main() -> None:
    FokusApp().run()


if __name__ == "__main__":
    main()
