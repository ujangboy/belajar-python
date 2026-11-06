from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from textual.widgets import Input, Select, Static, Switch

from hitung.app import HitungApp
from hitung.history import HistoryRecord
from hitung.screens.confirm import ConfirmScreen
from hitung.screens.help_screen import HelpScreen
from hitung.screens.history_screen import HistoryScreen
from hitung.screens.settings_screen import SettingsScreen
from hitung.storage import Storage


def shown(widget: Static) -> str:
    content = widget.content
    if hasattr(content, "plain"):
        return str(content.plain)
    return str(content)




async def open_standard(app: HitungApp, pilot) -> None:
    app.open_tool("standard")
    await pilot.pause()

async def commit(app: HitungApp, pilot, expression: str) -> None:
    app.query_one("#expr", Input).value = expression
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


@pytest.mark.asyncio
async def test_main_screen_default_state(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        assert shown(app.query_one("#result", Static)) == "0"
        assert app.focused is app.query_one("#expr", Input)
        assert app.query_one("#history-panel").display is True
        assert "Enter" in shown(app.query_one("#status", Static))
        assert app.records == []


@pytest.mark.asyncio
async def test_live_preview_and_commit(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)

        field = app.query_one("#expr", Input)
        field.value = "12 + 3 * (4 - 1)"
        await pilot.pause()

        result = app.query_one("#result", Static)
        assert shown(result) == "21"
        assert "-preview" in result.classes

        await pilot.press("enter")
        await pilot.pause()

        assert shown(result) == "21"
        assert "-preview" not in result.classes
        assert field.value == ""
        assert len(app.records) == 1
        assert (tmp_path / "history.jsonl").exists()

        stored = app.storage.load_history()
        assert len(stored) == 1
        assert stored[0].expression == "12 + 3 * (4 - 1)"
        assert stored[0].result == "21"


@pytest.mark.asyncio
async def test_error_is_shown_and_not_saved(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        await commit(app, pilot, "1/0")

        status = app.query_one("#status", Static)
        assert "nol" in shown(status).lower()
        assert "-error" in status.classes
        assert app.records == []
        assert not (tmp_path / "history.jsonl").exists()


@pytest.mark.asyncio
async def test_incomplete_expression_keeps_last_result(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        await commit(app, pilot, "2+3")
        assert shown(app.query_one("#result", Static)) == "5"

        app.query_one("#expr", Input).value = "2+"
        await pilot.pause()

        assert shown(app.query_one("#result", Static)) == "5"
        assert "-preview" not in app.query_one("#result", Static).classes


@pytest.mark.asyncio
async def test_escape_clears_entry(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        await commit(app, pilot, "5+5")

        field = app.query_one("#expr", Input)
        field.value = "7*7"
        await pilot.pause()
        assert shown(app.query_one("#result", Static)) == "49"

        await pilot.press("escape")
        await pilot.pause()

        assert field.value == ""
        assert shown(app.query_one("#result", Static)) == "10"
        assert "-preview" not in app.query_one("#result", Static).classes


@pytest.mark.asyncio
async def test_history_recall_with_arrows(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        await commit(app, pilot, "1+1")
        await commit(app, pilot, "2+2")

        field = app.query_one("#expr", Input)

        await pilot.press("up")
        await pilot.pause()
        assert field.value == "2+2"

        await pilot.press("up")
        await pilot.pause()
        assert field.value == "1+1"

        await pilot.press("up")
        await pilot.pause()
        assert field.value == "1+1"

        await pilot.press("down")
        await pilot.pause()
        assert field.value == "2+2"

        await pilot.press("down")
        await pilot.pause()
        assert field.value == ""


@pytest.mark.asyncio
async def test_copy_result(tmp_path: Path, monkeypatch) -> None:
    copied: list[str] = []
    monkeypatch.setattr(
        HitungApp,
        "copy_to_clipboard",
        lambda self, text: copied.append(text),
    )
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        app.query_one("#expr", Input).value = "6*7"
        await pilot.pause()
        await pilot.press("ctrl+y")
        await pilot.pause()

    assert copied == ["42"]


@pytest.mark.asyncio
async def test_ans_chains_previous_result(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        await commit(app, pilot, "2+3")

        field = app.query_one("#expr", Input)
        field.value = "ans*2"
        await pilot.pause()
        assert shown(app.query_one("#result", Static)) == "10"

        await pilot.press("enter")
        await pilot.pause()
        assert shown(app.query_one("#result", Static)) == "10"
        assert len(app.records) == 2
        assert app.records[-1].expression == "ans*2"


@pytest.mark.asyncio
async def test_history_screen_opens_and_closes(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        await commit(app, pilot, "1+1")

        await pilot.press("f2")
        await pilot.pause()
        assert isinstance(app.screen, HistoryScreen)
        entries = app.screen.query_one("#history-entries", Static)
        assert "1+1" in shown(entries)

        await pilot.press("escape")
        await pilot.pause()
        assert len(app.screen_stack) == 1


@pytest.mark.asyncio
async def test_history_clear_flow(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        await commit(app, pilot, "1+1")

        await pilot.press("f2")
        await pilot.pause()
        await pilot.click("#clear")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)

        await pilot.click("#confirm")
        await pilot.pause()

        assert len(app.screen_stack) == 1
        assert app.records == []
        assert app.storage.load_history() == []
        assert not (tmp_path / "history.jsonl").exists()


@pytest.mark.asyncio
async def test_help_screen_opens_and_closes(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        await pilot.press("f1")
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen)

        await pilot.press("escape")
        await pilot.pause()
        assert len(app.screen_stack) == 1


@pytest.mark.asyncio
async def test_settings_are_saved_and_used(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        await pilot.press("f3")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, SettingsScreen)

        screen.query_one("#precision", Input).value = "2"
        screen.query_one("#thousands", Switch).value = False
        await pilot.pause()
        await pilot.pause()
        screen.query_one("#save").focus()
        await pilot.press("enter")
        await pilot.pause()

        assert app.settings.precision == 2
        assert app.settings.thousands is False
        assert (tmp_path / "config.json").exists()
        await open_standard(app, pilot)

        app.query_one("#expr", Input).value = "1/3"
        await pilot.pause()
        assert shown(app.query_one("#result", Static)) == "0,33"


@pytest.mark.asyncio
async def test_settings_angle_mode(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        await pilot.press("f3")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, SettingsScreen)

        screen.query_one("#angle", Select).value = "rad"
        await pilot.pause()
        await pilot.pause()
        screen.query_one("#save").focus()
        await pilot.press("enter")
        await pilot.pause()

        assert app.settings.angle == "rad"
        await open_standard(app, pilot)

        app.query_one("#expr", Input).value = "sin(pi/2)"
        await pilot.pause()
        assert shown(app.query_one("#result", Static)) == "1"


@pytest.mark.asyncio
async def test_compact_mode_toggles_chrome(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        await pilot.press("f4")
        await pilot.pause()

        assert app.query_one("#topbar").display is False
        assert app.query_one("#history-panel").display is False
        assert app.query_one("#footer").display is False
        assert app.query_one("#compact-hint", Static).display is True

        await pilot.press("f4")
        await pilot.pause()

        assert app.query_one("#topbar").display is True
        assert app.query_one("#history-panel").display is True
        assert app.query_one("#footer").display is True
        assert app.query_one("#compact-hint", Static).display is False


@pytest.mark.asyncio
async def test_narrow_terminal_hides_side_panel(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        assert app.query_one("#body").display is True
        assert app.query_one("#history-panel").display is False


@pytest.mark.asyncio
async def test_too_small_terminal_and_resize(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(50, 15)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        assert app.query_one("#too-small", Static).display is True
        assert app.query_one("#body").display is False

        await pilot.resize_terminal(100, 30)
        await pilot.pause()
        assert app.query_one("#too-small", Static).display is False
        assert app.query_one("#body").display is True
        assert app.query_one("#history-panel").display is True

        await pilot.resize_terminal(50, 15)
        await pilot.pause()
        assert app.query_one("#too-small", Static).display is True
        assert app.query_one("#body").display is False


@pytest.mark.parametrize("size", [(60, 18), (100, 30), (140, 40)])
@pytest.mark.asyncio
async def test_layout_at_supported_sizes(
    tmp_path: Path,
    size: tuple[int, int],
) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        assert app.query_one("#body").display is True
        assert app.query_one("#too-small", Static).display is False

        card = app.query_one("#calc-card")
        assert card.region.width <= size[0]
        assert card.region.height <= size[1]


@pytest.mark.asyncio
async def test_topbar_counts_today(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await open_standard(app, pilot)
        assert "belum ada" in shown(app.query_one("#today", Static))

        await commit(app, pilot, "4*4")
        assert "1 hitungan" in shown(app.query_one("#today", Static))


def test_history_survives_restart(tmp_path: Path) -> None:
    # Tulis satu record langsung lewat storage, lalu pastikan app baru membacanya.
    storage = Storage(tmp_path)
    storage.append_history(
        HistoryRecord(
            at=datetime(2026, 10, 25, 9, 0).astimezone(),
            expression="3*3",
            result="9",
            value=9.0,
        )
    )

    reopened = HitungApp(data_dir=tmp_path)
    assert len(reopened.records) == 1
    assert reopened.records[0].expression == "3*3"
    assert reopened.records[0].result == "9"
