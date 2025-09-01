"""Utilities for double-pass speech transcription.

This module contains helper functions and a simple
``DoubleTranscriber`` class that demonstrates the architecture
for the transcribe-to-cursor tool. It focuses on two core ideas:

1. **Chunking with overlap** – Audio is processed in small chunks
   with a bit of overlap to allow a second, more accurate model to
   correct boundaries.
2. **Dual transcription** – A fast model provides immediate text
   while a slower, more precise model refines the final result.

The real application will later replace the model callables with
Whisper or derivatives. For unit tests we can inject light‑weight
functions that simply return strings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Sequence, Tuple

from .diff import merge_overlaps


def chunk_indices(length: float, chunk: float, overlap: float) -> List[Tuple[float, float]]:
    """Return start/end times for chunked processing.

    Parameters
    ----------
    length:
        Total length of the audio in seconds.
    chunk:
        Desired size of a single chunk in seconds.
    overlap:
        Amount of overlap between chunks in seconds.

    Examples
    --------
    >>> chunk_indices(10, 4, 1)
    [(0, 4), (3, 7), (6, 10)]
    """

    if chunk <= 0:
        raise ValueError("chunk must be positive")
    if overlap < 0 or overlap >= chunk:
        raise ValueError("overlap must be >= 0 and < chunk")

    segments: List[Tuple[float, float]] = []
    step = chunk - overlap
    start = 0.0
    while start < length:
        end = min(length, start + chunk)
        segments.append((round(start, 5), round(end, 5)))
        if end >= length:
            break
        start += step
    return segments


Callback = Callable[[str], None]
Model = Callable[[bytes], str]
Merger = Callable[[str, str], str]


@dataclass
class DoubleTranscriber:
    """Minimal orchestrator for a fast and a precise model.

    Parameters
    ----------
    fast_model:
        Callable that performs quick, low‑latency transcription.
    precise_model:
        Callable that performs accurate transcription on chunks.
    on_fast:
        Callback invoked with each fast transcription result. It can
        be used to display immediate feedback to the user.
    """

    fast_model: Model
    precise_model: Model
    on_fast: Callback | None = None
    on_precise: Callback | None = None
    merge: Merger = merge_overlaps
    _precise_text: str = field(default="", init=False)

    def _emit_fast(self, text: str) -> None:
        if self.on_fast:
            self.on_fast(text)

    def transcribe_chunks(self, chunks: Iterable[bytes]) -> str:
        """Transcribe an iterable of audio chunks.

        The fast model is executed immediately for each chunk and the
        result passed to ``on_fast``. The precise model is run after that
        and its output is appended to a buffer which is returned as the
        final text once all chunks have been processed.
        """

        self._precise_text = ""
        for chunk in chunks:
            fast_text = self.fast_model(chunk)
            self._emit_fast(fast_text)
            precise_chunk = self.precise_model(chunk)
            self._precise_text = self.merge(self._precise_text, precise_chunk)
            if self.on_precise:
                self.on_precise(self._precise_text)
        return self._precise_text
