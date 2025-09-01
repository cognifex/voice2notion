"""Helper modules for the transcribe-to-cursor prototype."""

from .transcriber import DoubleTranscriber
from .diff import merge_overlaps
from .recorder import (
    Recorder,
    start_recording,
    stop_recording,
    register_hotkeys,
    recorder,
)
from .pipeline import transcribe_from_recorder
from .typer import insert_text
from .config import Config, default_config_path
from .cli import run, configure
from .models import load_faster_whisper
from .active_window import is_text_field_focused
from .indicator import RecordingIndicator
from .packager import build_executable

__all__ = [
    "DoubleTranscriber",
    "Recorder",
    "recorder",
    "start_recording",
    "stop_recording",
    "register_hotkeys",
    "transcribe_from_recorder",
    "insert_text",
    "is_text_field_focused",
    "RecordingIndicator",
    "Config",
    "default_config_path",
    "configure",
    "run",
    "load_faster_whisper",
    "merge_overlaps",
    "build_executable",
]
