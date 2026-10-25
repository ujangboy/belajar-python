"""State machine Pomodoro yang tidak bergantung pada Textual."""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .config import Settings


class Phase(str, Enum):
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"

    @property
    def label(self) -> str:
        if self is Phase.FOCUS:
            return "FOKUS"
        if self is Phase.SHORT_BREAK:
            return "ISTIRAHAT PENDEK"
        return "ISTIRAHAT PANJANG"

    @property
    def is_break(self) -> bool:
        return self in (Phase.SHORT_BREAK, Phase.LONG_BREAK)


class State(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass(frozen=True, slots=True)
class Transition:
    """Hasil perpindahan fase, baik karena selesai maupun dilewati."""

    phase: Phase
    next_phase: Phase
    planned_seconds: int
    actual_seconds: int
    started_at: datetime | None
    ended_at: datetime
    completed: bool


class PomodoroTimer:
    """Timer berbasis deadline, sehingga tidak drift karena counting tick."""

    def __init__(
        self,
        settings: Settings,
        clock: Callable[[], float] | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.settings = settings
        self.clock = clock or time.monotonic
        self.now = now or (lambda: datetime.now().astimezone())

        self.phase = Phase.FOCUS
        self.state = State.IDLE
        self.completed_focus_in_cycle = 0
        self.phase_duration = float(self._duration_for(self.phase))
        self.remaining = self.phase_duration

        self._deadline: float | None = None
        self._started_at: datetime | None = None

    # ------------------------------------------------------------------ state
    def _duration_for(self, phase: Phase) -> int:
        if phase is Phase.FOCUS:
            return self.settings.focus_minutes * 60
        if phase is Phase.SHORT_BREAK:
            return self.settings.short_break_minutes * 60
        return self.settings.long_break_minutes * 60

    @property
    def duration(self) -> float:
        return self.phase_duration

    @property
    def display_time(self) -> str:
        total_seconds = max(0, math.ceil(self.remaining - 1e-9))
        return f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"

    @property
    def progress(self) -> float:
        if self.phase_duration <= 0:
            return 0.0
        value = 1.0 - (self.remaining / self.phase_duration)
        return min(1.0, max(0.0, value))

    @property
    def current_session_number(self) -> int:
        return min(
            self.completed_focus_in_cycle + 1,
            self.settings.sessions_per_cycle,
        )

    @property
    def started_at(self) -> datetime | None:
        return self._started_at

    # ---------------------------------------------------------------- controls
    def start(self) -> None:
        if self.state is State.RUNNING:
            return
        self._deadline = self.clock() + max(0.0, self.remaining)
        self.state = State.RUNNING
        if self._started_at is None:
            self._started_at = self.now()

    def pause(self) -> None:
        if self.state is not State.RUNNING or self._deadline is None:
            return
        self.remaining = max(0.0, self._deadline - self.clock())
        self._deadline = None
        self.state = State.PAUSED

    def toggle(self) -> None:
        if self.state is State.RUNNING:
            self.pause()
        else:
            self.start()

    def reset(self) -> None:
        self.state = State.IDLE
        self.phase_duration = float(self._duration_for(self.phase))
        self.remaining = self.phase_duration
        self._deadline = None
        self._started_at = None

    def skip(self) -> Transition:
        """Lewati fase saat ini tanpa menghitungnya sebagai selesai."""
        if self.state is State.RUNNING and self._deadline is not None:
            self.remaining = max(0.0, self._deadline - self.clock())
        elif self.state is State.IDLE:
            self.remaining = self.phase_duration

        completed_phase = self.phase
        planned_seconds = int(self.phase_duration)
        actual_seconds = max(0, planned_seconds - math.ceil(self.remaining))
        started_at = self._started_at
        ended_at = self.now()

        self._advance(completed_phase, completed=False)
        return Transition(
            phase=completed_phase,
            next_phase=self.phase,
            planned_seconds=planned_seconds,
            actual_seconds=actual_seconds,
            started_at=started_at,
            ended_at=ended_at,
            completed=False,
        )

    def tick(self, now: float | None = None) -> Transition | None:
        """Update sisa waktu. Kembalikan Transition hanya saat fase selesai."""
        if self.state is not State.RUNNING or self._deadline is None:
            return None

        current = self.clock() if now is None else now
        self.remaining = max(0.0, self._deadline - current)
        if self.remaining > 0:
            return None

        completed_phase = self.phase
        planned_seconds = int(self.phase_duration)
        actual_seconds = planned_seconds
        started_at = self._started_at
        ended_at = self.now()

        self._advance(completed_phase, completed=True)
        return Transition(
            phase=completed_phase,
            next_phase=self.phase,
            planned_seconds=planned_seconds,
            actual_seconds=actual_seconds,
            started_at=started_at,
            ended_at=ended_at,
            completed=True,
        )

    def update_settings(self, settings: Settings, apply_current: bool = False) -> None:
        """Pakai pengaturan baru. Fase berjalan tidak di-reset."""
        self.settings = settings
        if apply_current:
            self.reset()

    # --------------------------------------------------------------- internal
    def _advance(self, completed_phase: Phase, completed: bool) -> None:
        if completed_phase is Phase.FOCUS:
            if completed:
                self.completed_focus_in_cycle += 1
            if self.completed_focus_in_cycle >= self.settings.sessions_per_cycle:
                next_phase = Phase.LONG_BREAK
            else:
                next_phase = Phase.SHORT_BREAK
        elif completed_phase is Phase.SHORT_BREAK:
            next_phase = Phase.FOCUS
        else:
            self.completed_focus_in_cycle = 0
            next_phase = Phase.FOCUS

        self.phase = next_phase
        self.state = State.IDLE
        self.phase_duration = float(self._duration_for(next_phase))
        self.remaining = self.phase_duration
        self._deadline = None
        self._started_at = None
