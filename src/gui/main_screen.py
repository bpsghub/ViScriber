import os
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

SUPPORTED_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".webm"}

LANGUAGES = [
    ("Auto-detect", None),
    ("English", "en"), ("Indonesian", "id"), ("Spanish", "es"),
    ("French", "fr"), ("German", "de"), ("Japanese", "ja"),
    ("Korean", "ko"), ("Chinese", "zh"), ("Arabic", "ar"),
    ("Portuguese", "pt"), ("Russian", "ru"), ("Italian", "it"),
    ("Dutch", "nl"), ("Turkish", "tr"), ("Polish", "pl"),
    ("Vietnamese", "vi"), ("Thai", "th"), ("Hindi", "hi"),
    ("Swedish", "sv"), ("Danish", "da"),
]

MODELS = [
    ("tiny  (~75 MB)", "tiny"),
    ("base  (~140 MB)", "base"),
    ("small  (~250 MB, recommended)", "small"),
    ("medium  (~770 MB)", "medium"),
    ("large  (~1.5 GB)", "large"),
]


class MainScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._files: list[str] = []
        self._build()

    def _build(self):
        from src.config import load_config
        _cfg = load_config()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 0))
        ctk.CTkLabel(header, text="ViScriber: Local Video Transcriber", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="⚙ Settings", width=100, command=self._open_settings).pack(side="right")

        # Drop zone
        self._drop_zone = ctk.CTkLabel(
            self,
            text="Drop video files here\nor click to browse",
            font=ctk.CTkFont(size=14),
            fg_color=("#d0d0d0", "#2b2b2b"),
            corner_radius=12,
            cursor="hand2",
        )
        self._drop_zone.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        self._drop_zone.bind("<Button-1>", self._browse_files)
        try:
            self._drop_zone.drop_target_register(DND_FILES)
            self._drop_zone.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass  # tkinterdnd2 unavailable — fall back to click-only

        # File list
        self._list_frame = ctk.CTkScrollableFrame(self, height=120)
        self._list_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=4)

        # Controls
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=3, column=0, sticky="ew", padx=16, pady=8)
        controls.grid_columnconfigure((0, 1, 2), weight=1)

        lang_values = [name for name, _ in LANGUAGES]
        self._lang_map = {name: code for name, code in LANGUAGES}
        self._lang_var = ctk.StringVar(value=lang_values[0])
        ctk.CTkLabel(controls, text="Language").grid(row=0, column=0, sticky="w")
        ctk.CTkOptionMenu(controls, values=lang_values, variable=self._lang_var).grid(row=1, column=0, sticky="ew", padx=(0, 8))

        model_values = [label for label, _ in MODELS]
        self._model_map = {label: code for label, code in MODELS}
        _default_label = next((label for label, code in MODELS if code == _cfg.default_model), model_values[2])
        self._model_var = ctk.StringVar(value=_default_label)
        ctk.CTkLabel(controls, text="Model").grid(row=0, column=1, sticky="w")
        ctk.CTkOptionMenu(controls, values=model_values, variable=self._model_var).grid(row=1, column=1, sticky="ew", padx=4)

        out_frame = ctk.CTkFrame(controls, fg_color="transparent")
        out_frame.grid(row=1, column=2, sticky="ew", padx=(8, 0))
        _last_dir = _cfg.last_output_dir
        self._out_dir_var = ctk.StringVar(value=_last_dir if _last_dir else "Same as input")
        ctk.CTkLabel(controls, text="Output folder").grid(row=0, column=2, sticky="w")
        ctk.CTkEntry(out_frame, textvariable=self._out_dir_var).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(out_frame, text="…", width=32, command=self._pick_output_dir).pack(side="right")

        self._start_btn = ctk.CTkButton(
            self, text="Start Transcription", height=42,
            font=ctk.CTkFont(size=14, weight="bold"), command=self._start
        )
        self._start_btn.grid(row=4, column=0, sticky="ew", padx=16, pady=(4, 12))

    def _add_file(self, path: str):
        if path in self._files:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext not in SUPPORTED_EXTS:
            return
        self._files.append(path)
        row = ctk.CTkFrame(self._list_frame, fg_color="transparent")
        row.pack(fill="x", pady=1)
        ctk.CTkLabel(row, text=os.path.basename(path), anchor="w").pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="✕", width=28, height=24,
                      command=lambda p=path, r=row: self._remove_file(p, r)).pack(side="right")

    def _remove_file(self, path: str, row_widget):
        if path in self._files:
            self._files.remove(path)
        row_widget.destroy()

    def _on_drop(self, event):
        raw = event.data
        paths = self.tk.splitlist(raw)
        for p in paths:
            self._add_file(p.strip())

    def _browse_files(self, _event=None):
        from tkinter import filedialog
        paths = filedialog.askopenfilenames(
            filetypes=[("Video files", "*.mp4 *.mkv *.mov *.avi *.webm"), ("All files", "*")]
        )
        for p in paths:
            self._add_file(p)

    def _pick_output_dir(self):
        from tkinter import filedialog
        d = filedialog.askdirectory()
        if d:
            self._out_dir_var.set(d)

    def _open_settings(self):
        from src.gui.settings_screen import SettingsModal
        SettingsModal(self.master)

    def _confirm_overwrite(self, out_dir: str, cfg) -> bool:
        formats = [f for f in cfg.output_formats if f != "ai"]
        would_overwrite = []
        for path in self._files:
            stem = os.path.splitext(os.path.basename(path))[0]
            file_out_dir = os.path.dirname(path) or "." if out_dir == "Same as input" else out_dir
            for fmt in formats:
                candidate = os.path.join(file_out_dir, f"{stem}.{fmt}")
                if os.path.exists(candidate):
                    would_overwrite.append(os.path.basename(candidate))
        if not would_overwrite:
            return True
        from tkinter import messagebox
        names = "\n".join(would_overwrite[:5])
        if len(would_overwrite) > 5:
            names += f"\n…and {len(would_overwrite) - 5} more"
        return messagebox.askyesno(
            "Files will be overwritten",
            f"These files already exist and will be overwritten:\n\n{names}\n\nContinue?"
        )

    def _start(self):
        if not self._files:
            from tkinter import messagebox
            messagebox.showinfo(
                "No files",
                "Please add video files first.\n\nClick the drop zone to browse, or drag files onto it."
            )
            return

        from tkinter import messagebox
        from src.core.extractor import is_ffmpeg_available, ffmpeg_install_guide
        if not is_ffmpeg_available():
            messagebox.showerror("FFmpeg Not Found", ffmpeg_install_guide())
            return

        lang_code = self._lang_map.get(self._lang_var.get())
        model_code = self._model_map.get(self._model_var.get(), "small")
        out_dir = self._out_dir_var.get()

        from src.config import load_config, save_config
        cfg = load_config()
        if not self._confirm_overwrite(out_dir, cfg):
            return
        cfg.default_model = model_code
        cfg.last_output_dir = out_dir
        save_config(cfg)

        options = {"language": lang_code, "model": model_code, "output_dir": out_dir}
        self.master.show_progress(list(self._files), options)


class ResultsScreen(ctk.CTkFrame):
    def __init__(self, master, output_files: list):
        super().__init__(master, fg_color="transparent")
        self._output_files = output_files
        self._build()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Transcription Complete ✓",
                     font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(20, 8))

        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=4)
        for path in self._output_files:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ext = os.path.splitext(path)[1].upper()
            ctk.CTkLabel(row, text=f"{ext}  {os.path.basename(path)}", anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(row, text="Open", width=60, command=lambda p=path: self._open(p)).pack(side="right", padx=2)
            ctk.CTkButton(row, text="Folder", width=60,
                          command=lambda p=path: self._open_folder(p)).pack(side="right")

        ctk.CTkButton(self, text="Transcribe More Files", height=38,
                      command=self.master.show_main).grid(row=2, column=0, padx=16, pady=12, sticky="ew")

    def _open(self, path):
        import subprocess, sys
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

    def _open_folder(self, path):
        import subprocess, sys
        folder = os.path.dirname(path)
        if sys.platform.startswith("win"):
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder])
        else:
            subprocess.run(["xdg-open", folder])
