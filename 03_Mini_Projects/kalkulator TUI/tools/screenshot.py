"""Dev tool: generate screenshot SVG ke docs/ untuk README.

Jalankan dari folder project::

    python -m tools.screenshot
"""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from hitung.app import HitungApp
from hitung.history import HistoryRecord
from hitung.storage import Storage
from hitung.widgets.scientific_tool import ScientificTool
from hitung.widgets.standard_tool import StandardTool

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"

# (hari lalu, jam, ekspresi, hasil, nilai, kategori)
SEED = (
    (0, 9, "12 + 3 * (4 - 1)", "21", 21.0, "standard"),
    (0, 10, "sqrt(144) + 2^3", "20", 20.0, "scientific"),
    (0, 11, "200 + 10%", "220", 220.0, "standard"),
    (1, 15, "sin(30)", "0,5", 0.5, "scientific"),
    (2, 8, "100 °C -> °F", "212", 212.0, "converter:temperature"),
    (3, 20, "tip 150 · 15%", "22,5", 22.5, "tip"),
    (6, 7, "1/3", "0,333333", 1 / 3, "standard"),
)


def seed_history(data_dir: Path) -> None:
    storage = Storage(data_dir)
    now = datetime.now().astimezone().replace(microsecond=0)
    for days_ago, hour, expression, result, value, category in SEED:
        at = (now - timedelta(days=days_ago)).replace(
            hour=hour,
            minute=0,
            second=0,
        )
        storage.append_history(
            HistoryRecord(
                at=at,
                expression=expression,
                result=result,
                value=value,
                category=category,
            )
        )


async def click(pilot, *ids: str) -> None:
    for widget_id in ids:
        await pilot.click(f"#{widget_id}")
        await pilot.pause()


async def capture(
    name: str,
    actions=None,
    *,
    seed_data: bool = False,
    size: tuple[int, int] = (100, 30),
) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp)
        if seed_data:
            seed_history(data_dir)

        app = HitungApp(data_dir=data_dir)
        async with app.run_test(size=size) as pilot:
            await pilot.pause()
            if actions is not None:
                await actions(app, pilot)
                await pilot.pause()

            OUT.mkdir(exist_ok=True)
            path = OUT / f"{name}.svg"
            path.write_text(app.export_screenshot(), encoding="utf-8")
            print(f"wrote {path}")


async def main() -> None:
    async def preview(app, pilot):
        app.query_one("#tool-standard", StandardTool).set_expression("12 + 3 * (4 - 1)")

    await capture("main", preview)

    async def result(app, pilot):
        tool = app.query_one("#tool-standard", StandardTool)
        tool.set_expression("sqrt(144) + 2^3")
        tool.calculate()

    await capture("result", result)

    async def error(app, pilot):
        tool = app.query_one("#tool-standard", StandardTool)
        tool.set_expression("1 / 0")
        tool.calculate()

    await capture("error", error)

    async def dashboard(app, pilot):
        app.open_tool("dashboard")

    await capture("dashboard", dashboard, seed_data=True)

    async def scientific(app, pilot):
        app.open_tool("scientific")
        await pilot.pause()
        tool = app.query_one("#tool-scientific", ScientificTool)
        tool.set_expression("sin(30)")
        tool.calculate()

    await capture("scientific", scientific)

    async def converter(app, pilot):
        app.open_tool("converter")
        await pilot.pause()
        await pilot.click("#tab-temperature")
        await pilot.pause()
        await click(pilot, "conv-key-1", "conv-key-0", "conv-key-0")

    await capture("converter", converter)

    async def percentage(app, pilot):
        app.open_tool("percentage")
        await pilot.pause()
        app.query_one("#pct-price").value = "100"
        app.query_one("#pct-percent").value = "10"
        await pilot.click("#pct-run")

    await capture("percentage", percentage)

    async def tip(app, pilot):
        app.open_tool("tip")
        await pilot.pause()
        app.query_one("#tip-bill").value = "150"
        await pilot.click("#tip-15")
        app.query_one("#tip-people").value = "2"
        await pilot.click("#tip-calc")

    await capture("tip", tip)

    async def history(app, pilot):
        await pilot.press("f2")

    await capture("history", history, seed_data=True)

    async def settings(app, pilot):
        await pilot.press("f3")

    await capture("settings", settings)

    async def help_screen(app, pilot):
        await pilot.press("f1")

    await capture("help", help_screen)

    async def confirm(app, pilot):
        await pilot.press("f2")
        await pilot.pause()
        await pilot.click("#clear")

    await capture("confirm", confirm, seed_data=True)

    await capture("narrow", None, seed_data=True, size=(80, 24))
    await capture("small", None, size=(50, 15))


if __name__ == "__main__":
    asyncio.run(main())
