from tkinter import *
from db import init_db, needs_setup
from login import Login, FirstSetup

init_db()

root = Tk()
root.geometry('925x600')
if needs_setup():
    FirstSetup(root)
else:
    Login(root)
root.mainloop()