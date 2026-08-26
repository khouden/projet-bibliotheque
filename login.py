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
        self.root.title("Bibliothèque - Login")
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
        self.password.insert(0, "mot de passe")
        self.password.bind('<FocusIn>', self.on_enterp)
        self.password.bind('<FocusOut>', self.on_leavep)

        self.underline = Frame(self.frame, width=255, height=2, bg=prColor)
        self.underline.place(relx=0.5, rely=0.5, anchor="center")

        # login button
        self.loginButton = Button(self.frame, width=29, pady=5, text="connexion", bg=prColor, fg="white", relief="solid",
                                  activebackground=bgColor, activeforeground=prColor, font=('Rubik', 11), cursor="hand2",
                                  command=self.login)
        self.loginButton.place(relx=0.5, rely=0.7, anchor="center")

        # creation
        self.labelCreator = Label(self.contentframe, text="Crée par : Abdellah khouden et Abderrahim bensaid",
                                  font=('Rubik', 11), bg=bgColor)
        self.labelCreator.place(x=50, y=490)
        self.labelCreator = Label(self.contentframe, text="et Othman Elhyane",
                                  font=('Rubik', 11), bg=bgColor)
        self.labelCreator.place(x=120, y=520)

        # encadre
        self.labelEncadre = Label(self.contentframe, text="Encadré par : Mr.Abdellah sair",
                                  font=('Rubik', 11), bg=bgColor)
        self.labelEncadre.place(x=530, y=490)

    def on_enterp(self, e):
        self.password.config(show="*")
        self.password.delete(0, 'end')

    def on_leavep(self, e):
        name = self.password.get()
        if name == '':
            self.password.config(show="")
            self.password.insert(0, 'mot de passe')

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
            messagebox.showerror("Invalid informations", "le mot de passe est incorrecte")


class FirstSetup:
    def __init__(self, root):
        self.root = root
        self.root.title("Bibliothèque - Première utilisation")
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
        self.title = Label(self.frame, text="Première utilisation", fg=prColor, font=('Rubik', 20), bg=bgColor)
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        self.subtitle = Label(self.frame, text="Définissez votre mot de passe :", fg=prColor,
                              font=('Rubik', 12), bg=bgColor)
        self.subtitle.place(relx=0.5, rely=0.25, anchor="center")

        # mot de passe
        self.password = Entry(self.frame, width=25, fg=prColor, border=0, font=('Rubik', 12), bg=bgColor, show="*")
        self.password.place(relx=0.5, rely=0.42, anchor="center")
        self.password.insert(0, "mot de passe")
        self.password.bind('<FocusIn>', self.on_enterp)
        self.password.bind('<FocusOut>', self.on_leavep)

        self.underline = Frame(self.frame, width=255, height=2, bg=prColor)
        self.underline.place(relx=0.5, rely=0.47, anchor="center")

        # confirmation
        self.confirm = Entry(self.frame, width=25, fg=prColor, border=0, font=('Rubik', 12), bg=bgColor, show="*")
        self.confirm.place(relx=0.5, rely=0.58, anchor="center")
        self.confirm.insert(0, "confirmer le mot de passe")
        self.confirm.bind('<FocusIn>', self.on_enterc)
        self.confirm.bind('<FocusOut>', self.on_leavec)

        self.underline2 = Frame(self.frame, width=255, height=2, bg=prColor)
        self.underline2.place(relx=0.5, rely=0.63, anchor="center")

        # button
        self.setupButton = Button(self.frame, width=29, pady=5, text="Définir le mot de passe", bg=prColor, fg="white",
                                  relief="solid", activebackground=bgColor, activeforeground=prColor,
                                  font=('Rubik', 11), cursor="hand2", command=self.define_password)
        self.setupButton.place(relx=0.5, rely=0.8, anchor="center")

    def on_enterp(self, e):
        self.password.delete(0, 'end')

    def on_leavep(self, e):
        if self.password.get() == '':
            self.password.insert(0, 'mot de passe')

    def on_enterc(self, e):
        self.confirm.delete(0, 'end')

    def on_leavec(self, e):
        if self.confirm.get() == '':
            self.confirm.insert(0, 'confirmer le mot de passe')

    def define_password(self):
        password = self.password.get().strip()
        confirm = self.confirm.get().strip()
        if password in ("mot de passe", ""):
            messagebox.showerror("Erreur", "Le mot de passe est obligatoire.")
            return
        if len(password) < 4:
            messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 4 caractères.")
            return
        if confirm in ("confirmer le mot de passe", "") or password != confirm:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
            return
        set_password(password)
        messagebox.showinfo("Success", "Votre mot de passe a été défini avec succès.")
        self.contentframe.pack_forget()
        MainMenu(self.root)
