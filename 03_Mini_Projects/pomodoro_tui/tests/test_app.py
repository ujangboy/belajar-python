from __future__ import annotations

from pathlib import Path

import pytest
from textual.widgets import Digits, Input, Static, Switch

from fokus.app import FokusApp
from fokus.config import Settings
from fokus.screens.confirm import ConfirmScreen
from fokus.screens.settings_screen import SettingsScreen
from fokus.screens.stats_screen import StatsScreen
from fokus.timer import Phase, State
from fokus.widgets.timer_card import TimerCard


class FakeClock:
    def __init__(self, start: float = 1_000.0) -> None:
        self.value = start

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


@pytest.mark.asyncio
async def test_main_screen_starts_and_pauses(tmp_path: Path) -> None:
    clock = FakeClock()
    app = FokusApp(data_dir=tmp_path, clock=clock)

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        assert app.query_one(Digits).value == "25:00"
        assert app.timer.state is State.IDLE

        await pilot.press("space")
        await pilot.pause()
        assert app.timer.state is State.RUNNING

        clock.advance(60)
        app._tick()
        await pilot.pause()
        assert app.query_one(Digits).value == "24:00"

        await pilot.press("space")
        await pilot.pause()
        assert app.timer.state is State.PAUSED
        assert app.timer.display_time == "24:00"


@pytest.mark.asyncio
async def test_stats_settings_and_zen_open(tmp_path: Path) -> None:
    app = FokusApp(data_dir=tmp_path)

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()

        await pilot.press("t")
        await pilot.pause()
        assert isinstance(app.screen, StatsScreen)
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("c")
        await pilot.pause()
        assert isinstance(app.screen, SettingsScreen)
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("z")
        await pilot.pause()
        assert "zen" in app.screen.classes
        assert app.query_one("#topbar").display is False
        assert app.query_one("#zen-hint", Static).display is True

        await pilot.press("z")
        await pilot.pause()
        assert "zen" not in app.screen.classes
        assert app.query_one("#topbar").display is True


@pytest.mark.asyncio
async def test_save_settings(tmp_path: Path) -> None:
    app = FokusApp(data_dir=tmp_path)

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        await pilot.press("c")
        await pilot.pause()

        screen = app.screen
        assert isinstance(screen, SettingsScreen)
        screen.query_one("#focus", Input).value = "30"
        screen.query_one("#sound", Switch).value = False

        await pilot.click("#save")
        await pilot.pause()

        assert app.settings.focus_minutes == 30
        assert app.settings.sound is False
        assert app.timer.display_time == "30:00"
        assert (tmp_path / "config.json").exists()


@pytest.mark.asyncio
async def test_completed_focus_is_persisted(tmp_path: Path) -> None:
    clock = FakeClock()
    app = FokusApp(data_dir=tmp_path, clock=clock)

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        app.timer.update_settings(
            Settings(focus_minutes=1, sound=False),
            apply_current=True,
        )
        app.timer.start()
        clock.advance(60)
        app._tick()
        await pilot.pause()

        assert app.timer.phase is Phase.SHORT_BREAK
        assert app.timer.state is State.RUNNING
        records = app.storage.load_sessions()
        assert len(records) == 1
        assert records[0].phase == "focus"
        assert records[0].completed is True
        assert records[0].actual_seconds == 60


@pytest.mark.asyncio
async def test_too_small_terminal_shows_message(tmp_path: Path) -> None:
    app = FokusApp(data_dir=tmp_path)

    async with app.run_test(size=(50, 15)) as pilot:
        await pilot.pause()
        assert app.query_one("#too-small", Static).display is True
        assert app.query_one("#body").display is False


@pytest.mark.asyncio
async def test_skip_focus_needs_confirmation(tmp_path: Path) -> None:
    app = FokusApp(data_dir=tmp_path)

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        await pilot.press("space")
        await pilot.press("s")
        await pilot.pause()

        assert isinstance(app.screen, ConfirmScreen)
        assert app.timer.phase is Phase.FOCUS

        await pilot.click("#confirm")
        await pilot.pause()

        assert app.timer.phase is Phase.SHORT_BREAK
        assert app.timer.state is State.IDLE
        assert app.timer.completed_focus_in_cycle == 0


@pytest.mark.asyncio
async def test_settings_blocked_while_running(tmp_path: Path) -> None:
    app = FokusApp(data_dir=tmp_path)

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        await pilot.press("space")
        await pilot.press("c")
        await pilot.pause()

        assert not isinstance(app.screen, SettingsScreen)
        assert app.timer.state is State.RUNNING


@pytest.mark.asyncio
async def test_paused_settings_keep_remaining_time(tmp_path: Path) -> None:
    clock = FakeClock()
    app = FokusApp(data_dir=tmp_path, clock=clock)

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        await pilot.press("space")
        clock.advance(60)
        app._tick()
        await pilot.press("space")
        assert app.timer.state is State.PAUSED
        assert app.timer.display_time == "24:00"

        await pilot.press("c")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, SettingsScreen)
        screen.query_one("#focus", Input).value = "50"
        await pilot.click("#save")
        await pilot.pause()

        assert app.settings.focus_minutes == 50
        assert app.timer.display_time == "24:00"


@pytest.mark.parametrize("size", [(60, 18), (120, 30)])
@pytest.mark.asyncio
async def test_layout_at_supported_sizes(
    tmp_path: Path,
    size: tuple[int, int],
) -> None:
    app = FokusApp(data_dir=tmp_path)

    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        assert app.query_one("#body").display is True
        assert app.query_one("#too-small").display is False

        card = app.query_one(TimerCard)
        assert card.region.width <= size[0]
        assert card.region.height <= size[1]


@pytest.mark.asyncio
async def test_runtime_resize_toggles_small_message(tmp_path: Path) -> None:
    app = FokusApp(data_dir=tmp_path)

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        assert app.query_one("#body").display is True

        await pilot.resize_terminal(50, 15)
        await pilot.pause()
        assert app.query_one("#too-small", Static).display is True
        assert app.query_one("#body").display is False

        await pilot.resize_terminal(80, 24)
        await pilot.pause()
        assert app.query_one("#too-small", Static).display is False
        assert app.query_one("#body").display is True
