from hitung.app import HitungApp


async def click_keys(pilot, *keys: str) -> None:
    for key in keys:
        await pilot.click(f"#sci-{key}")
        await pilot.pause()


async def test_trig_and_angle_mode(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("scientific")
        await pilot.pause()
        await click_keys(pilot, "key-sin", "key-3", "key-0", "key-rparen", "key-equals")
        assert app.query_one("#sci-calc-result").content == "0,5"
        await pilot.click("#sci-key-angle")
        await pilot.pause()
        assert app.settings.angle == "rad"
        assert app.query_one("#sci-calc-angle").content == "RAD"


async def test_swap_expression_with_ans(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("scientific")
        await pilot.pause()
        await click_keys(pilot, "key-2", "key-plus", "key-3", "key-equals")
        await pilot.click("#sci-key-swap")
        await pilot.pause()
        assert app.query_one("#sci-calc-expression").content == "5"


async def test_power_sqrt_and_category(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("scientific")
        await pilot.pause()
        await click_keys(pilot, "key-3", "key-sq", "key-equals")
        assert app.query_one("#sci-calc-result").content == "9"
        assert app.records[-1].category == "scientific"

        await click_keys(pilot, "key-sqrt", "key-9", "key-rparen", "key-equals")
        assert app.query_one("#sci-calc-result").content == "3"


async def test_clear(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("scientific")
        await pilot.pause()
        await click_keys(pilot, "key-1", "key-2")
        await pilot.click("#sci-key-clear")
        await pilot.pause()
        assert app.query_one("#sci-calc-expression").content == ""
