"""Utilities for typing text into the active window."""

from __future__ import annotations

try:  # pragma: no cover - patched in tests
    import keyboard
except Exception:  # pragma: no cover
    keyboard = None  # type: ignore

from .active_window import is_text_field_focused


def insert_text(text: str) -> None:
    """Type ``text`` at the current cursor position.

    In real usage this relies on the ``keyboard`` package which provides
    cross-platform keyboard emulation. During tests the module-level
    ``keyboard`` attribute can be patched with a stub exposing a ``write``
    method.
    """

    if keyboard is None:  # pragma: no cover
        raise RuntimeError("keyboard not available")
    if not is_text_field_focused():  # pragma: no branch - simple guard
        return
    keyboard.write(text)
