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
import logging

try:  # pragma: no cover - these are patched in tests
    import sounddevice as sd
except Exception:  # pragma: no cover
    sd = None  # type: ignore

try:  # pragma: no cover
    import keyboard
except Exception:  # pragma: no cover
    keyboard = None  # type: ignore

try:  # pragma: no cover
    from pynput import keyboard as pynput_keyboard
except Exception:  # pragma: no cover
    pynput_keyboard = None  # type: ignore

from .hotkeys import normalize_hotkey
from .indicator import indicator


class Recorder:
    """Manage an input stream and hotkey registration."""

    def __init__(self, samplerate: int = 16_000, channels: int = 1, dtype: str = "int16"):
        self.samplerate = samplerate
        self.channels = channels
        self.dtype = dtype
        self.queue: "queue.Queue[bytes | None]" = queue.Queue()
        self._stream: Optional[sd.InputStream] = None
        self.is_recording = False
        self._hold_active = False

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
        logging.debug("recording started")
        indicator.start()

    def stop_recording(self) -> None:
        """Stop and close the microphone stream."""

        if not self.is_recording:
            return
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self.is_recording = False
        logging.debug("recording stopped")
        indicator.stop()
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
        toggle = normalize_hotkey(toggle)
        hold = normalize_hotkey(hold) if hold else None
        logging.debug("register hotkeys toggle=%s hold=%s", toggle, hold)

        if keyboard is not None:
            keyboard.add_hotkey(toggle, self.toggle_recording)
            if hold:
                keyboard.add_hotkey(hold, self.start_recording)
                keyboard.add_hotkey(hold, self.stop_recording, trigger_on_release=True)
            return

        if pynput_keyboard is None:  # pragma: no cover
            raise RuntimeError("keyboard not available")

        def parse(combo: str) -> set:
            keys = set()
            for part in combo.split("+"):
                name = part.strip().lower()
                try:
                    keys.add(getattr(pynput_keyboard.Key, name))
                except AttributeError:
                    keys.add(pynput_keyboard.KeyCode.from_char(name))
            return keys

        toggle_keys = parse(toggle)
        hold_keys = parse(hold) if hold else None
        pressed: set = set()

        def on_press(key):
            pressed.add(key)
            if toggle_keys <= pressed:
                self.toggle_recording()
            if hold_keys and hold_keys <= pressed and not self.is_recording:
                self.start_recording()
                self._hold_active = True

        def on_release(key):
            pressed.discard(key)
            if hold_keys and self._hold_active and not hold_keys <= pressed:
                self._hold_active = False
                self.stop_recording()

        self._listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
        self._listener.start()


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

