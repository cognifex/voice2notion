import importlib
import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import cursor_tool.typer as typer


def test_insert_text_uses_keyboard_write(monkeypatch):
    stub = types.SimpleNamespace(write=lambda text: stub.calls.append(text))
    stub.calls = []  # type: ignore[attr-defined]
    import cursor_tool.typer as typer

    monkeypatch.setattr(typer, "keyboard", stub, raising=False)
    monkeypatch.setattr(typer, "is_text_field_focused", lambda: True, raising=False)
    typer.insert_text("hello")
    assert stub.calls == ["hello"]


def test_insert_text_skips_when_no_focus(monkeypatch):
    stub = types.SimpleNamespace(write=lambda text: stub.calls.append(text))
    stub.calls = []  # type: ignore[attr-defined]
    import cursor_tool.typer as typer

    monkeypatch.setattr(typer, "keyboard", stub, raising=False)
    monkeypatch.setattr(typer, "is_text_field_focused", lambda: False, raising=False)
    typer.insert_text("ignored")
    assert stub.calls == []


def test_insert_text_pynput_fallback(monkeypatch):
    class DummyController:
        def __init__(self):
            self.calls = []

        def type(self, text):
            self.calls.append(text)

    dummy_controller = DummyController()
    dummy_keyboard = types.SimpleNamespace(Controller=lambda: dummy_controller)

    fake_pynput = types.ModuleType("pynput")
    fake_pynput.keyboard = dummy_keyboard

    import importlib, sys
    monkeypatch.setitem(sys.modules, "pynput", fake_pynput)
    monkeypatch.setitem(sys.modules, "keyboard", None)
    if "cursor_tool.typer" in sys.modules:
        typer = importlib.reload(sys.modules["cursor_tool.typer"])
    else:
        typer = importlib.import_module("cursor_tool.typer")
    monkeypatch.setattr(typer, "is_text_field_focused", lambda: True, raising=False)
    typer.insert_text("hi")
    assert dummy_controller.calls == ["hi"]
