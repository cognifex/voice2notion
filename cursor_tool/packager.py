"""Packaging helpers for building a standalone executable."""

from __future__ import annotations

import subprocess
from pathlib import Path


def build_executable(entry_script: str = "cursor_tool/cli.py", name: str = "cursor_tool") -> list[str]:
    """Create a Windows executable using PyInstaller.

    Parameters
    ----------
    entry_script:
        The path to the script that should act as the program's entry point.
    name:
        The desired name of the generated executable.

    Returns
    -------
    list[str]
        The command passed to ``subprocess.run`` for building the executable.

    Notes
    -----
    The function only invokes PyInstaller. It does not verify that PyInstaller
    is installed or that the build succeeds. It is primarily intended for use
    in automated packaging scripts and unit tests, where the actual build step
    may be mocked.
    """

    script_path = Path(entry_script)
    if not script_path.exists():
        raise FileNotFoundError(entry_script)

    cmd = [
        "pyinstaller",
        "--onefile",
        "--name",
        name,
        "--windowed",
        str(script_path),
    ]
    subprocess.run(cmd, check=True)
    return cmd
