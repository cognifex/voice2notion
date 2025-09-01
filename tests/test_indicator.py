import importlib
import sys
import types
from pathlib import Path

import pytest


@pytest.fixture
def indicator_module(monkeypatch):
    colors: list[str] = []

    dummy_tk = types.SimpleNamespace()

    class DummyRoot:
        def overrideredirect(self, _):
            pass

        def attributes(self, *_):
            pass

        def geometry(self, *_):
            pass

        def configure(self, *_ , **__):
            pass

        def mainloop(self):
            pass

        def after(self, _delay, func):
            func()

    class DummyCanvas:
        def __init__(self, *_, **__):
            pass

        def pack(self):
            pass

        def create_oval(self, *_, **__):
            return 1

        def itemconfig(self, _id, *, fill):
            colors.append(fill)

    dummy_tk.Tk = DummyRoot
    dummy_tk.Canvas = DummyCanvas

    class DummyThread:
        def __init__(self, target, daemon):
            self.target = target
            self.daemon = daemon
            self.started = False

        def start(self):
            self.started = True
            self.target()

    monkeypatch.setattr("threading.Thread", DummyThread)
    monkeypatch.setitem(sys.modules, "tkinter", dummy_tk)
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    if "cursor_tool.indicator" in sys.modules:
        del sys.modules["cursor_tool.indicator"]
    module = importlib.import_module("cursor_tool.indicator")
    yield module, colors
    if "cursor_tool.indicator" in sys.modules:
        del sys.modules["cursor_tool.indicator"]


def test_start_stop_indicator(indicator_module):
    module, colors = indicator_module
    ind = module.RecordingIndicator()
    ind.start()
    ind.stop()
    assert colors == ["green", "red"]
