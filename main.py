from tkinter import *
from login import Login
from mainMenu import MainMenu
from db import init_db

init_db()

root = Tk()
root.geometry('925x600')
Login(root)
#MainMenu(root)
root.mainloop()