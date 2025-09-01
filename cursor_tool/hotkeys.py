from __future__ import annotations

"""Utilities for normalising hotkey strings.

The :mod:`keyboard` package expects English key names like ``ctrl`` and
``shift``.  Users on non-English layouts often enter localised names such as
``strg`` or ``umschalt`` which would otherwise raise a ``ValueError``.

``normalize_hotkey`` replaces known localised aliases with the canonical names
understood by the ``keyboard`` library.
"""

from typing import Iterable, Optional

# mapping of common non-English key names to the values expected by ``keyboard``
KEY_ALIASES = {
    "strg": "ctrl",
    "steuerung": "ctrl",
    "control": "ctrl",
    "umschalt": "shift",
    "shift": "shift",
    "altgr": "alt gr",
    "alt": "alt",
    "option": "alt",
    "win": "windows",
    "meta": "windows",
}

# set of modifier keys that may appear in hotkey definitions
MODIFIER_KEYS = {"ctrl", "shift", "alt", "alt gr", "windows"}


def _normalize_part(part: str) -> Optional[str]:
    """Return normalised version of *part* or ``None`` if invalid."""

    cleaned = part.strip().lower().strip("\"'` ")
    if not cleaned or not any(ch.isalnum() for ch in cleaned):
        return None
    return KEY_ALIASES.get(cleaned, cleaned)

def normalize_hotkey(hotkey: str | Iterable[str]) -> str:
    """Return *hotkey* with known aliases replaced by canonical names."""
    if isinstance(hotkey, str):
        parts = hotkey.split("+")
    else:  # pragma: no cover - not used but keeps function generic
        parts = list(hotkey)

    normalized: list[str] = []
    for p in parts:
        norm = _normalize_part(p)
        if norm:
            normalized.append(norm)
    return "+".join(normalized)


def is_modifier_combo(hotkey: str) -> bool:
    """Return ``True`` if *hotkey* contains only modifier keys."""

    parts = normalize_hotkey(hotkey).split("+") if hotkey else []
    return bool(parts) and all(part in MODIFIER_KEYS for part in parts)
