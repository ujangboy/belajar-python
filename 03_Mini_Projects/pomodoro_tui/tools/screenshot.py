"""Dev tool: generate screenshot SVG ke docs/ untuk README."""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from fokus.app import FokusApp
from fokus.config import Settings
from fokus.storage import SessionRecord, Storage
from fokus.timer import Phase

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"


class FakeClock:
    def __init__(self, start: float = 1_000.0) -> None:
        self.value = start

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def seed_sessions(data_dir: Path) -> None:
    storage = Storage(data_dir)
    now = datetime.now().astimezone().replace(microsecond=0)
    pattern = (25, 50, 25, 0, 75, 25, 50)
    for offset, minutes in enumerate(pattern):
        if minutes == 0:
            continue
        started = now - timedelta(days=6 - offset, hours=2)
        ended = started + timedelta(minutes=minutes)
        storage.append_session(
            SessionRecord(
                started_at=started,
                ended_at=ended,
                phase="focus",
                planned_seconds=minutes * 60,
                actual_seconds=minutes * 60,
                completed=True,
            )
        )


async def capture(
    name: str,
    actions=None,
    *,
    seed_data: bool = False,
    size: tuple[int, int] = (80, 24),
) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp)
        if seed_data:
            seed_sessions(data_dir)

        clock = FakeClock()
        app = FokusApp(data_dir=data_dir, clock=clock)
        async with app.run_test(size=size) as pilot:
            await pilot.pause()
            if actions is not None:
                await actions(app, pilot, clock)
                await pilot.pause()

            OUT.mkdir(exist_ok=True)
            path = OUT / f"{name}.svg"
            path.write_text(app.export_screenshot(), encoding="utf-8")
            print(f"wrote {path}")


async def main() -> None:
    await capture("main")

    async def running(app, pilot, clock):
        await pilot.press("space")
        clock.advance(725)
        app._tick()

    await capture("running", running)

    async def paused(app, pilot, clock):
        await pilot.press("space")
        clock.advance(540)
        app._tick()
        await pilot.press("space")

    await capture("paused", paused)

    async def stats(app, pilot, clock):
        await pilot.press("t")

    await capture("stats", stats, seed_data=True)

    async def settings(app, pilot, clock):
        await pilot.press("c")

    await capture("settings", settings)

    async def help_screen(app, pilot, clock):
        await pilot.press("question_mark")

    await capture("help", help_screen)

    async def confirm(app, pilot, clock):
        await pilot.press("space")
        await pilot.press("q")

    await capture("confirm", confirm)

    async def zen(app, pilot, clock):
        await pilot.press("z")

    await capture("zen", zen)

    async def short_break(app, pilot, clock):
        app.timer.update_settings(
            Settings(focus_minutes=1, sound=False),
            apply_current=True,
        )
        await pilot.press("space")
        clock.advance(60)
        app._tick()
        clock.advance(65)
        app._tick()

    await capture("short_break", short_break, seed_data=True)

    async def long_break(app, pilot, clock):
        app.timer.update_settings(
            Settings(focus_minutes=1, short_break_minutes=1, sound=False),
            apply_current=True,
        )
        for _ in range(4):
            timer = app.timer
            timer.start()
            clock.advance(timer.remaining)
            app._tick()
            if timer.phase is Phase.SHORT_BREAK:
                timer.start()
                clock.advance(timer.remaining)
                app._tick()
        clock.advance(120)
        app._tick()

    await capture("long_break", long_break)

    await capture("small", None, size=(50, 15))


if __name__ == "__main__":
    asyncio.run(main())
