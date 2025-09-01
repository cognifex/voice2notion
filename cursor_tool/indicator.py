import threading

try:
    import tkinter as tk
except Exception:  # pragma: no cover - tkinter might not be installed
    tk = None


class RecordingIndicator:
    """Small always-on-top overlay indicating recording state."""

    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._root: "tk.Tk" | None = None
        self._canvas: "tk.Canvas" | None = None
        self._oval: int | None = None
        self._visible = False
        self._color = "red"

    # visual helpers ----------------------------------------------------
    def _run(self) -> None:
        if not tk:  # pragma: no cover - no GUI available
            return
        try:
            root = tk.Tk()
        except Exception:  # pragma: no cover - e.g. no DISPLAY
            return
        self._root = root
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        try:
            root.attributes("-transparentcolor", "black")
        except Exception:
            pass
        root.geometry("20x20+10+10")
        root.configure(bg="black")
        canvas = tk.Canvas(root, width=20, height=20, highlightthickness=0, bg="black")
        canvas.pack()
        self._canvas = canvas
        self._oval = canvas.create_oval(2, 2, 18, 18, fill=self._color, outline="")
        root.mainloop()

    def _update(self, color: str) -> None:
        if not self._root or not self._canvas or self._oval is None:
            return
        self._color = color
        def _():
            self._canvas.itemconfig(self._oval, fill=color)
        self._root.after(0, _)

    # public API --------------------------------------------------------
    @property
    def visible(self) -> bool:
        return self._visible

    def show(self) -> None:
        """Create the overlay if not yet visible."""
        if self._visible:
            return
        self._visible = True
        if tk:
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            # wait briefly for Tk to initialise
            import time
            for _ in range(50):
                if self._root is not None:
                    break
                time.sleep(0.01)

    def start(self) -> None:
        """Turn the indicator green."""
        self.show()
        self._update("green")

    def stop(self) -> None:
        """Turn the indicator red."""
        self.show()
        self._update("red")


indicator = RecordingIndicator()
