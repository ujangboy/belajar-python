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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"

# (hari lalu, jam, ekspresi, hasil, nilai)
SEED = (
    (0, 9, "12 + 3 * (4 - 1)", "21", 21.0),
    (0, 10, "sqrt(144) + 2^3", "20", 20.0),
    (0, 11, "200 * 15%", "30", 30.0),
    (1, 15, "sin(30)", "0,5", 0.5),
    (2, 8, "2^10", "1.024", 1024.0),
    (3, 20, "ans * 2", "42", 42.0),
    (6, 7, "1/3", "0,333333", 1 / 3),
)


def seed_history(data_dir: Path) -> None:
    storage = Storage(data_dir)
    now = datetime.now().astimezone().replace(microsecond=0)
    for days_ago, hour, expression, result, value in SEED:
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
            )
        )


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
    await capture("main")

    async def typing(app, pilot):
        app.query_one("#expr").value = "12 + 3 * (4 - 1)"

    await capture("typing", typing)

    async def result(app, pilot):
        app.query_one("#expr").value = "sqrt(144) + 2^3"
        await pilot.pause()
        await pilot.press("enter")

    await capture("result", result)

    async def error(app, pilot):
        app.query_one("#expr").value = "1 / 0"
        await pilot.pause()
        await pilot.press("enter")

    await capture("error", error)

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

    async def compact(app, pilot):
        await pilot.press("f4")

    await capture("compact", compact, seed_data=True)

    await capture("narrow", None, seed_data=True, size=(80, 24))
    await capture("small", None, size=(50, 15))


if __name__ == "__main__":
    asyncio.run(main())
