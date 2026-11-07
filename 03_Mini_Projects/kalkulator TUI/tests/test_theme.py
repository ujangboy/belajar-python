from hitung.theme import build_theme, ACCENTS


def test_dark_theme_colors():
    theme = build_theme(mode="dark", accent="blue")
    assert theme.background == "#0B0E14"
    assert theme.surface == "#111827"
    assert theme.panel == "#1A202B"
    assert theme.primary == "#4C8DFF"
    assert theme.variables["border"] == "#2A3444"
    assert theme.variables["muted"] == "#93A1B3"


def test_accents():
    assert ACCENTS["blue"] == "#4C8DFF"
    assert ACCENTS["mint"] == "#6FD3A8"
    assert ACCENTS["amber"] == "#FF7A6B"


def test_default_accent_is_blue_and_bogus_falls_back():
    assert build_theme().primary == ACCENTS["blue"]
    assert build_theme(accent="bogus").primary == ACCENTS["blue"]
    assert build_theme(mode="light").background == "#F4F7FB"
