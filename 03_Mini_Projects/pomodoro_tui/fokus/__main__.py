"""Entry point `python -m fokus`."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from .app import main
except ModuleNotFoundError as error:
    if error.name != "textual":
        raise
    requirements = Path(__file__).resolve().parents[1] / "requirements.txt"
    raise SystemExit(
        "FOKUS butuh package 'textual', tetapi belum terpasang di Python ini.\n"
        "\n"
        "Cara termudah (Windows) - otomatis memakai Python + dependency yang ada:\n"
        "    run.cmd\n"
        "\n"
        "Atau pasang manual dengan Python yang sedang dipakai:\n"
        f'    "{sys.executable}" -m pip install -r "{requirements}"\n'
    ) from None

if __name__ == "__main__":
    main()
