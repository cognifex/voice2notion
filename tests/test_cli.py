import importlib
import sys
import types
from pathlib import Path
from io import StringIO

import pytest


def reload_cli(monkeypatch, keyboard_module):
    monkeypatch.setitem(sys.modules, "keyboard", keyboard_module)
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    if "cursor_tool.cli" in sys.modules:
        del sys.modules["cursor_tool.cli"]
    return importlib.import_module("cursor_tool.cli")


def test_prompt_hotkey_with_keyboard(monkeypatch, capsys):
    dummy_keyboard = types.SimpleNamespace(read_hotkey=lambda suppress=False: "ctrl+h")
    cli_mod = reload_cli(monkeypatch, dummy_keyboard)
    result = cli_mod.prompt_hotkey("Toggle hotkey", "ctrl+a")
    assert result == "ctrl+h"
    out = capsys.readouterr().out
    assert "Toggle hotkey [ctrl+a]:" in out
    assert "ctrl+h" in out


def test_prompt_hotkey_fallback(monkeypatch):
    cli_mod = reload_cli(monkeypatch, None)
    monkeypatch.setattr("builtins.input", lambda _=None: "strg+y")
    assert cli_mod.prompt_hotkey("Toggle hotkey", "ctrl+a") == "ctrl+y"


def test_configure_consumes_trailing_enter(monkeypatch, tmp_path):
    hotkeys = iter(["ctrl+t", "ctrl+h"])
    dummy_keyboard = types.SimpleNamespace(read_hotkey=lambda suppress=False: next(hotkeys))
    cli_mod = reload_cli(monkeypatch, dummy_keyboard)

    stdin = StringIO("\nfast\nprecise\n4\n")
    monkeypatch.setattr(sys, "stdin", stdin)

    calls = {"n": 0}

    def fake_flush():
        if calls["n"] == 2:
            stdin.read(1)
        calls["n"] += 1

    monkeypatch.setattr(cli_mod, "_flush_stdin", fake_flush)

    cfg = cli_mod.configure(path=tmp_path / "cfg.json")

    assert cfg.fast_model == "fast"
    assert cfg.precise_model == "precise"
    assert cfg.chunk_seconds == 4.0


def test_run_prints_status(monkeypatch, capsys):
    cli_mod = reload_cli(monkeypatch, None)
    cfg = cli_mod.Config(
        toggle_key="ctrl+t",
        hold_key="ctrl+h",
        fast_model="fast",
        precise_model="precise",
        chunk_seconds=5.0,
    )
    monkeypatch.setattr(cli_mod.Config, "load", lambda path=None: cfg)
    monkeypatch.setattr(cli_mod, "register_hotkeys", lambda t, h: None)
    monkeypatch.setattr(cli_mod, "load_faster_whisper", lambda name: (lambda _: name))
    monkeypatch.setattr(
        cli_mod, "transcribe_from_recorder", lambda rec, transcriber: "result"
    )
    called = {}
    monkeypatch.setattr(cli_mod.indicator, "show", lambda: called.setdefault("show", True))
    text = cli_mod.run()
    assert text == "result"
    assert called["show"] is True
    out = capsys.readouterr().out
    assert "Loading models" in out
    assert "Press ctrl+t" in out
    assert "result" in out
