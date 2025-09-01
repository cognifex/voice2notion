from io import StringIO
import types

import pytest

from cursor_tool import cli


def test_prompt_hotkey_normalizes(monkeypatch):
    monkeypatch.setattr(cli, "keyboard", None)
    monkeypatch.setattr("builtins.input", lambda prompt="": "strg+y")
    assert cli.prompt_hotkey("Toggle hotkey", "ctrl+a") == "ctrl+y"


def test_prompt_hotkey_reprompts_invalid(monkeypatch):
    monkeypatch.setattr(cli, "keyboard", None)
    inputs = iter(["ctrl+shift", "ctrl+h"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    assert cli.prompt_hotkey("Toggle hotkey", "ctrl+a") == "ctrl+h"


def test_prompt_hotkey_with_keyboard(monkeypatch, capsys):
    hotkeys = iter(["ctrl+shift", "ctrl+h"])
    dummy_keyboard = types.SimpleNamespace(read_hotkey=lambda suppress=True: next(hotkeys))
    monkeypatch.setattr(cli, "keyboard", dummy_keyboard)
    result = cli.prompt_hotkey("Toggle hotkey", "ctrl+a")
    assert result == "ctrl+h"
    out = capsys.readouterr().out
    assert "Please include a non-modifier key" in out


def test_configure_reads_values(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "keyboard", None)
    stdin = StringIO("ctrl+t\nctrl+h\nfast\nprecise\n4\nde\n")
    monkeypatch.setattr("builtins.input", lambda prompt="": stdin.readline().rstrip("\n"))
    cfg = cli.configure(path=tmp_path / "cfg.json")
    assert cfg.fast_model == "fast"
    assert cfg.precise_model == "precise"
    assert cfg.chunk_seconds == 4.0
    assert cfg.language == "de"


def test_run_prints_status(monkeypatch, capsys):
    cfg = cli.Config(
        toggle_key="ctrl+t",
        hold_key="ctrl+h",
        fast_model="fast",
        precise_model="precise",
        chunk_seconds=5.0,
        language="de",
    )
    monkeypatch.setattr(cli.Config, "load", lambda path=None: cfg)
    monkeypatch.setattr(cli, "register_hotkeys", lambda t, h: None)

    def fake_loader(name, *, language):
        return lambda _: f"{name}-{language}"

    monkeypatch.setattr(cli, "load_faster_whisper", fake_loader)
    monkeypatch.setattr(cli, "transcribe_from_recorder", lambda rec, transcriber: "result")
    called = {}
    monkeypatch.setattr(cli.indicator, "show", lambda: called.setdefault("show", True))
    text = cli.run()
    assert text == "result"
    assert called["show"] is True
    out = capsys.readouterr().out
    assert "Loading models" in out
    assert "Press ctrl+t" in out
    assert "result" in out

