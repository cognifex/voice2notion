import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from cursor_tool.pipeline import transcribe_from_recorder
from cursor_tool.recorder import Recorder
from cursor_tool.transcriber import DoubleTranscriber


def test_transcribe_from_recorder_integration():
    r = Recorder()
    r.queue.put(b"a")
    r.queue.put(b"b")
    r.queue.put(None)

    fast, precise, emitted = [], [], []

    def fast_model(chunk: bytes) -> str:
        fast.append(chunk)
        return chunk.decode()

    def precise_model(chunk: bytes) -> str:
        precise.append(chunk)
        return chunk.decode().upper()

    dt = DoubleTranscriber(fast_model, precise_model, emitted.append)
    final = transcribe_from_recorder(r, dt)

    assert fast == [b"a", b"b"]
    assert precise == [b"a", b"b"]
    assert emitted == ["a", "b"]
    assert final == "A B"
