from tkinter import *
from tkinter import ttk, messagebox
from db import connect, verify_password, set_password
from paths import asset_path
from mainMenu import MainMenu

bgColor = "#00c9a7"
prColor = "#12192c"
textHolderColor = "#7a7e89"


class Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Library - Login")
        self.root.geometry('925x600')
        self.root.configure(background=bgColor)
        self.root.resizable(False, False)
        self.icon_image = PhotoImage(file=asset_path("icon.png"))
        self.root.iconphoto(False, self.icon_image)

        # content frame
        self.contentframe = Frame(self.root, bg=bgColor, padx=50, pady=50)
        self.contentframe.pack(expand=True, fill="both")

        # login image
        self.img = PhotoImage(file=asset_path('login2.png'))
        self.imgLabel = Label(self.contentframe, image=self.img, bg=bgColor)
        self.imgLabel.image = self.img
        self.imgLabel.place(x=20, y=20)

        # login frame
        self.frame = Frame(self.contentframe, width=350, height=350, bg=bgColor)
        self.frame.place(x=450, y=30)

        # title
        self.title = Label(self.frame, text="Login", fg=prColor, font=('Rubik', 23), bg=bgColor)
        self.title.place(relx=0.5, rely=0.15, anchor="center")

        # mot de passe
        self.password = Entry(self.frame, width=25, fg=prColor, border=0, font=('Rubik', 12), bg=bgColor)
        self.password.place(relx=0.5, rely=0.45, anchor="center")
        self.password.insert(0, "password")
        self.password.bind('<FocusIn>', self.on_enterp)
        self.password.bind('<FocusOut>', self.on_leavep)
        self.password.bind('<Return>', self.on_return)

        self.underline = Frame(self.frame, width=255, height=2, bg=prColor)
        self.underline.place(relx=0.5, rely=0.5, anchor="center")

        # login button
        self.loginButton = Button(self.frame, width=29, pady=5, text="Login", bg=prColor, fg="white", relief="solid",
                                  activebackground=bgColor, activeforeground=prColor, font=('Rubik', 11), cursor="hand2",
                                  command=self.login)
        self.loginButton.place(relx=0.5, rely=0.7, anchor="center")

        # credits
        self.labelCreator = Label(self.contentframe, text="Created by: Abdellah Khouden & Abderrahim Bensaid",
                                  font=('Rubik', 11), bg=bgColor)
        self.labelCreator.place(x=50, y=490)
        self.labelCreator = Label(self.contentframe, text="and Othman Elhyane",
                                  font=('Rubik', 11), bg=bgColor)
        self.labelCreator.place(x=120, y=520)

        # supervisor
        self.labelEncadre = Label(self.contentframe, text="Supervised by: Mr. Abdellah Sair",
                                  font=('Rubik', 11), bg=bgColor)
        self.labelEncadre.place(x=530, y=490)

    def on_enterp(self, e):
        self.password.config(show="*")
        self.password.delete(0, 'end')

    def on_leavep(self, e):
        name = self.password.get()
        if name == '':
            self.password.config(show="")
            self.password.insert(0, 'password')

    def on_return(self, e):
        self.login()

    def login(self):
        password = self.password.get()
        connection = connect()

        cursor = connection.cursor()
        cursor.execute("SELECT password FROM login WHERE id = 1")
        data = cursor.fetchone()
        cursor.close()
        connection.close()
        if data and verify_password(password, data[0]):
            self.contentframe.pack_forget()
            MainMenu(self.root)
        else:
            messagebox.showerror("Error", "Incorrect password.")


class FirstSetup:
    def __init__(self, root):
        self.root = root
        self.root.title("Library - First Use")
        self.root.geometry('925x600')
        self.root.configure(background=bgColor)
        self.root.resizable(False, False)
        self.icon_image = PhotoImage(file=asset_path("icon.png"))
        self.root.iconphoto(False, self.icon_image)

        # content frame
        self.contentframe = Frame(self.root, bg=bgColor, padx=50, pady=50)
        self.contentframe.pack(expand=True, fill="both")

        # setup frame
        self.frame = Frame(self.contentframe, width=350, height=350, bg=bgColor)
        self.frame.place(x=450, y=30)

        # title
        self.title = Label(self.frame, text="First use", fg=prColor, font=('Rubik', 20), bg=bgColor)
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        self.subtitle = Label(self.frame, text="Set your password:", fg=prColor,
                              font=('Rubik', 12), bg=bgColor)
        self.subtitle.place(relx=0.5, rely=0.25, anchor="center")

        # mot de passe
        self.password = Entry(self.frame, width=25, fg=prColor, border=0, font=('Rubik', 12), bg=bgColor, show="*")
        self.password.place(relx=0.5, rely=0.42, anchor="center")
        self.password.insert(0, "password")
        self.password.bind('<FocusIn>', self.on_enterp)
        self.password.bind('<FocusOut>', self.on_leavep)
        self.password.bind('<Return>', self.on_next_field)

        self.underline = Frame(self.frame, width=255, height=2, bg=prColor)
        self.underline.place(relx=0.5, rely=0.47, anchor="center")

        # confirmation
        self.confirm = Entry(self.frame, width=25, fg=prColor, border=0, font=('Rubik', 12), bg=bgColor, show="*")
        self.confirm.place(relx=0.5, rely=0.58, anchor="center")
        self.confirm.insert(0, "confirm password")
        self.confirm.bind('<FocusIn>', self.on_enterc)
        self.confirm.bind('<FocusOut>', self.on_leavec)
        self.confirm.bind('<Return>', self.on_submit)

        self.underline2 = Frame(self.frame, width=255, height=2, bg=prColor)
        self.underline2.place(relx=0.5, rely=0.63, anchor="center")

        # button
        self.setupButton = Button(self.frame, width=29, pady=5, text="Set password", bg=prColor, fg="white",
                                  relief="solid", activebackground=bgColor, activeforeground=prColor,
                                  font=('Rubik', 11), cursor="hand2", command=self.define_password)
        self.setupButton.place(relx=0.5, rely=0.8, anchor="center")

    def on_enterp(self, e):
        self.password.delete(0, 'end')

    def on_leavep(self, e):
        if self.password.get() == '':
            self.password.insert(0, 'password')

    def on_enterc(self, e):
        self.confirm.delete(0, 'end')

    def on_next_field(self, e):
        self.confirm.focus_set()

    def on_submit(self, e):
        self.define_password()

    def on_leavec(self, e):
        if self.confirm.get() == '':
            self.confirm.insert(0, 'confirm password')

    def define_password(self):
        password = self.password.get().strip()
        confirm = self.confirm.get().strip()
        if password in ("password", ""):
            messagebox.showerror("Error", "Password is required.")
            return
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters long.")
            return
        if confirm in ("confirm password", "") or password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        set_password(password)
        messagebox.showinfo("Success", "Your password has been set successfully.")
        self.contentframe.pack_forget()
        MainMenu(self.root)
