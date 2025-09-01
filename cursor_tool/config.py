from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from .hotkeys import normalize_hotkey, is_modifier_combo

DEFAULT_TOGGLE = "ctrl+shift+space"
DEFAULT_HOLD = "ctrl+space"
DEFAULT_FAST_MODEL = "tiny"
DEFAULT_PRECISE_MODEL = "base"
DEFAULT_CHUNK_SECONDS = 5.0
DEFAULT_LANGUAGE = "de"


def default_config_path() -> Path:
    """Return the default path for the config file."""
    return Path.home() / ".cursor_tool.json"


@dataclass
class Config:
    """Persistent user configuration."""

    toggle_key: str = DEFAULT_TOGGLE
    hold_key: str = DEFAULT_HOLD
    fast_model: str = DEFAULT_FAST_MODEL
    precise_model: str = DEFAULT_PRECISE_MODEL
    chunk_seconds: float = DEFAULT_CHUNK_SECONDS
    language: str = DEFAULT_LANGUAGE

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """Load configuration from *path* or default location."""

        cfg_path = path or default_config_path()
        if cfg_path.exists():
            data = json.loads(cfg_path.read_text("utf-8"))
            cfg = cls(**{**asdict(cls()), **data})  # type: ignore[arg-type]
        else:
            cfg = cls()

        cfg.toggle_key = normalize_hotkey(cfg.toggle_key)
        cfg.hold_key = normalize_hotkey(cfg.hold_key)
        if is_modifier_combo(cfg.toggle_key):
            cfg.toggle_key = DEFAULT_TOGGLE
        if is_modifier_combo(cfg.hold_key):
            cfg.hold_key = DEFAULT_HOLD
        return cfg

    def save(self, path: Optional[Path] = None) -> None:
        """Write configuration to *path* or default location."""

        cfg_path = path or default_config_path()
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(json.dumps(asdict(self), indent=2), "utf-8")
