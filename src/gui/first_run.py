import sys
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
        return any(
            p.name == f"models--Systran--faster-whisper-{model_size}"
            for p in cache_root.iterdir()
        ) if cache_root.exists() else False
    except OSError:
        return False


def maybe_show_first_run(app):
    from src.config import load_config
    from src.core.extractor import is_ffmpeg_available

    cfg = load_config()
    if _model_cached(cfg.default_model) and is_ffmpeg_available():
        return
    dialog = _FirstRunDialog(app)
    app.wait_window(dialog)


class _FirstRunDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Welcome to ViScriber")
        self.geometry("540x460")
        self.resizable(False, False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._selected = ctk.StringVar(value="small")
        self._ffmpeg_missing = False
        self._ffmpeg_button = None
        self._download_button = None
        self._status = None
        self._progress = None
        self._build()

    def _build(self):
        from src.core.extractor import is_ffmpeg_available

        self._ffmpeg_missing = not is_ffmpeg_available()

        ctk.CTkLabel(
            self,
            text="Set up the local transcription tools",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(pady=(16, 4))
        ctk.CTkLabel(
            self,
            text="ViScriber uses FFmpeg to extract audio and Whisper models for transcription.\nBoth are downloaded once and stored locally.",
            text_color="gray",
        ).pack(pady=(0, 12))

        ffmpeg_frame = ctk.CTkFrame(self)
        ffmpeg_frame.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(
            ffmpeg_frame,
            text="FFmpeg",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(12, 2))

        if self._ffmpeg_missing:
            ctk.CTkLabel(
                ffmpeg_frame,
                text="Required to read video audio tracks.",
                text_color="gray",
            ).pack(anchor="w", padx=14)
            if sys.platform.startswith("win"):
                self._ffmpeg_button = ctk.CTkButton(
                    ffmpeg_frame,
                    text="Install FFmpeg automatically",
                    command=self._install_ffmpeg,
                )
                self._ffmpeg_button.pack(anchor="w", padx=14, pady=(8, 12))
            else:
                ctk.CTkLabel(
                    ffmpeg_frame,
                    text="Install FFmpeg separately, then reopen ViScriber.",
                    text_color="gray",
                ).pack(anchor="w", padx=14, pady=(6, 12))
        else:
            ctk.CTkLabel(
                ffmpeg_frame,
                text="FFmpeg is already available.",
                text_color="gray",
            ).pack(anchor="w", padx=14, pady=(0, 12))

        model_frame = ctk.CTkFrame(self)
        model_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        ctk.CTkLabel(
            model_frame,
            text="Choose a Whisper model to download",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(
            model_frame,
            text="Models are cached locally and downloaded only once.",
            text_color="gray",
        ).pack(anchor="w", padx=14, pady=(0, 8))

        for size, mb, note in MODEL_INFO:
            row = ctk.CTkFrame(model_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkRadioButton(
                row,
                text=f"{size}  {mb}  — {note}",
                variable=self._selected,
                value=size,
            ).pack(side="left")

        self._progress = ctk.CTkProgressBar(model_frame)
        self._progress.set(0)
        self._progress.pack(fill="x", padx=14, pady=(10, 4))
        self._status = ctk.CTkLabel(model_frame, text="")
        self._status.pack(anchor="w", padx=14)

        button_row = ctk.CTkFrame(model_frame, fg_color="transparent")
        button_row.pack(fill="x", padx=14, pady=(10, 12))
        self._download_button = ctk.CTkButton(
            button_row,
            text="Download model and continue",
            command=self._download_model,
        )
        self._download_button.pack(side="right")
        ctk.CTkButton(button_row, text="Close", command=self.destroy).pack(side="right", padx=(0, 8))

    def _set_status(self, message: str):
        self._status.configure(text=message)

    def _set_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        if self._ffmpeg_button is not None:
            self._ffmpeg_button.configure(state=state)
        if self._download_button is not None:
            self._download_button.configure(state=state)

    def _install_ffmpeg(self):
        if not sys.platform.startswith("win"):
            return

        self._set_busy(True)
        self._set_status("Downloading FFmpeg for Windows…")

        def worker():
            try:
                from src.core.extractor import download_ffmpeg_windows

                install_path = download_ffmpeg_windows()
                self.after(0, lambda: self._on_ffmpeg_installed(install_path))
            except Exception as exc:
                self.after(0, lambda: self._on_error(f"FFmpeg install failed: {exc}"))

        threading.Thread(target=worker, daemon=True).start()

    def _on_ffmpeg_installed(self, install_path: str):
        self._ffmpeg_missing = False
        if self._ffmpeg_button is not None:
            self._ffmpeg_button.configure(text="FFmpeg installed", state="disabled")
        self._set_status(f"FFmpeg installed to {install_path}")
        self._set_busy(False)

    def _download_model(self):
        model_size = self._selected.get()
        self._set_busy(True)
        self._set_status(f"Downloading {model_size} model from Hugging Face…")

        def worker():
            try:
                from faster_whisper import WhisperModel
                from src.config import load_config, save_config

                self.after(0, self._progress.start)
                WhisperModel(model_size, device="cpu", compute_type="int8")
                self.after(0, self._progress.stop)
                self.after(0, lambda: self._progress.set(1))

                cfg = load_config()
                cfg.default_model = model_size
                save_config(cfg)
                self.after(0, self.destroy)
            except Exception as exc:
                self.after(0, lambda: self._on_error(f"Error: {exc}"))

        threading.Thread(target=worker, daemon=True).start()

    def _on_error(self, message: str):
        self._progress.stop()
        self._set_status(message)
        self._set_busy(False)
