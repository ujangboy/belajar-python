from hitung.navigation import default_tools


def test_tool_ids():
    ids = [t.tool_id for t in default_tools()]
    assert ids == [
        "dashboard",
        "standard",
        "scientific",
        "converter",
        "percentage",
        "tip",
        "history",
        "favorites",
        "settings",
        "help",
    ]


def test_shortcuts():
    by_id = {t.tool_id: t for t in default_tools()}
    assert by_id["standard"].shortcut == "Ctrl+1"
    assert by_id["scientific"].shortcut == "Ctrl+2"
    assert by_id["converter"].shortcut == "Ctrl+3"
