from __future__ import annotations

from datetime import datetime, timezone

import pytest

from fokus.config import Settings
from fokus.timer import Phase, PomodoroTimer, State


class FakeClock:
    def __init__(self, start: float = 1_000.0) -> None:
        self.value = start

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def fixed_now() -> datetime:
    return datetime(2026, 10, 19, 9, 0, tzinfo=timezone.utc)


def make_timer(**settings_kwargs) -> tuple[PomodoroTimer, FakeClock]:
    clock = FakeClock()
    timer = PomodoroTimer(
        Settings(**settings_kwargs),
        clock=clock,
        now=fixed_now,
    )
    return timer, clock


def finish_current(timer: PomodoroTimer, clock: FakeClock):
    timer.start()
    clock.advance(timer.remaining)
    transition = timer.tick()
    assert transition is not None
    return transition


def test_initial_state() -> None:
    timer, _ = make_timer()
    assert timer.phase is Phase.FOCUS
    assert timer.state is State.IDLE
    assert timer.display_time == "25:00"
    assert timer.remaining == 25 * 60
    assert timer.progress == 0.0


def test_start_tick_pause_resume() -> None:
    timer, clock = make_timer()

    timer.start()
    assert timer.state is State.RUNNING

    clock.advance(60)
    assert timer.tick() is None
    assert timer.display_time == "24:00"
    assert timer.progress == pytest.approx(1 / 25)

    timer.pause()
    assert timer.state is State.PAUSED
    frozen = timer.remaining

    clock.advance(120)
    assert timer.tick() is None
    assert timer.remaining == frozen

    timer.start()
    clock.advance(10)
    assert timer.tick() is None
    assert timer.remaining == frozen - 10


def test_focus_completion_moves_to_short_break() -> None:
    timer, clock = make_timer()
    transition = finish_current(timer, clock)

    assert transition.completed is True
    assert transition.phase is Phase.FOCUS
    assert transition.next_phase is Phase.SHORT_BREAK
    assert transition.actual_seconds == 25 * 60
    assert timer.phase is Phase.SHORT_BREAK
    assert timer.state is State.IDLE
    assert timer.completed_focus_in_cycle == 1
    assert timer.display_time == "05:00"


def test_four_focus_sessions_trigger_long_break() -> None:
    timer, clock = make_timer()

    for index in range(4):
        finish_current(timer, clock)
        if index < 3:
            assert timer.phase is Phase.SHORT_BREAK
            finish_current(timer, clock)
            assert timer.phase is Phase.FOCUS
        else:
            assert timer.phase is Phase.LONG_BREAK
            assert timer.completed_focus_in_cycle == 4

    finish_current(timer, clock)
    assert timer.phase is Phase.FOCUS
    assert timer.completed_focus_in_cycle == 0


def test_skip_focus_does_not_count_as_completed() -> None:
    timer, clock = make_timer()
    timer.start()
    clock.advance(60)

    transition = timer.skip()
    assert transition.completed is False
    assert transition.phase is Phase.FOCUS
    assert transition.next_phase is Phase.SHORT_BREAK
    assert transition.actual_seconds == 60
    assert timer.completed_focus_in_cycle == 0
    assert timer.phase is Phase.SHORT_BREAK
    assert timer.state is State.IDLE


def test_skip_long_break_resets_cycle() -> None:
    timer, clock = make_timer()
    for index in range(4):
        finish_current(timer, clock)
        if index < 3:
            finish_current(timer, clock)

    assert timer.phase is Phase.LONG_BREAK
    timer.skip()
    assert timer.phase is Phase.FOCUS
    assert timer.completed_focus_in_cycle == 0


def test_reset_returns_to_full_duration() -> None:
    timer, clock = make_timer()
    timer.start()
    clock.advance(100)
    timer.tick()
    timer.reset()

    assert timer.state is State.IDLE
    assert timer.phase is Phase.FOCUS
    assert timer.remaining == 25 * 60
    assert timer.display_time == "25:00"
    assert timer.started_at is None


def test_update_settings_idle_applies_immediately() -> None:
    timer, _ = make_timer()
    timer.update_settings(Settings(focus_minutes=50), apply_current=True)

    assert timer.remaining == 50 * 60
    assert timer.display_time == "50:00"


def test_update_settings_paused_keeps_current_phase() -> None:
    timer, clock = make_timer()
    timer.start()
    clock.advance(60)
    timer.tick()
    timer.pause()

    timer.update_settings(Settings(focus_minutes=50), apply_current=False)
    assert timer.remaining == 24 * 60

    finish_current(timer, clock)
    assert timer.phase is Phase.SHORT_BREAK


def test_short_break_can_be_skipped() -> None:
    timer, clock = make_timer()
    finish_current(timer, clock)
    assert timer.phase is Phase.SHORT_BREAK

    transition = timer.skip()
    assert transition.phase is Phase.SHORT_BREAK
    assert transition.next_phase is Phase.FOCUS
    assert timer.phase is Phase.FOCUS
