import threading

try:
    import tkinter as tk
except Exception:  # pragma: no cover - tkinter might not be installed
    tk = None

try:
    import winsound
except Exception:  # pragma: no cover - winsound only on Windows
    winsound = None


class RecordingIndicator:
    """Small overlay and optional beeps indicating recording state."""

    def __init__(self, *, beep: bool = True) -> None:
        self._beep = beep
        self._thread: threading.Thread | None = None
        self._root: "tk.Tk" | None = None
        self._visible = False

    # sound helpers -----------------------------------------------------
    def _play_start(self) -> None:
        if self._beep and winsound:
            winsound.Beep(880, 150)

    def _play_stop(self) -> None:
        if self._beep and winsound:
            winsound.Beep(440, 150)

    # visual helpers ----------------------------------------------------
    def _run(self) -> None:
        if not tk:  # pragma: no cover - no GUI available
            return
        root = tk.Tk()
        self._root = root
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        canvas = tk.Canvas(root, width=20, height=20, highlightthickness=0)
        canvas.pack()
        canvas.create_oval(2, 2, 18, 18, fill="green", outline="")
        root.mainloop()

    # public API --------------------------------------------------------
    @property
    def visible(self) -> bool:
        return self._visible

    def start(self) -> None:
        """Show indicator and play start sound."""
        if self._visible:
            return
        self._visible = True
        if tk:
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
        self._play_start()

    def stop(self) -> None:
        """Hide indicator and play stop sound."""
        if not self._visible:
            return
        self._visible = False
        if self._root:
            self._root.quit()
            self._root = None
        self._thread = None
        self._play_stop()
