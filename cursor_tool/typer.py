"""Utilities for typing text into the active window."""

from __future__ import annotations

try:  # pragma: no cover - patched in tests
    import keyboard
except Exception:  # pragma: no cover
    keyboard = None  # type: ignore

try:  # pragma: no cover
    from pynput import keyboard as pynput_keyboard
except Exception:  # pragma: no cover
    pynput_keyboard = None  # type: ignore

from .active_window import is_text_field_focused


def insert_text(text: str) -> None:
    """Type ``text`` at the current cursor position.

    In real usage this relies on the ``keyboard`` package which provides
    cross-platform keyboard emulation. During tests the module-level
    ``keyboard`` attribute can be patched with a stub exposing a ``write``
    method.
    """

    if not is_text_field_focused():  # pragma: no branch - simple guard
        return
    if keyboard is not None:
        keyboard.write(text)
        return
    if pynput_keyboard is not None:  # pragma: no cover - simplified fallback
        controller = pynput_keyboard.Controller()
        controller.type(text)
        return
    raise RuntimeError("keyboard not available")
