from hitung.app import HitungApp


async def test_dashboard_quick_access(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("dashboard")
        await pilot.pause()
        assert app.query_one("#quick-scientific")
        await pilot.click("#quick-scientific")
        await pilot.pause()
        assert app._active_tool == "scientific"
