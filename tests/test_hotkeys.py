from cursor_tool.hotkeys import normalize_hotkey, is_modifier_combo


def test_normalize_hotkey_aliases():
    assert normalize_hotkey("q+strg+umschalt") == "q+ctrl+shift"
    assert normalize_hotkey("ALT+Q") == "alt+q"


def test_normalize_hotkey_strips_punctuation():
    assert normalize_hotkey("'+strg+umschalt") == "ctrl+shift"
    assert normalize_hotkey("`+ALT") == "alt"


def test_is_modifier_combo():
    assert is_modifier_combo("ctrl+shift") is True
    assert is_modifier_combo("ctrl+q") is False
