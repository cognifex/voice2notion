"""Helpers for loading Whisper models."""

from __future__ import annotations

from .transcriber import Model


def load_faster_whisper(name: str, device: str = "cpu", *, language: str = "de") -> Model:
    """Return a callable that transcribes audio with ``faster-whisper``.

    The returned function accepts raw PCM ``bytes`` and returns the
    concatenated transcription text. ``device`` can be ``"cpu"`` or
    ``"cuda"`` depending on system capabilities.
    """

    from faster_whisper import WhisperModel  # local import for optional dep
    try:  # try optional dependency
        import numpy as np
    except Exception:  # pragma: no cover - fallback without numpy
        np = None  # type: ignore

    model = WhisperModel(name, device=device, compute_type="int8")

    def _transcribe(audio: bytes) -> str:
        """Decode raw audio frames to text using the loaded model."""

        if np is not None:
            array = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0
        else:  # simple pure Python conversion
            import array as pyarray

            ints = pyarray.array("h", audio)
            array = [i / 32768.0 for i in ints]
        segments, _ = model.transcribe(array, language=language, task="transcribe")
        return " ".join(seg.text.strip() for seg in segments)

    return _transcribe
