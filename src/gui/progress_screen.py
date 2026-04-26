import threading
import os
import customtkinter as ctk
from src.config import load_config
from src.core.transcriber import transcribe_file
from src.core.ai_client import get_client


class ProgressScreen(ctk.CTkFrame):
    def __init__(self, master, files: list, options: dict):
        super().__init__(master, fg_color="transparent")
        self._files = files
        self._opts = options
        self._cancel_event = threading.Event()
        self._output_files: list[str] = []
        self._build()
        self._start_worker()

    def _build(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Transcribing…",
                     font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(16, 4))

        self._overall_label = ctk.CTkLabel(self, text="File 0 of 0")
        self._overall_label.grid(row=1, column=0)
        self._overall_bar = ctk.CTkProgressBar(self, width=400)
        self._overall_bar.set(0)
        self._overall_bar.grid(row=2, column=0, padx=32, pady=4, sticky="ew")

        self._step_label = ctk.CTkLabel(self, text="Starting…")
        self._step_label.grid(row=3, column=0)
        self._file_bar = ctk.CTkProgressBar(self, width=400)
        self._file_bar.set(0)
        self._file_bar.grid(row=4, column=0, padx=32, pady=4, sticky="ew")

        self._log = ctk.CTkTextbox(self, height=200, state="disabled")
        self._log.grid(row=5, column=0, sticky="nsew", padx=16, pady=8)

        self._cancel_btn = ctk.CTkButton(self, text="Cancel", fg_color="gray40",
                                         command=self._cancel)
        self._cancel_btn.grid(row=6, column=0, pady=(0, 12))

    def _log_line(self, text: str):
        self._log.configure(state="normal")
        self._log.insert("end", text + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _update_progress(self, file_index: int, step: str, pct: float):
        overall = (file_index / len(self._files)) if self._files else 0
        self.master.after(0, lambda: self._overall_label.configure(
            text=f"File {file_index + 1} of {len(self._files)}"))
        self.master.after(0, lambda: self._overall_bar.set(overall))
        self.master.after(0, lambda: self._step_label.configure(text=step))
        self.master.after(0, lambda: self._file_bar.set(pct / 100))
        self.master.after(0, lambda: self._log_line(f"[{os.path.basename(self._files[file_index])}] {step}"))

    def _cancel(self):
        self._cancel_event.set()
        self._cancel_btn.configure(state="disabled", text="Cancelling…")

    def _start_worker(self):
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        cfg = load_config()
        opts = self._opts
        out_base = opts.get("output_dir", "Same as input")

        for i, video_path in enumerate(self._files):
            if self._cancel_event.is_set():
                break

            if out_base == "Same as input":
                out_dir = os.path.dirname(video_path) or "."
            else:
                out_dir = out_base

            formats = [f for f in cfg.output_formats if f != "ai"]

            result = transcribe_file(
                video_path=video_path,
                output_dir=out_dir,
                language=opts.get("language"),
                model_size=opts.get("model", "small"),
                device=cfg.default_device,
                chunk_minutes=5,
                formats=formats,
                progress_callback=lambda step, pct, idx=i: self._update_progress(idx, step, pct),
            )

            if result.success:
                self._output_files.extend(result.output_files)

                if "ai" in cfg.output_formats and cfg.ai_provider != "none":
                    self.master.after(0, lambda idx=i: self._step_label.configure(text="Generating AI summary…"))
                    ai_client = get_client(cfg.ai_provider, cfg.api_key, cfg.ollama_url)
                    if ai_client:
                        txt_files = [f for f in result.output_files if f.endswith(".txt")]
                        if txt_files:
                            transcript = open(txt_files[0], encoding="utf-8").read()
                            summary = ai_client.summarize(transcript, cfg.custom_ai_prompt)
                            md_path = txt_files[0].replace(".txt", "_summary.md")
                            with open(md_path, "w", encoding="utf-8") as f:
                                f.write(summary)
                            self._output_files.append(md_path)
            else:
                self.master.after(0, lambda e=result.error: self._log_line(f"[ERROR] {e}"))

        self.master.after(0, lambda: self.master.show_results(self._output_files))
