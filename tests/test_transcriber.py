import itertools
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from cursor_tool.transcriber import chunk_indices, DoubleTranscriber


def test_chunk_indices_overlap():
    assert chunk_indices(10, 4, 1) == [(0, 4), (3, 7), (6, 10)]


def test_double_transcriber_invokes_models_and_callbacks():
    fast_calls = []
    precise_calls = []

    def fast_model(chunk: bytes) -> str:
        fast_calls.append(chunk)
        return f"fast-{chunk.decode()}"

    def precise_model(chunk: bytes) -> str:
        precise_calls.append(chunk)
        return f"precise-{chunk.decode()}"

    fast_emitted: list[str] = []
    precise_emitted: list[str] = []

    dt = DoubleTranscriber(
        fast_model,
        precise_model,
        on_fast=fast_emitted.append,
        on_precise=precise_emitted.append,
    )
    final = dt.transcribe_chunks([b"a", b"b"])

    assert fast_calls == [b"a", b"b"]
    assert precise_calls == [b"a", b"b"]
    assert fast_emitted == ["fast-a", "fast-b"]
    assert precise_emitted == ["precise-a", "precise-a precise-b"]
    assert final == "precise-a precise-b"
