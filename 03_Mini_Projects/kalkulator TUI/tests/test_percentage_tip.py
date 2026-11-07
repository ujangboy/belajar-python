from hitung.app import HitungApp
from hitung.engines.percentage_engine import percent_change, tax_amount


def test_percentage_engine_modes():
    assert percent_change(100, 120) == 20
    assert tax_amount(100, 11) == (11, 111)


async def test_percentage_discount(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("percentage")
        await pilot.pause()
        app.query_one("#pct-price").value = "100"
        app.query_one("#pct-percent").value = "10"
        await pilot.click("#pct-run")
        await pilot.pause()
        assert "90" in app.query_one("#pct-out").content


async def test_percentage_mode_switch(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("percentage")
        await pilot.pause()
        await pilot.click("#pct-mode-of")
        await pilot.pause()
        app.query_one("#pct-price").value = "200"
        app.query_one("#pct-percent").value = "10"
        await pilot.click("#pct-run")
        await pilot.pause()
        assert "20" in app.query_one("#pct-out").content


async def test_tip_calculation(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("tip")
        await pilot.pause()
        app.query_one("#tip-bill").value = "150"
        await pilot.click("#tip-15")
        app.query_one("#tip-people").value = "2"
        await pilot.click("#tip-calc")
        await pilot.pause()
        assert "22,5" in app.query_one("#tip-amount").content
        assert "86,25" in app.query_one("#tip-per-person").content
