"""Glue code that connects a Recorder with a DoubleTranscriber."""

from __future__ import annotations

from .recorder import Recorder
from .transcriber import DoubleTranscriber


def _queue_iter(recorder: Recorder):
    """Yield audio chunks from ``recorder`` until a ``None`` sentinel is seen."""

    while True:
        chunk = recorder.queue.get()
        if chunk is None:
            break
        yield chunk


def transcribe_from_recorder(recorder: Recorder, transcriber: DoubleTranscriber) -> str:
    """Drain ``recorder``'s queue into ``transcriber`` and return the final text."""

    return transcriber.transcribe_chunks(_queue_iter(recorder))
