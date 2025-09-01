import importlib
import sys
import types
from pathlib import Path


import pytest


@pytest.fixture
def recorder_module(monkeypatch):
    dummy_sd = types.SimpleNamespace()

    class DummyStream:
        def __init__(self, *args, **kwargs):
            self.callback = kwargs["callback"]
            self.started = False

        def start(self):
            self.started = True
            self.callback(b"abc", None, None, None)

        def stop(self):
            self.started = False

        def close(self):
            pass

    dummy_sd.InputStream = DummyStream

    dummy_keyboard = types.SimpleNamespace()
    callbacks: dict[str, types.FunctionType] = {}
    params: dict[str, bool] = {}

    def add_hotkey(key, cb, suppress=False, trigger_on_release=False):
        params["suppress"] = suppress
        params["trigger_on_release"] = trigger_on_release
        callbacks["toggle"] = cb

    def on_press_key(key, cb, suppress=False):
        callbacks["press"] = cb

    def on_release_key(key, cb, suppress=False):
        callbacks["release"] = cb

    dummy_keyboard.add_hotkey = add_hotkey
    dummy_keyboard.on_press_key = on_press_key
    dummy_keyboard.on_release_key = on_release_key

    monkeypatch.setitem(sys.modules, "sounddevice", dummy_sd)
    monkeypatch.setitem(sys.modules, "keyboard", dummy_keyboard)
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    if "cursor_tool.recorder" in sys.modules:
        del sys.modules["cursor_tool.recorder"]
    module = importlib.import_module("cursor_tool.recorder")
    return module, callbacks, params


def test_start_and_stop_recording(recorder_module):
    module, _, _ = recorder_module
    module.start_recording()
    assert module.recorder.is_recording is True
    assert module.recorder.queue.get() == b"abc"
    module.stop_recording()
    assert module.recorder.is_recording is False


def test_hotkey_callbacks(recorder_module):
    module, callbacks, params = recorder_module
    module.register_hotkeys("ctrl+alt+r", "shift+s")
    assert params["suppress"] is True
    assert params["trigger_on_release"] is True

    callbacks["toggle"]()
    assert module.recorder.is_recording is True
    callbacks["toggle"]()
    assert module.recorder.is_recording is False

    callbacks["press"](None)
    assert module.recorder.is_recording is True
    callbacks["release"](None)
    assert module.recorder.is_recording is False


def test_pynput_fallback(monkeypatch):
    callbacks: dict[str, types.FunctionType] = {}

    class DummyListener:
        def __init__(self, on_press=None, on_release=None):
            callbacks["press"] = on_press
            callbacks["release"] = on_release

        def start(self):
            pass

    class DummyKeyboard(types.SimpleNamespace):
        class KeyCode:
            @staticmethod
            def from_char(c):
                return c

        Listener = DummyListener

    fake_pynput = types.ModuleType("pynput")
    fake_pynput.keyboard = DummyKeyboard

    monkeypatch.setitem(sys.modules, "pynput", fake_pynput)
    monkeypatch.setitem(sys.modules, "keyboard", None)

    class DummyStream:
        def __init__(self, *a, **k):
            pass

        def start(self):
            pass

        def stop(self):
            pass

        def close(self):
            pass

    monkeypatch.setitem(sys.modules, "sounddevice", types.SimpleNamespace(InputStream=DummyStream))
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    if "cursor_tool.recorder" in sys.modules:
        del sys.modules["cursor_tool.recorder"]
    module = importlib.import_module("cursor_tool.recorder")

    module.register_hotkeys("a", "b")
    callbacks["press"]("a")
    assert module.recorder.is_recording is True
    callbacks["release"]("a")
    callbacks["press"]("a")
    assert module.recorder.is_recording is False
    callbacks["release"]("a")

    callbacks["press"]("b")
    assert module.recorder.is_recording is True
    callbacks["release"]("b")
    assert module.recorder.is_recording is False

