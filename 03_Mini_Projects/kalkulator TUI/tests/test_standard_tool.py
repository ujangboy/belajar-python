from hitung.app import HitungApp
from hitung.widgets.standard_tool import preprocess_percent


def test_contextual_percent_variants():
    assert preprocess_percent("200 + 10%", angle="deg", ans=0) == "200 + 20"
    assert preprocess_percent("200 - 10%", angle="deg", ans=0) == "200 - 20"
    assert preprocess_percent("10%", angle="deg", ans=0) == "10%"
    assert preprocess_percent("200 * 10%", angle="deg", ans=0) == "200 * 10%"


async def test_button_input_and_result(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        for key in ["key-1", "key-plus", "key-2", "key-equals"]:
            await pilot.click(f"#{key}")
            await pilot.pause()
        display = app.query_one("#calc-result")
        assert display.content == "3"
        assert len(app.records) == 1


async def test_contextual_percent(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        for key in [
            "key-2",
            "key-0",
            "key-0",
            "key-plus",
            "key-1",
            "key-0",
            "key-percent",
            "key-equals",
        ]:
            await pilot.click(f"#{key}")
            await pilot.pause()
        assert app.query_one("#calc-result").content == "220"


async def test_clear_and_backspace(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        for key in ["key-1", "key-2", "key-backspace"]:
            await pilot.click(f"#{key}")
            await pilot.pause()
        assert app.query_one("#calc-expression").content == "1"
        await pilot.click("#key-clear")
        await pilot.pause()
        assert app.query_one("#calc-expression").content == ""
