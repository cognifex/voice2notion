import importlib
import queue
import sys
from pathlib import Path

import pytest


def test_run_registers_hotkeys_and_returns_precise_text(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    cli = importlib.import_module("cursor_tool.cli")
    from cursor_tool import recorder

    cfg = cli.Config(toggle_key="t", hold_key="h")
    monkeypatch.setattr(cli.Config, "load", classmethod(lambda cls: cfg))

    calls = {}

    def fake_register(toggle, hold):
        calls["toggle"] = toggle
        calls["hold"] = hold

    monkeypatch.setattr(cli, "register_hotkeys", fake_register)

    typed: list[str] = []
    monkeypatch.setattr(cli, "insert_text", lambda text: typed.append(text))

    recorder.queue = queue.Queue()
    recorder.queue.put(b"data")
    recorder.queue.put(None)

    fast_model = lambda chunk: "FAST"
    precise_model = lambda chunk: "PRECISE"

    result = cli.run(fast_model, precise_model)

    assert calls == {"toggle": "t", "hold": "h"}
    assert typed == ["FAST"]
    assert result == "PRECISE"


def test_configure_prompts_and_saves(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    cli = importlib.import_module("cursor_tool.cli")

    responses = iter(["T", "H", "tiny", "base", "2.0"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    path = tmp_path / "cfg.json"

    cfg = cli.configure(path)

    assert cfg.toggle_key == "T"
    assert cfg.hold_key == "H"
    assert cfg.fast_model == "tiny"
    assert cfg.precise_model == "base"
    assert cfg.chunk_seconds == 2.0
    assert cli.Config.load(path) == cfg
