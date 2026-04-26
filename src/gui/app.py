import customtkinter as ctk
from src.config import load_config, save_config

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        try:
            from tkinterdnd2 import TkinterDnD
            TkinterDnD._require(self)
        except Exception:
            pass
        self.title("Video Transcriber")
        self.geometry("720x540")
        self.minsize(640, 480)
        self.cfg = load_config()
        self._current_screen = None

    def show_screen(self, screen_frame: ctk.CTkFrame):
        if self._current_screen is not None:
            self._current_screen.grid_forget()
        screen_frame.grid(row=0, column=0, sticky="nsew")
        self._current_screen = screen_frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def show_main(self):
        from src.gui.main_screen import MainScreen
        self.show_screen(MainScreen(self))

    def show_progress(self, files, options):
        from src.gui.progress_screen import ProgressScreen
        self.show_screen(ProgressScreen(self, files=files, options=options))

    def show_results(self, output_files):
        from src.gui.main_screen import ResultsScreen
        self.show_screen(ResultsScreen(self, output_files=output_files))
