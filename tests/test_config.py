import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from cursor_tool.config import Config

def test_load_defaults(tmp_path):
    path = tmp_path / "config.json"
    cfg = Config.load(path)
    assert cfg.toggle_key == "ctrl+shift+space"
    assert cfg.fast_model == "tiny"
    assert cfg.chunk_seconds == 5.0
    assert cfg.language == "de"

def test_save_and_load(tmp_path):
    path = tmp_path / "config.json"
    cfg = Config(toggle_key="F9", fast_model="tiny", chunk_seconds=3.5)
    cfg.save(path)
    loaded = Config.load(path)
    assert loaded == cfg
