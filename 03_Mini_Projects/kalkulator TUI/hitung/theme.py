"""Palet dan tema Textual untuk HITUNG."""

from __future__ import annotations

from textual.theme import Theme

ACCENTS = {
    "blue": "#4C8DFF",
    "mint": "#6FD3A8",
    "amber": "#FF7A6B",
    "rose": "#F28FAD",
}


def build_theme(*, mode: str = "dark", accent: str = "blue") -> Theme:
    primary = ACCENTS.get(accent, ACCENTS["blue"])
    dark = mode != "light"
    if dark:
        fg, bg, surface, panel, border, muted = "#E6EDF3", "#0B0E14", "#111827", "#1A202B", "#2A3444", "#93A1B3"
    else:
        fg, bg, surface, panel, border, muted = "#1B2430", "#F4F7FB", "#FFFFFF", "#EEF3F8", "#C8D3E1", "#5C6B7A"
    secondary = "#4C8DFF" if dark else "#2F6FEB"
    name = f"hitung-{mode}-{accent}"
    return Theme(
        name=name,
        primary=primary,
        secondary=secondary,
        accent=primary,
        warning="#FF7A6B" if dark else "#B7791F",
        error="#FF7A6B" if dark else "#C53030",
        success="#6FD3A8" if dark else "#2F855A",
        foreground=fg,
        background=bg,
        surface=surface,
        panel=panel,
        dark=dark,
        variables={"border": border, "muted": muted, "preview": secondary},
    )


HITUNG_THEME = build_theme(mode="dark")
# Compatibility exports for existing Rich/Textual styling helpers.
PRIMARY = ACCENTS["blue"]
SECONDARY = "#4C8DFF"
WARNING = "#FF7A6B"
ERROR = "#FF7A6B"
SUCCESS = "#6FD3A8"
TEXT = "#E6EDF3"
MUTED = "#93A1B3"
BACKGROUND = "#0B0E14"
SURFACE = "#111827"
PANEL = "#1A202B"
BORDER = "#2A3444"
