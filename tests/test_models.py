import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

from cursor_tool.models import load_faster_whisper


def test_load_faster_whisper_calls_library(monkeypatch):
    fake_segments = [MagicMock(text="hi"), MagicMock(text="there")]
    inst: dict[str, DummyModel] = {}

    class DummyModel:
        def __init__(self, name, device, compute_type):
            inst["obj"] = self
            self.called_with = (name, device, compute_type)
            self.language = None

        def transcribe(self, array, language):
            self.language = language
            return fake_segments, None

    fake_module = SimpleNamespace(WhisperModel=DummyModel)
    monkeypatch.setitem(sys.modules, "faster_whisper", fake_module)

    model = load_faster_whisper("tiny")
    result = model(b"\x00\x00")

    assert inst["obj"].called_with == ("tiny", "cpu", "int8")
    assert inst["obj"].language == "de"
    assert result == "hi there"
