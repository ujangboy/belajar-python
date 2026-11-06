"""Palet dan tema Textual untuk HITUNG."""

from __future__ import annotations

from textual.theme import Theme

ACCENTS = {
    "mint": "#6FD3A8",
    "blue": "#8AB4F8",
    "amber": "#F0C674",
    "rose": "#F28FAD",
}


def build_theme(*, mode: str = "dark", accent: str = "mint") -> Theme:
    primary = ACCENTS.get(accent, ACCENTS["mint"])
    dark = mode != "light"
    if dark:
        fg, bg, surface, panel, border, muted = "#E6EDF3", "#12151C", "#1A202B", "#161C26", "#2F3A4A", "#93A1B3"
    else:
        fg, bg, surface, panel, border, muted = "#1B2430", "#F4F7FB", "#FFFFFF", "#EEF3F8", "#C8D3E1", "#5C6B7A"
    secondary = "#4F8CFF" if dark else "#2F6FEB"
    name = f"hitung-{mode}-{accent}"
    return Theme(
        name=name,
        primary=primary,
        secondary=secondary,
        accent=primary,
        warning="#F0C674" if dark else "#B7791F",
        error="#FF7A6B" if dark else "#C53030",
        success="#A6DA7A" if dark else "#2F855A",
        foreground=fg,
        background=bg,
        surface=surface,
        panel=panel,
        dark=dark,
        variables={"border": border, "muted": muted, "preview": secondary},
    )


HITUNG_THEME = build_theme(mode="dark", accent="mint")
# Compatibility exports for existing Rich/Textual styling helpers.
PRIMARY = ACCENTS["mint"]
SECONDARY = "#8AB4F8"
WARNING = "#F0C674"
ERROR = "#FF7A6B"
SUCCESS = "#A6DA7A"
TEXT = "#E6EDF3"
MUTED = "#93A1B3"
BACKGROUND = "#12151C"
SURFACE = "#1A202B"
PANEL = "#161C26"
BORDER = "#2F3A4A"
