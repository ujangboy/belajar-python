"""Palet dan tema Textual untuk HITUNG (PRD v3.0 tokens)."""

from __future__ import annotations

from textual.theme import Theme

# Aksen dapat dipilih user; default selaras PRD Primary #4389F5.
ACCENTS = {
    "blue": "#4389F5",
    "mint": "#55D6A4",
    "amber": "#E9B96E",
    "rose": "#ED7777",
}


def build_theme(*, mode: str = "dark", accent: str = "blue") -> Theme:
    primary = ACCENTS.get(accent, ACCENTS["blue"])
    dark = mode != "light"
    if dark:
        # PRD v3.0 dark tokens (dipetakan ke variabel tema Textual).
        fg = "#E5ECF5"
        bg = "#0B0F16"
        surface = "#111927"
        panel = "#151C28"  # sidebar/surface nav
        border = "#29374A"
        muted = "#96A4B7"
        success = "#55D6A4"
        warning = "#E9B96E"
        error = "#ED7777"
        secondary = "#65A2FF"
    else:
        fg, bg, surface, panel, border, muted = "#1B2430", "#F4F7FB", "#FFFFFF", "#EEF3F8", "#C8D3E1", "#5C6B7A"
        success = "#2F855A"
        warning = "#B7791F"
        error = "#C53030"
        secondary = "#2F6FEB"
    name = f"hitung-{mode}-{accent}"
    hover = "#1D2A3C" if dark else "#E6EEF8"
    return Theme(
        name=name,
        primary=primary,
        secondary=secondary,
        accent=primary,
        warning=warning,
        error=error,
        success=success,
        foreground=fg,
        background=bg,
        surface=surface,
        panel=panel,
        dark=dark,
        variables={
            "border": border,
            "muted": muted,
            "text-muted": muted,
            "preview": secondary,
            "hover": hover,
            "sidebar": panel,
            "danger": error,
        },
    )


HITUNG_THEME = build_theme(mode="dark")
# Compatibility exports for existing Rich/Textual styling helpers.
PRIMARY = ACCENTS["blue"]
SECONDARY = "#65A2FF"
WARNING = "#E9B96E"
ERROR = "#ED7777"
SUCCESS = "#55D6A4"
TEXT = "#E5ECF5"
MUTED = "#96A4B7"
BACKGROUND = "#0B0F16"
SURFACE = "#111927"
PANEL = "#151C28"
BORDER = "#29374A"
