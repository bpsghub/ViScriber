import customtkinter as ctk
from src.config import load_config, save_config


class SettingsModal(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("480x560")
        self.minsize(400, 400)
        self.resizable(False, True)
        self.grab_set()
        self._cfg = load_config()
        self._build()

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Scrollable form area
        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        pad = {"padx": 16, "pady": 6}

        ctk.CTkLabel(scroll, text="AI Provider", anchor="w").grid(row=0, column=0, sticky="w", **pad)
        self._provider_var = ctk.StringVar(value=self._cfg.ai_provider)
        provider_menu = ctk.CTkOptionMenu(
            scroll, values=["none", "claude", "openai", "ollama"],
            variable=self._provider_var, command=self._on_provider_change
        )
        provider_menu.grid(row=1, column=0, sticky="ew", **pad)

        ctk.CTkLabel(scroll, text="API Key (Claude / OpenAI)", anchor="w").grid(row=2, column=0, sticky="w", **pad)
        self._api_key_var = ctk.StringVar(value=self._cfg.api_key)
        self._api_key_entry = ctk.CTkEntry(scroll, textvariable=self._api_key_var, show="•")
        self._api_key_entry.grid(row=3, column=0, sticky="ew", **pad)

        ctk.CTkLabel(scroll, text="Ollama URL", anchor="w").grid(row=4, column=0, sticky="w", **pad)
        self._ollama_var = ctk.StringVar(value=self._cfg.ollama_url)
        self._ollama_entry = ctk.CTkEntry(scroll, textvariable=self._ollama_var)
        self._ollama_entry.grid(row=5, column=0, sticky="ew", **pad)

        ctk.CTkLabel(scroll, text="AI Prompt (what to do with transcript)", anchor="w").grid(row=6, column=0, sticky="w", **pad)
        self._prompt_box = ctk.CTkTextbox(scroll, height=80)
        self._prompt_box.grid(row=7, column=0, sticky="ew", **pad)
        self._prompt_box.insert("0.0", self._cfg.custom_ai_prompt)

        ctk.CTkLabel(scroll, text="Output Formats", anchor="w").grid(row=8, column=0, sticky="w", **pad)
        fmt_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        fmt_frame.grid(row=9, column=0, sticky="w", **pad)
        self._fmt_txt = ctk.CTkCheckBox(fmt_frame, text=".txt transcript")
        self._fmt_srt = ctk.CTkCheckBox(fmt_frame, text=".srt subtitles")
        self._fmt_ai = ctk.CTkCheckBox(fmt_frame, text="AI summary (.md)")
        self._fmt_txt.pack(side="left", padx=8)
        self._fmt_srt.pack(side="left", padx=8)
        self._fmt_ai.pack(side="left", padx=8)
        if "txt" in self._cfg.output_formats:
            self._fmt_txt.select()
        if "srt" in self._cfg.output_formats:
            self._fmt_srt.select()
        if "ai" in self._cfg.output_formats:
            self._fmt_ai.select()

        ctk.CTkLabel(scroll, text="Device", anchor="w").grid(row=10, column=0, sticky="w", **pad)
        self._device_var = ctk.StringVar(value=self._cfg.default_device)
        ctk.CTkOptionMenu(scroll, values=["cpu", "cuda", "auto"],
                          variable=self._device_var).grid(row=11, column=0, sticky="ew", **pad)

        # Save/Cancel pinned at bottom, outside scroll
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(4, 12))
        ctk.CTkButton(btn_frame, text="Save", command=self._save).pack(side="right", padx=4)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="right")

        self._on_provider_change(self._provider_var.get())

    def _on_provider_change(self, value):
        is_api = value in ("claude", "openai")
        is_ollama = value == "ollama"
        state_api = "normal" if is_api else "disabled"
        state_ollama = "normal" if is_ollama else "disabled"
        self._api_key_entry.configure(state=state_api)
        self._ollama_entry.configure(state=state_ollama)

    def _save(self):
        if self._provider_var.get() == "ollama":
            from urllib.parse import urlparse
            from tkinter import messagebox
            url = self._ollama_var.get()
            try:
                hostname = urlparse(url).hostname or ""
            except Exception:
                hostname = ""
            if hostname not in ("localhost", "127.0.0.1", "::1", ""):
                if not messagebox.askyesno(
                    "External Ollama URL",
                    f"The Ollama URL points to a non-local host ({hostname}).\n"
                    "Your transcripts will be sent to that server. Continue?"
                ):
                    return

        formats = []
        if self._fmt_txt.get():
            formats.append("txt")
        if self._fmt_srt.get():
            formats.append("srt")
        if self._fmt_ai.get():
            formats.append("ai")
        if not formats:
            formats = ["txt"]

        self._cfg.ai_provider = self._provider_var.get()
        self._cfg.api_key = self._api_key_var.get()
        self._cfg.ollama_url = self._ollama_var.get()
        self._cfg.custom_ai_prompt = self._prompt_box.get("0.0", "end").strip()
        self._cfg.output_formats = formats
        self._cfg.default_device = self._device_var.get()
        save_config(self._cfg)
        self.destroy()
