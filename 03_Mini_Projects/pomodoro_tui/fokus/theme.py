"""Palet dan tema Textual untuk FOKUS."""

from textual.theme import Theme

FOCUS = "#FF7A6B"
SHORT_BREAK = "#5FD3C4"
LONG_BREAK = "#8AB4F8"
SUCCESS = "#A6DA7A"
WARNING = "#F0C674"
TEXT = "#E6EDF3"
MUTED = "#93A1B3"
BACKGROUND = "#12151C"
SURFACE = "#1A202B"
PANEL = "#161C26"
BORDER = "#2F3A4A"

FOKUS_THEME = Theme(
    name="fokus",
    primary=FOCUS,
    secondary=SHORT_BREAK,
    accent=LONG_BREAK,
    warning=WARNING,
    error=FOCUS,
    success=SUCCESS,
    foreground=TEXT,
    background=BACKGROUND,
    surface=SURFACE,
    panel=PANEL,
    dark=True,
    variables={
        "border": BORDER,
        "muted": MUTED,
        "focus": FOCUS,
        "break-short": SHORT_BREAK,
        "break-long": LONG_BREAK,
    },
)
