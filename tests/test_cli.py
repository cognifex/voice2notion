import importlib
import sys
import types
from pathlib import Path

import pytest


def reload_cli(monkeypatch, keyboard_module):
    monkeypatch.setitem(sys.modules, "keyboard", keyboard_module)
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    if "cursor_tool.cli" in sys.modules:
        del sys.modules["cursor_tool.cli"]
    return importlib.import_module("cursor_tool.cli")


def test_prompt_hotkey_with_keyboard(monkeypatch, capsys):
    called: dict[str, bool] = {}

    def read_hotkey(*, suppress=False):
        called["read_hotkey"] = suppress
        return "ctrl+h"

    def read_key(*, suppress=False):
        called["read_key"] = suppress
        return "enter"

    dummy_keyboard = types.SimpleNamespace(
        read_hotkey=read_hotkey, read_key=read_key, _pressed_events=set()
    )
    cli_mod = reload_cli(monkeypatch, dummy_keyboard)
    result = cli_mod.prompt_hotkey("Toggle hotkey", "ctrl+a")
    assert result == "ctrl+h"
    assert called["read_hotkey"] is True
    assert called["read_key"] is True
    out = capsys.readouterr().out
    assert "Toggle hotkey [ctrl+a] (press hotkey, then ENTER to confirm):" in out
    assert "ctrl+h" in out


def test_prompt_hotkey_enter_keeps_current(monkeypatch, capsys):
    called = {}

    def read_hotkey(*, suppress=False):
        called["read_hotkey"] = suppress
        return "enter"

    def read_key(*, suppress=False):
        called["read_key"] = suppress
        return "enter"

    dummy_keyboard = types.SimpleNamespace(
        read_hotkey=read_hotkey, read_key=read_key, _pressed_events=set()
    )
    cli_mod = reload_cli(monkeypatch, dummy_keyboard)
    result = cli_mod.prompt_hotkey("Toggle hotkey", "ctrl+a")
    assert result == "ctrl+a"
    assert called["read_hotkey"] is True
    assert "read_key" not in called


def test_prompt_hotkey_fallback(monkeypatch):
    cli_mod = reload_cli(monkeypatch, None)
    monkeypatch.setattr("builtins.input", lambda _=None: "ctrl+y")
    assert cli_mod.prompt_hotkey("Toggle hotkey", "ctrl+a") == "ctrl+y"


def test_run_prints_ready_message(monkeypatch, capsys):
    dummy_keyboard = types.SimpleNamespace()
    cli_mod = reload_cli(monkeypatch, dummy_keyboard)
    cfg = types.SimpleNamespace(
        toggle_key="ctrl+y",
        hold_key="ctrl",
        fast_model="tiny",
        precise_model="base",
        chunk_seconds=5.0,
    )
    monkeypatch.setattr(cli_mod.Config, "load", staticmethod(lambda path=None: cfg))
    monkeypatch.setattr(cli_mod, "register_hotkeys", lambda *a, **k: None)
    monkeypatch.setattr(cli_mod, "load_faster_whisper", lambda name: lambda b: "text")
    monkeypatch.setattr(cli_mod, "transcribe_from_recorder", lambda r, t: "done")
    result = cli_mod.run()
    out = capsys.readouterr().out
    assert "Press ctrl+y to start/stop recording or hold ctrl." in out
    assert result == "done"
