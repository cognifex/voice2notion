"""Audio recorder with global hotkey support.

This module provides a tiny abstraction around ``sounddevice`` for
capturing microphone input and ``keyboard`` for registering global
hotkeys.  It exposes ``start_recording`` and ``stop_recording`` helper
functions which feed raw audio frames into a queue.  The intent is to
offer a minimal building block for the later transcribe-to-cursor tool.

The implementation is deliberately lightweight so that unit tests can
patch the external dependencies.  In real usage the queue would be
consumed by transcription workers.
"""

from __future__ import annotations

import queue
from typing import Optional

try:  # pragma: no cover - these are patched in tests
    import sounddevice as sd
except Exception:  # pragma: no cover
    sd = None  # type: ignore

try:  # pragma: no cover
    import keyboard
except Exception:  # pragma: no cover
    keyboard = None  # type: ignore


class Recorder:
    """Manage an input stream and hotkey registration."""

    def __init__(self, samplerate: int = 16_000, channels: int = 1, dtype: str = "int16"):
        self.samplerate = samplerate
        self.channels = channels
        self.dtype = dtype
        self.queue: "queue.Queue[bytes | None]" = queue.Queue()
        self._stream: Optional[sd.InputStream] = None
        self.is_recording = False

    def _callback(self, indata, frames, time, status) -> None:  # pragma: no cover - called by sounddevice
        """Receive audio frames from ``sounddevice`` and enqueue them."""

        self.queue.put(bytes(indata))

    def start_recording(self) -> None:
        """Start the microphone stream if not already active."""

        if self.is_recording:
            return
        if sd is None:  # pragma: no cover
            raise RuntimeError("sounddevice not available")
        self._stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype=self.dtype,
            callback=self._callback,
        )
        self._stream.start()
        self.is_recording = True

    def stop_recording(self) -> None:
        """Stop and close the microphone stream."""

        if not self.is_recording:
            return
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self.is_recording = False
        # Signal consumers that no more audio will arrive
        self.queue.put(None)

    def toggle_recording(self) -> None:
        """Toggle between ``start_recording`` and ``stop_recording``."""

        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def register_hotkeys(self, toggle: str, hold: Optional[str] = None) -> None:
        """Register global hotkeys for controlling the recorder."""

        if keyboard is None:  # pragma: no cover
            raise RuntimeError("keyboard not available")
        keyboard.add_hotkey(toggle, self.toggle_recording)
        if hold:
            keyboard.on_press_key(hold, lambda _: self.start_recording())
            keyboard.on_release_key(hold, lambda _: self.stop_recording())


recorder = Recorder()


def start_recording() -> None:
    """Module-level helper delegating to :class:`Recorder`."""

    recorder.start_recording()


def stop_recording() -> None:
    """Module-level helper delegating to :class:`Recorder`."""

    recorder.stop_recording()


def register_hotkeys(toggle: str, hold: Optional[str] = None) -> None:
    """Register hotkeys on the module-level recorder."""

    recorder.register_hotkeys(toggle, hold)

