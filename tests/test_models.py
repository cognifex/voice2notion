import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

from cursor_tool.models import load_faster_whisper


def test_load_faster_whisper_calls_library(monkeypatch):
    fake_segments = [MagicMock(text="hi"), MagicMock(text="there")]

    called = {}

    class DummyModel:
        def __init__(self, name, device, compute_type):
            self.called_with = (name, device, compute_type)

        def transcribe(self, array, language="en"):
            called["language"] = language
            return fake_segments, None

    dummy_cls = MagicMock(side_effect=DummyModel)
    fake_module = SimpleNamespace(WhisperModel=dummy_cls)
    monkeypatch.setitem(sys.modules, "faster_whisper", fake_module)

    model = load_faster_whisper("tiny", language="de")
    result = model(b"\x00\x00")

    dummy_cls.assert_called_with("tiny", device="cpu", compute_type="int8")
    assert result == "hi there"
    assert called["language"] == "de"
