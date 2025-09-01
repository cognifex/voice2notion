from io import StringIO

import pytest

from cursor_tool import cli


def test_prompt_hotkey_normalizes(monkeypatch):
    monkeypatch.setattr(cli.keyboard, "read_hotkey", lambda suppress=True: "strg+y")
    assert cli.prompt_hotkey("Toggle hotkey", "ctrl+a") == "ctrl+y"


def test_prompt_hotkey_reprompts_invalid(monkeypatch):
    inputs = iter(["ctrl+shift", "ctrl+h"])
    monkeypatch.setattr(cli.keyboard, "read_hotkey", lambda suppress=True: next(inputs))
    assert cli.prompt_hotkey("Toggle hotkey", "ctrl+a") == "ctrl+h"


def test_configure_reads_values(monkeypatch, tmp_path):
    hotkeys = iter(["ctrl+t", "ctrl+h"])
    monkeypatch.setattr(cli.keyboard, "read_hotkey", lambda suppress=True: next(hotkeys))
    stdin = StringIO("fast\nprecise\n4\nde\n")
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

