from textual.widgets import Select

from hitung.app import HitungApp


async def open_converter(pilot, app, category: str | None = None) -> None:
    app.open_tool("converter")
    await pilot.pause()
    if category is not None:
        await pilot.click(f"#tab-{category}")
        await pilot.pause()


async def press(pilot, *keys: str) -> None:
    for key in keys:
        await pilot.click(f"#conv-{key}")
        await pilot.pause()


async def test_temperature_conversion(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await open_converter(pilot, app, "temperature")
        await press(pilot, "key-1", "key-0", "key-0", "key-equals")
        assert "212" in app.query_one("#conv-result").content


async def test_focus_navigation(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await open_converter(pilot, app)
        await pilot.click("#conv-key-up")
        await pilot.pause()
        assert app.query_one("#conv-from").has_focus
        await pilot.click("#conv-key-down")
        await pilot.pause()
        assert app.query_one("#conv-to").has_focus


async def test_swap_and_history(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await open_converter(pilot, app, "temperature")
        await press(pilot, "key-1", "key-0", "key-0", "key-equals")

        assert app.records[-1].category == "converter:temperature"

        await pilot.click("#conv-swap")
        await pilot.pause()
        assert app.query_one("#conv-from-unit", Select).value == "f"
        assert "100" in app.query_one("#conv-result").content


async def test_iec_data_units(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await open_converter(pilot, app, "data")
        app.query_one("#conv-from-unit", Select).value = "KiB"
        app.query_one("#conv-to-unit", Select).value = "B"
        await pilot.pause()
        await press(pilot, "key-1")
        assert "1.024" in app.query_one("#conv-result").content
