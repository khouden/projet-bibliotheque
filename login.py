from tkinter import *
from tkinter import ttk,messagebox
from db import connect, verify_password
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
        self.icon_image = PhotoImage(file=asset_path("icon.png"))  # Replace with your icon file path
        self.root.iconphoto(False, self.icon_image)
        
        #content frame
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
        self.title.place(relx=0.5, rely=0.1, anchor="center")

        #nom utilisateur
        self.user = Entry(self.frame, width=25, fg=prColor, border=0,font=('Rubik', 12) ,bg=bgColor)
        self.user.place(relx=0.5, rely=0.4, anchor="center")
        self.user.insert(0,"nom d'utilisateur")
        self.user.bind('<FocusIn>', self.on_enter)
        self.user.bind('<FocusOut>', self.on_leave)

        self.underline = Frame(self.frame, width=255, height=2, bg=prColor)
        self.underline.place(relx=0.5, rely=0.45, anchor="center")

        #mot de passe
        self.password = Entry(self.frame, width=25, fg=prColor, border=0,font=('Rubik', 12) ,bg=bgColor)
        self.password.place(relx=0.5, rely=0.6, anchor="center")
        self.password.insert(0,"mot de passe")
        self.password.bind('<FocusIn>', self.on_enterp)
        self.password.bind('<FocusOut>', self.on_leavep)

        self.underline = Frame(self.frame, width=255, height=2, bg=prColor)
        self.underline.place(relx=0.5, rely=0.65, anchor="center")

        # login button

        self.loginButton = Button(self.frame, width=29, pady=5, text="connexion", bg=prColor, fg="white", relief="solid",
                                    activebackground=bgColor,  activeforeground=prColor, font=('Rubik', 11) , cursor="hand2",
                                    command=self.login)
        self.loginButton.place(relx=0.5, rely=0.9, anchor="center")

        #cration
        self.labelCreator = Label(self.contentframe, text="Crée par : Abdellah khouden et Abderrahim bensaid",
                                  font=('Rubik', 11), bg=bgColor)
        self.labelCreator.place(x=50, y=490)
        self.labelCreator = Label(self.contentframe, text="et Othman Elhyane",
                                  font=('Rubik', 11), bg=bgColor)
        self.labelCreator.place(x=120, y=520)

        #encadre
        self.labelEncadre = Label(self.contentframe, text="Encadré par : Mr.Abdellah sair",
                                  font=('Rubik', 11), bg=bgColor)
        self.labelEncadre.place(x=530, y=490)
    def on_enter(self,e):
        self.user.delete(0, 'end')
    def on_leave(self, e):
        name = self.user.get()
        if name == '':
            self.user.insert(0,'nom d\'utilisateur')
    def on_enterp(self,e):
        self.password.config(show="*")
        self.password.delete(0, 'end')
    def on_leavep(self, e):
        name = self.password.get()
        if name == '':
            self.password.config(show="")
            self.password.insert(0, 'mot de passe')

    def login(self):
        username = self.user.get()
        password = self.password.get()
        connection = connect()

        cursor = connection.cursor()
        cursor.execute("Select * from login where username=?", (username,))
        data = cursor.fetchone()
        cursor.close()
        connection.close()
        if data and verify_password(password, data[1]):
            self.contentframe.pack_forget()
            MainMenu(self.root)
        else:
            messagebox.showerror("Invalid informations", "le nom d'utilisateur ou le mot de passe est incorrecte")

