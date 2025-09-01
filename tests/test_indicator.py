import importlib
import sys
import types
from pathlib import Path

import pytest


@pytest.fixture
def indicator_module(monkeypatch):
    beeps = []

    def beep(freq, dur):
        beeps.append((freq, dur))

    dummy_winsound = types.SimpleNamespace(Beep=beep)
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

        def wm_attributes(self, *_ , **__):
            pass

        def mainloop(self):
            pass

        def quit(self):
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

        def itemconfig(self, *_ , **__):
            pass

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

    monkeypatch.setitem(sys.modules, "winsound", dummy_winsound)
    monkeypatch.setitem(sys.modules, "tkinter", dummy_tk)
    monkeypatch.setattr("threading.Thread", DummyThread)
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    if "cursor_tool.indicator" in sys.modules:
        del sys.modules["cursor_tool.indicator"]
    module = importlib.import_module("cursor_tool.indicator")
    yield module, beeps
    if "cursor_tool.indicator" in sys.modules:
        del sys.modules["cursor_tool.indicator"]


def test_start_stop_indicator(indicator_module):
    module, beeps = indicator_module
    ind = module.RecordingIndicator()
    ind.start()
    assert ind.visible is True
    ind.stop()
    assert ind.visible is True
    assert beeps == []
