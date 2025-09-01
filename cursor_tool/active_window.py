"""Detect whether the currently focused window accepts text input.

This module provides a minimal abstraction for determining if the
user's current focus is on an editable control.  On Windows we query the
foreground window's class name via ``ctypes``.  For other platforms or
when the query fails the function falls back to assuming text input is
allowed so that development and tests can proceed without a GUI.
"""

from __future__ import annotations

import sys
from typing import Iterable

try:  # pragma: no cover - platform specific
    import ctypes
    from ctypes import wintypes
except Exception:  # pragma: no cover - non-Windows
    ctypes = None  # type: ignore


EDIT_CLASSES: Iterable[str] = {
    "Edit",
    "RichEdit20A",
    "RichEdit20W",
}


def _get_foreground_class() -> str:
    """Return the window class name of the foreground window."""
    if ctypes is None:  # pragma: no cover - platform specific
        return ""
    try:  # pragma: no cover - only executed on Windows
        user32 = ctypes.windll.user32  # type: ignore[attr-defined]
        hwnd = user32.GetForegroundWindow()
        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf, 256)
        return buf.value
    except Exception:
        return ""


def is_text_field_focused() -> bool:
    """Return ``True`` if the foreground window is likely editable.

    The heuristic simply checks the native window class name against a
    small set of known edit controls.  It errs on the side of ``True`` so
    that the typing helper remains usable in environments where we cannot
    determine the focus reliably (e.g. during tests or on non-Windows
    platforms).
    """

    cls = _get_foreground_class()
    if not cls:
        return True
    return cls in EDIT_CLASSES

