"""Dev tool: ubah screenshot SVG Textual menjadi grid teks 80x24.

Dipakai untuk verifikasi layout tanpa membuka terminal sungguhan:

    python -m tools.svg_dump docs/main.svg
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree

COLUMN_WIDTH = 12.2
SVG = "{http://www.w3.org/2000/svg}"


def dump(path: Path) -> str:
    root = ElementTree.parse(path).getroot()
    lines: dict[int, list[tuple[int, str]]] = {}
    max_row = 0

    for text in root.iter(f"{SVG}text"):
        content = "".join(text.itertext()).replace("\n", "").strip()
        if not content:
            continue
        clip = text.get("clip-path", "")
        match = re.search(r"line-(\d+)", clip)
        if match is None:
            continue
        row = int(match.group(1))
        column = round(float(text.get("x", "0")) / COLUMN_WIDTH)
        lines.setdefault(row, []).append((column, content))
        max_row = max(max_row, row)

    output: list[str] = []
    for row in range(max_row + 1):
        cells = sorted(lines.get(row, []))
        line = ""
        for column, content in cells:
            if len(line) < column:
                line += " " * (column - len(line))
            line += content
        output.append(f"{row:02d}|{line.rstrip()}")
    return "\n".join(output)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    paths = [Path(arg) for arg in sys.argv[1:]]
    if not paths:
        paths = sorted(Path("docs").glob("*.svg"))
    for path in paths:
        print(f"=== {path.name} ===")
        print(dump(path))
        print()


if __name__ == "__main__":
    main()
