# Transcribe to Cursor

A lightweight prototype for Windows that transcribes speech and types the
result into the currently focused text field.  It uses two Whisper models:
a tiny one for instant feedback and a larger one for background
corrections.

## Features

* Global hotkeys to start/stop recording or hold-to-talk
* Real-time transcription with a fast model
* Higher quality corrections in the background
* Visual indicator overlay with optional beep sounds
* Persistent configuration for hotkeys, model names and chunk length
* Helper to package the tool as a standalone Windows executable

## Installation

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m cursor_tool --configure  # set up hotkeys and model names
python -m cursor_tool              # start the recorder and transcriber
```

When configuring, press the desired key combinations (or hit Enter to keep
the current value) and the chosen hotkeys will be displayed in a readable
form.  Manual input also works and common localised names such as
``strg`` (``ctrl``) or ``umschalt`` (``shift``) are automatically
normalised.  If the ``keyboard`` package is unavailable, the tool falls
back to ``pynput`` for handling them.

The default configuration is stored in ``~/.cursor_tool.json``.  During
runtime the fast model's output is injected directly at the cursor while
the precise model refines the text in-place.

## Packaging

To create a standalone executable on Windows, install ``pyinstaller`` and
run:

```bash
python -c "from cursor_tool import build_executable; build_executable()"
```

The resulting binary will appear in the ``dist`` directory.

## Development

Install dependencies and run the test suite:

```bash
pip install -r requirements.txt
pytest -q
```

## License

This project is released under the MIT license.
