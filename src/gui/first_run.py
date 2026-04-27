import os
import threading
from pathlib import Path
import customtkinter as ctk

MODEL_INFO = [
    ("tiny",   "~75 MB",   "Fastest; lower accuracy"),
    ("base",   "~140 MB",  "Fast; decent accuracy"),
    ("small",  "~250 MB",  "Recommended balance"),
    ("medium", "~770 MB",  "High accuracy; slower"),
    ("large",  "~1.5 GB",  "Best accuracy; very slow on CPU"),
]


def _model_cached(model_size: str) -> bool:
    cache_root = Path.home() / ".cache" / "huggingface" / "hub"
    try:
        return any(p.name == f"models--Systran--faster-whisper-{model_size}"
                   for p in cache_root.iterdir()) if cache_root.exists() else False
    except OSError:
        return False


def maybe_show_first_run(app):
    from src.config import load_config, save_config
    cfg = load_config()
    if _model_cached(cfg.default_model):
        return
    dialog = _FirstRunDialog(app)
    app.wait_window(dialog)


class _FirstRunDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Welcome — Download Whisper Model")
        self.geometry("460x360")
        self.resizable(False, False)
        self.grab_set()
        self._selected = ctk.StringVar(value="small")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Choose a Whisper model to download",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(16, 4))
        ctk.CTkLabel(self, text="Models are cached locally (~/.cache/huggingface/hub).\nDownload only happens once.",
                     text_color="gray").pack(pady=(0, 12))

        for size, mb, note in MODEL_INFO:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=2)
            ctk.CTkRadioButton(row, text=f"{size}  {mb}  — {note}",
                               variable=self._selected, value=size).pack(side="left")

        self._progress = ctk.CTkProgressBar(self)
        self._progress.set(0)
        self._progress.pack(fill="x", padx=20, pady=(16, 4))
        self._status = ctk.CTkLabel(self, text="")
        self._status.pack()

        ctk.CTkButton(self, text="Download & Continue", command=self._download).pack(pady=12)

    def _download(self):
        model_size = self._selected.get()
        self._status.configure(text=f"Downloading {model_size} model from HuggingFace…")

        def worker():
            try:
                from faster_whisper import WhisperModel
                self._progress.start()
                WhisperModel(model_size, device="cpu", compute_type="int8")
                self._progress.stop()
                self._progress.set(1)
                from src.config import load_config, save_config
                cfg = load_config()
                cfg.default_model = model_size
                save_config(cfg)
                self.master.after(0, self.destroy)
            except Exception as e:
                self.master.after(0, lambda: self._status.configure(text=f"Error: {e}"))

        threading.Thread(target=worker, daemon=True).start()
