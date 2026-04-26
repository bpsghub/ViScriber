from src.gui.app import App
from src.gui.first_run import maybe_show_first_run


def main():
    app = App()
    maybe_show_first_run(app)
    app.show_main()
    app.mainloop()


if __name__ == "__main__":
    main()
