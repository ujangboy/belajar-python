from hitung.app import HitungApp
from hitung.widgets.display import CalculatorDisplay
from hitung.widgets.keypad import SCIENTIFIC_KEYS, STANDARD_KEYS, ScientificKeypad


async def test_sidebar_opens_tool(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await pilot.click("#side-scientific")
        await pilot.pause()
        assert app._active_tool == "scientific"


async def test_display_updates(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        display = app.query_one(CalculatorDisplay)
        display.set_expression("12 + 3")
        display.set_result("15", preview=True)
        display.set_status("OK")
        display.set_angle("rad")
        assert display.query_one("#calc-expression").content == "12 + 3"
        assert "-preview" in display.query_one("#calc-result").classes
        assert display.query_one("#calc-result").content == "15"
        assert display.query_one("#calc-status").content == "OK"
        assert display.query_one("#calc-angle").content == "RAD"


def test_keypad_layouts():
    assert len(STANDARD_KEYS) == 24
    assert len(SCIENTIFIC_KEYS) == 35
    ids = [k[0] for k in SCIENTIFIC_KEYS]
    assert "key-equals" in ids and "key-clear" in ids and "key-swap" in ids
    std_ids = [k[0] for k in STANDARD_KEYS]
    assert "key-equals" in std_ids and "key-percent" in std_ids
