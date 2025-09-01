import subprocess
from pathlib import Path

import pytest

from cursor_tool.packager import build_executable


def test_build_executable_invokes_pyinstaller(monkeypatch, tmp_path):
    script = tmp_path / "dummy.py"
    script.write_text("print('hi')\n")

    captured = {}

    def fake_run(cmd, check):
        captured['cmd'] = cmd
        captured['check'] = check

    monkeypatch.setattr(subprocess, "run", fake_run)

    cmd = build_executable(str(script), name="demo")

    expected = [
        "pyinstaller",
        "--onefile",
        "--name",
        "demo",
        "--windowed",
        str(script),
    ]

    assert captured['cmd'] == expected
    assert captured['check'] is True
    assert cmd == expected


def test_missing_entry_script_raises(tmp_path):
    missing = tmp_path / "missing.py"
    with pytest.raises(FileNotFoundError):
        build_executable(str(missing))
