import os
import sys
import traceback
from tkinter import *
from tkinter import messagebox
from db import init_db, needs_setup
from login import Login, FirstSetup


def app_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def log_and_report(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    try:
        with open(os.path.join(app_base_dir(), "error.log"), "a", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
            f.write("\n")
    except OSError:
        pass
    try:
        messagebox.showerror(
            "Unexpected error",
            "An unexpected error occurred.\n"
            "Details were written to error.log\n\n"
            f"{exc_type.__name__}: {exc_value}")
    except Exception:
        pass


sys.excepthook = log_and_report


def start_app():
    global root
    try:
        init_db()
    except Exception:
        log_and_report(*sys.exc_info())
        sys.exit(1)

    root = Tk()
    root.geometry('925x600')
    root.report_callback_exception = lambda t, v, b: log_and_report(t, v, b)

    if needs_setup():
        FirstSetup(root)
    else:
        Login(root)
    root.mainloop()


if __name__ == "__main__":
    start_app()
