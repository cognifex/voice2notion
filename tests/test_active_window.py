import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from cursor_tool.active_window import is_text_field_focused
import cursor_tool.active_window as aw


def test_is_text_field_focused_true(monkeypatch):
    monkeypatch.setattr(aw, "_get_foreground_class", lambda: "Edit", raising=False)
    assert is_text_field_focused()


def test_is_text_field_focused_false(monkeypatch):
    monkeypatch.setattr(aw, "_get_foreground_class", lambda: "Button", raising=False)
    assert not is_text_field_focused()


def test_is_text_field_focused_browser(monkeypatch):
    monkeypatch.setattr(aw, "_get_foreground_class", lambda: "Chrome_WidgetWin_1", raising=False)
    assert is_text_field_focused()
