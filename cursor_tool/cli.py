"""Command-line entry point tying all helpers together.

This module wires the recorder, transcriber and typer modules into a
minimal ``run`` function.  The function is intentionally small so tests
can patch dependencies like models or keyboard interactions.  In real
usage the caller would supply proper Whisper model callables.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

try:  # pragma: no cover - used only when configuring hotkeys
    import keyboard
except Exception:  # pragma: no cover
    keyboard = None  # type: ignore

from .config import Config
from .pipeline import transcribe_from_recorder
from .recorder import recorder, register_hotkeys
from .transcriber import DoubleTranscriber, Model
from .typer import insert_text
from .models import load_faster_whisper


def prompt_hotkey(label: str, current: str) -> str:
    """Prompt user to press a hotkey and return its string representation."""

    if keyboard is None:
        # Fallback to manual typing when ``keyboard`` isn't installed
        return input(f"{label} [{current}]: ") or current

    print(f"{label} [{current}]: ", end="", flush=True)
    hotkey = keyboard.read_hotkey(suppress=False)
    if hotkey == "enter":
        print()
        return current
    print(hotkey)
    return hotkey


def configure(
    path: Optional[Path] = None,
    toggle_key: Optional[str] = None,
    hold_key: Optional[str] = None,
    fast_model: Optional[str] = None,
    precise_model: Optional[str] = None,
    chunk_seconds: Optional[float] = None,
) -> Config:
    """Interactively update and persist user configuration."""

    cfg = Config.load(path)

    def prompt(label: str, current: str) -> str:
        return input(f"{label} [{current}]: ") or current

    toggle_key = toggle_key or prompt_hotkey("Toggle hotkey", cfg.toggle_key)
    hold_key = hold_key or prompt_hotkey("Hold hotkey", cfg.hold_key)
    fast_model = fast_model or prompt("Fast model", cfg.fast_model)
    precise_model = precise_model or prompt("Precise model", cfg.precise_model)
    if chunk_seconds is None:
        chunk_input = prompt("Chunk length (seconds)", str(cfg.chunk_seconds))
        chunk_seconds = float(chunk_input)

    cfg = Config(
        toggle_key=toggle_key,
        hold_key=hold_key,
        fast_model=fast_model,
        precise_model=precise_model,
        chunk_seconds=chunk_seconds,
    )
    cfg.save(path)
    return cfg


def run(fast_model: Model | None = None, precise_model: Model | None = None) -> str:
    """Load config, register hotkeys and process audio once recording stops."""

    cfg = Config.load()
    register_hotkeys(cfg.toggle_key, cfg.hold_key)
    fast = fast_model or load_faster_whisper(cfg.fast_model)
    precise = precise_model or load_faster_whisper(cfg.precise_model)
    transcriber = DoubleTranscriber(fast, precise, on_fast=insert_text)
    return transcribe_from_recorder(recorder, transcriber)
