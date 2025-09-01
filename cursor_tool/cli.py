"""Command-line entry point tying all helpers together.

This module wires the recorder, transcriber and typer modules into a
minimal ``run`` function.  The function is intentionally small so tests
can patch dependencies like models or keyboard interactions.  In real
usage the caller would supply proper Whisper model callables.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import logging

try:  # pragma: no cover - used only when configuring hotkeys
    import keyboard
except Exception:  # pragma: no cover
    keyboard = None  # type: ignore

from .config import Config
from .hotkeys import normalize_hotkey
from .pipeline import transcribe_from_recorder
from .recorder import recorder, register_hotkeys
from .transcriber import DoubleTranscriber, Model
from .typer import insert_text
from .models import load_faster_whisper
from .indicator import indicator


def _flush_stdin() -> None:
    """Best-effort removal of pending characters from ``stdin``."""

    try:  # Windows
        import msvcrt

        while msvcrt.kbhit():
            msvcrt.getwch()
    except Exception:
        try:  # POSIX
            import sys
            import termios

            termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except Exception:
            pass


def prompt_hotkey(label: str, current: str) -> str:
    """Prompt the user for a hotkey and normalise the result.

    The function prefers ``keyboard.read_hotkey`` so the user can simply press
    the desired combination.  When ``keyboard`` isn't available or the user
    types a value manually we still normalise common localised key names such as
    ``strg`` or ``umschalt``.
    """

    if keyboard is None:
        # Fallback to manual typing when ``keyboard`` isn't installed
        return normalize_hotkey(input(f"{label} [{current}]: ") or current)

    print(f"{label} [{current}]: ", end="", flush=True)
    hotkey = keyboard.read_hotkey(suppress=False)
    if hotkey == "enter":
        print()
        return current
    print(hotkey)
    _flush_stdin()
    return normalize_hotkey(hotkey)


def configure(
    path: Optional[Path] = None,
    toggle_key: Optional[str] = None,
    hold_key: Optional[str] = None,
    fast_model: Optional[str] = None,
    precise_model: Optional[str] = None,
    chunk_seconds: Optional[float] = None,
    language: Optional[str] = None,
) -> Config:
    """Interactively update and persist user configuration."""

    cfg = Config.load(path)

    def prompt(label: str, current: str) -> str:
        _flush_stdin()
        return input(f"{label} [{current}]: ") or current

    toggle_key = normalize_hotkey(toggle_key or prompt_hotkey("Toggle hotkey", cfg.toggle_key))
    hold_key = normalize_hotkey(hold_key or prompt_hotkey("Hold hotkey", cfg.hold_key))
    fast_model = fast_model or prompt("Fast model", cfg.fast_model)
    precise_model = precise_model or prompt("Precise model", cfg.precise_model)
    if chunk_seconds is None:
        chunk_input = prompt("Chunk length (seconds)", str(cfg.chunk_seconds))
        chunk_seconds = float(chunk_input)
    language = language or prompt("Language", cfg.language)

    cfg = Config(
        toggle_key=toggle_key,
        hold_key=hold_key,
        fast_model=fast_model,
        precise_model=precise_model,
        chunk_seconds=chunk_seconds,
        language=language,
    )
    cfg.save(path)
    return cfg


def run(
    fast_model: Model | None = None,
    precise_model: Model | None = None,
    *,
    verbose: bool = False,
) -> str:
    """Load config, register hotkeys and process audio once recording stops."""

    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    cfg = Config.load()
    logging.debug("configuration loaded: %s", cfg)
    print("Loading models...", flush=True)
    fast = fast_model or load_faster_whisper(cfg.fast_model, language=cfg.language)
    precise = precise_model or load_faster_whisper(cfg.precise_model, language=cfg.language)
    indicator.show()
    register_hotkeys(cfg.toggle_key, cfg.hold_key)
    msg = f"Press {cfg.toggle_key} to start/stop recording"
    if cfg.hold_key and cfg.hold_key != cfg.toggle_key:
        msg += f" or hold {cfg.hold_key} to talk"
    print(msg + ".")
    transcriber = DoubleTranscriber(fast, precise, on_fast=insert_text)
    text = transcribe_from_recorder(recorder, transcriber)
    print(text)
    return text
