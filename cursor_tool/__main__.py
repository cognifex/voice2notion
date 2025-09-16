"""Command line interface for the transcribe-to-cursor tool.

This module provides a small CLI that either launches the interactive
configuration wizard or starts the recorder and transcription pipeline.
It allows end users to run the package via ``python -m cursor_tool``
without writing additional scripts.
"""

from __future__ import annotations

import argparse

from .cli import run, configure


def main(argv: list[str] | None = None) -> None:
    """Entry point for the ``python -m cursor_tool`` command."""

    parser = argparse.ArgumentParser(description="Transcribe speech directly to the cursor.")
    parser.add_argument(
        "--configure",
        action="store_true",
        help="run the interactive configuration wizard",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="enable debug logging",
    )
    args = parser.parse_args(argv)

    if args.configure:
        configure()
    else:
        run(verbose=args.verbose)


if __name__ == "__main__":  # pragma: no cover - exercised via tests
    main()
