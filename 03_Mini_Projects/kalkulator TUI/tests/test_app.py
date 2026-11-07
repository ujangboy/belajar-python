from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from textual.widgets import Input, Select, Switch

from hitung.app import HitungApp
from hitung.history import HistoryRecord
from hitung.screens.confirm import ConfirmScreen
from hitung.screens.help_screen import HelpScreen
from hitung.screens.history_screen import HistoryScreen
from hitung.screens.settings_screen import SettingsScreen
from hitung.storage import Storage


async def press(pilot, *keys: str) -> None:
    for key in keys:
        await pilot.click(f"#{key}")
        await pilot.pause()


async def press_expression(pilot, tokens: str) -> None:
    """Tekan tombol standar untuk ekspresi sederhana seperti '12+3*(4-1)'."""
    labels = {
        "+": "key-plus",
        "-": "key-minus",
        "*": "key-multiply",
        "/": "key-divide",
        "(": "key-lparen",
        ")": "key-rparen",
        ".": "key-dot",
    }
    for char in tokens:
        await press(pilot, labels.get(char, f"key-{char}"))


async def commit(pilot, tokens: str) -> None:
    await press_expression(pilot, tokens)
    await press(pilot, "key-equals")


@pytest.mark.asyncio
async def test_main_screen_default_state(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        assert app.query_one("#calc-result").content == "0"
        assert app.query_one("#calc-expression").content == ""
        assert app.query_one("#sidebar").display is True
        assert app.records == []


@pytest.mark.asyncio
async def test_live_preview_and_commit(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await press_expression(pilot, "12+3*(4-1)")

        result = app.query_one("#calc-result")
        assert result.content == "21"
        assert "-preview" in result.classes
        assert app.query_one("#calc-expression").content == "12+3*(4-1)"

        await press(pilot, "key-equals")

        assert result.content == "21"
        assert "-preview" not in result.classes
        assert app.query_one("#calc-expression").content == ""
        assert len(app.records) == 1
        assert (tmp_path / "history.jsonl").exists()

        stored = app.storage.load_history()
        assert len(stored) == 1
        assert stored[0].expression == "12+3*(4-1)"
        assert stored[0].result == "21"
        assert stored[0].category == "standard"


@pytest.mark.asyncio
async def test_error_is_shown_and_not_saved(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await commit(pilot, "1/0")

        status = app.query_one("#calc-status")
        assert "nol" in str(status.content).lower()
        assert "-error" in status.classes
        assert app.records == []
        assert not (tmp_path / "history.jsonl").exists()


@pytest.mark.asyncio
async def test_incomplete_expression_keeps_last_result(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await commit(pilot, "2+3")
        assert app.query_one("#calc-result").content == "5"

        await press(pilot, "key-2", "key-plus")

        assert app.query_one("#calc-result").content == "5"
        assert "-preview" not in app.query_one("#calc-result").classes


@pytest.mark.asyncio
async def test_escape_clears_entry(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await commit(pilot, "5+5")

        await press_expression(pilot, "7*7")
        assert app.query_one("#calc-result").content == "49"

        await pilot.press("escape")
        await pilot.pause()

        assert app.query_one("#calc-expression").content == ""
        assert app.query_one("#calc-result").content == "10"
        assert "-preview" not in app.query_one("#calc-result").classes


@pytest.mark.asyncio
async def test_history_recall_with_arrows(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await commit(pilot, "1+1")
        await commit(pilot, "2+2")

        expression = app.query_one("#calc-expression")

        await pilot.press("up")
        await pilot.pause()
        assert expression.content == "2+2"

        await pilot.press("up")
        await pilot.pause()
        assert expression.content == "1+1"

        await pilot.press("up")
        await pilot.pause()
        assert expression.content == "1+1"

        await pilot.press("down")
        await pilot.pause()
        assert expression.content == "2+2"

        await pilot.press("down")
        await pilot.pause()
        assert expression.content == ""


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
        await press_expression(pilot, "6*7")
        await pilot.press("ctrl+y")
        await pilot.pause()

    assert copied == ["42"]


@pytest.mark.asyncio
async def test_ans_chains_previous_result(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await commit(pilot, "2+3")
        await press(pilot, "key-ans", "key-multiply", "key-2")

        assert app.query_one("#calc-result").content == "10"

        await press(pilot, "key-equals")
        assert app.query_one("#calc-result").content == "10"
        assert len(app.records) == 2
        assert app.records[-1].expression == "ans*2"


@pytest.mark.asyncio
async def test_history_screen_opens_and_closes(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await commit(pilot, "1+1")

        await pilot.press("f2")
        await pilot.pause()
        assert isinstance(app.screen, HistoryScreen)
        entries = app.screen.query_one("#history-entries")
        assert "1+1" in str(entries.content)

        await pilot.press("escape")
        await pilot.pause()
        assert len(app.screen_stack) == 1


@pytest.mark.asyncio
async def test_history_clear_flow(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await commit(pilot, "1+1")

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

        await commit(pilot, "1/3")
        assert app.query_one("#calc-result").content == "0,33"


@pytest.mark.asyncio
async def test_settings_angle_mode(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
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


@pytest.mark.asyncio
async def test_narrow_terminal_hides_side_panel(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        assert app.query_one("#sidebar").display is False
        assert app.query_one("#calc-display").display is True


@pytest.mark.asyncio
async def test_too_small_terminal_and_resize(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(50, 15)) as pilot:
        await pilot.pause()
        assert app.query_one("#too-small").display is True
        assert app.query_one("#shell").display is False

        await pilot.resize_terminal(100, 30)
        await pilot.pause()
        assert app.query_one("#too-small").display is False
        assert app.query_one("#shell").display is True
        assert app.query_one("#sidebar").display is True

        await pilot.resize_terminal(50, 15)
        await pilot.pause()
        assert app.query_one("#too-small").display is True
        assert app.query_one("#shell").display is False


@pytest.mark.asyncio
async def test_sidebar_and_global_shortcuts(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        await pilot.click("#side-converter")
        await pilot.pause()
        assert app._active_tool == "converter"

        await pilot.click("#side-dashboard")
        await pilot.pause()
        assert app._active_tool == "dashboard"

        await pilot.press("ctrl+2")
        await pilot.pause()
        assert app._active_tool == "scientific"

        await pilot.press("ctrl+f")
        await pilot.pause()
        assert app._active_tool == "dashboard"


@pytest.mark.asyncio
async def test_sidebar_modal_tools(tmp_path: Path) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        await pilot.click("#side-history")
        await pilot.pause()
        assert isinstance(app.screen, HistoryScreen)
        await pilot.press("escape")
        await pilot.pause()

        await pilot.click("#side-settings")
        await pilot.pause()
        assert isinstance(app.screen, SettingsScreen)
        await pilot.press("escape")
        await pilot.pause()

        await pilot.click("#side-help")
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen)


@pytest.mark.parametrize("size", [(60, 18), (100, 30), (140, 40)])
@pytest.mark.asyncio
async def test_layout_at_supported_sizes(
    tmp_path: Path,
    size: tuple[int, int],
) -> None:
    app = HitungApp(data_dir=tmp_path)

    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        assert app.query_one("#shell").display is True
        assert app.query_one("#too-small").display is False

        tool = app.query_one("#tool-standard")
        assert tool.region.width <= size[0]
        assert tool.region.height <= size[1]


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
