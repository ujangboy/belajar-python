"""Kartu utama: fase, digit timer, progres, titik sesi, dan hint."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Digits, Static

from ..theme import FOCUS, MUTED, TEXT, WARNING
from ..timer import Phase, PomodoroTimer, State
from .progress_line import ProgressLine


class TimerCard(Vertical):
    can_focus = False

    def compose(self) -> ComposeResult:
        yield Static("FOKUS · SESI 1/4", id="phase")
        yield Digits("25:00", id="digits")
        yield ProgressLine(id="progress")
        yield Static("", id="dots")
        yield Static("", id="today")
        yield Static("", id="hint")

    def on_mount(self) -> None:
        self.query_one("#digits", Digits).can_focus = False

    def update_view(
        self,
        timer: PomodoroTimer,
        today_sessions: int,
        today_minutes: int,
    ) -> None:
        configured = timer.settings.sessions_per_cycle

        if timer.phase is Phase.FOCUS:
            label = f"FOKUS · SESI {timer.current_session_number}/{configured}"
        else:
            label = timer.phase.label

        phase_text = Text(label, style="bold")
        if timer.state is State.PAUSED:
            phase_text.append("  ·  DIJEDA", style=f"bold {WARNING}")
        self.query_one("#phase", Static).update(phase_text)

        self.query_one("#digits", Digits).update(timer.display_time)
        self.query_one("#progress", ProgressLine).fraction = timer.progress

        dots = Text()
        for index in range(configured):
            if index < timer.completed_focus_in_cycle:
                dots.append("●", style=FOCUS)
            elif index == timer.completed_focus_in_cycle and timer.phase is Phase.FOCUS:
                dots.append("◉", style=FOCUS)
            else:
                dots.append("○", style=MUTED)
            if index < configured - 1:
                dots.append("  ")
        self.query_one("#dots", Static).update(dots)

        if today_sessions:
            today = Text(
                f"{today_sessions} sesi · {today_minutes} menit fokus hari ini",
                style=MUTED,
            )
        else:
            today = Text("Belum ada sesi hari ini", style=MUTED)
        self.query_one("#today", Static).update(today)

        hint = Text()
        hint.append("Space", style=f"bold {TEXT}")
        if timer.state is State.RUNNING:
            hint.append(" jeda    ", style=MUTED)
            hint.append("s", style=f"bold {TEXT}")
            hint.append(" lewati", style=MUTED)
        elif timer.state is State.PAUSED:
            hint.append(" lanjut    ", style=MUTED)
            hint.append("r", style=f"bold {TEXT}")
            hint.append(" reset", style=MUTED)
        elif timer.phase is Phase.FOCUS:
            hint.append(" mulai fokus", style=MUTED)
        else:
            hint.append(" mulai istirahat", style=MUTED)
        self.query_one("#hint", Static).update(hint)

        for class_name in ("-focus", "-short-break", "-long-break", "-paused"):
            self.remove_class(class_name)
        phase_class = {
            Phase.FOCUS: "-focus",
            Phase.SHORT_BREAK: "-short-break",
            Phase.LONG_BREAK: "-long-break",
        }[timer.phase]
        self.add_class(phase_class)
        if timer.state is State.PAUSED:
            self.add_class("-paused")
