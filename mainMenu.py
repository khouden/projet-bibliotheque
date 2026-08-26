from tkinter import *
from tkinter import ttk, messagebox

from paths import asset_path
from livre import *
from adherent import *
from emprunt import *


#les coleurs:
bgColor = "#00c9a7"
prColor = "#12192c"
textHolderColor = "#7a7e89"


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.resizable(False, False)
        # ajouter style au combobox
        self.root.option_add('*TCombobox*Listbox.selectBackground', prColor)
        self.root.option_add("*TCombobox*Listbox*Font", ("Rubik", 12))


        self.create_menus()
        self.home()



    def home(self):
        clearPage(self.root)
        self.root.title("Library - Home")
        self.contentframe = Frame(self.root, bg=bgColor)
        self.contentframe.pack(expand=True, fill="both")
        self.bg_image = PhotoImage(file=asset_path("background.png"))

        self.background_label = Label(self.contentframe, image=self.bg_image)
        self.background_label.pack()

        # books combobox
        self.livre_combobox = ttk.Combobox(self.contentframe, font=('Rubik', 12), state="readonly", width=18)
        self.livre_combobox.place(x= 120, y = 430)
        self.livre_combobox["values"]= ['list books', 'add book', 'edit books']
        self.livre_combobox.bind("<<ComboboxSelected>>", self.choisir_livre)

        # members combobox
        self.adherent_combobox = ttk.Combobox(self.contentframe, font=('Rubik', 12), state="readonly", width=18)
        self.adherent_combobox.place(x=363, y=430)
        self.adherent_combobox["values"]= ['list members', 'add member', 'edit member']
        self.adherent_combobox.bind("<<ComboboxSelected>>", self.choisir_adherent)

        # loans combobox
        self.emprunt_combobox = ttk.Combobox(self.contentframe, font=('Rubik', 12), state="readonly", width=18)
        self.emprunt_combobox.place(x=606, y=430)
        self.emprunt_combobox["values"] = ['list loans', 'borrow a book', 'return a book', 'edit loans']
        self.emprunt_combobox.bind("<<ComboboxSelected>>", self.choisir_emprunt)

    def create_menus(self):
        self.menu = Menu(self.root, bg=prColor, fg="white", activebackground=prColor, activeforeground="white")
        self.root.config(menu=self.menu)

        self.options_menu = Menu(self.menu, tearoff=0, bg=prColor, fg="white", activebackground=bgColor,
                                 activeforeground="white", font=('Rubik', 12))

        self.menu.add_cascade(label="Options", menu=self.options_menu)
        self.options_menu.add_command(label="Home", command=self.home)
        self.options_menu.add_command(label="Change password", command=self.change_password)
        self.options_menu.add_separator()
        self.options_menu.add_command(label="Quit", command=self.quitter)

        self.livre_menu = Menu(self.menu, tearoff=0, bg=prColor, fg="white", activebackground=bgColor,
                               activeforeground="white", font=('Rubik', 12))

        self.menu.add_cascade(label="Books", menu=self.livre_menu)
        self.livre_menu.add_command(label="List books", command=self.lister_livres)
        self.livre_menu.add_command(label="Add book", command=self.ajouter_livres)
        self.livre_menu.add_command(label="Edit book", command=self.modifier_livres)
        # self.livre_menu.add_command(label="Supprimer livre", command=self.modifier_livres)

        self.adherent_menu = Menu(self.menu, tearoff=0, bg=prColor, fg="white", activebackground=bgColor,
                                  activeforeground="white", font=('Rubik', 12))
        self.menu.add_cascade(label="Members", menu=self.adherent_menu)
        self.adherent_menu.add_command(label="List members", command=self.lister_adherent)
        self.adherent_menu.add_command(label="Add member", command=self.ajouter_adherent)
        self.adherent_menu.add_command(label="Edit member", command=self.modifier_adherent)
        self.emprunt_menu = Menu(self.menu, tearoff=0, bg=prColor, fg="white", activebackground=bgColor,
                                 activeforeground="white", font=('Rubik', 12))

        self.menu.add_cascade(label="Loans", menu=self.emprunt_menu)
        self.emprunt_menu.add_command(label="List loans", command=self.lister_emprunt)

        # new loan submenu
        self.prendre_menu = Menu(self.emprunt_menu, tearoff=0, bg=prColor, fg="white", activebackground=bgColor,
                                 activeforeground="white", font=('Rubik', 12))
        self.emprunt_menu.add_cascade(label="New loan", menu=self.prendre_menu)

        self.prendre_menu.add_command(label="Borrow a book", command=self.prendre_emprunt)

        self.prendre_menu.add_command(label="Return a book", command=self.retourner_emprunt)

        self.emprunt_menu.add_command(label="Edit loan", command=self.modifier_emprunts)

        # emprunt_menu.add_command(label="Modifier", command=lambda: EmpruntManagement(self.root, self.app).modify_emprunt())

        # content frame
        self.contentframe = Frame(self.root, bg=bgColor, padx=50, pady=50)
        self.contentframe.pack(expand=True, fill="both")

    def hide_menu_bar(self):
        # Iterate through all the menus in the root window and forget them
        if self.menu:
            self.menu.delete(0, "end")

    # options

    def quitter(self):
        if tkinter.messagebox.askyesno("Quit", "Do you want to quit?"):
            exit()

    def change_password(self):
        self.clear_widgets()
        from login import ChangePassword
        ChangePassword(self.root)



    # combobox navigation
    def choisir_livre(self, event):
        match self.livre_combobox.get():
            case "list books":
                self.lister_livres()
            case "add book":
                self.ajouter_livres()
            case "edit books":
                self.modifier_livres()
    def choisir_adherent(self, event):
        match self.adherent_combobox.get():
            case "list members":
                self.lister_adherent()
            case "add member":
                self.ajouter_adherent()
            case "edit member":
                self.modifier_adherent()
    def choisir_emprunt(self, event):
        match self.emprunt_combobox.get():
            case "list loans":
                self.lister_emprunt()
            case "borrow a book":
                self.prendre_emprunt()
            case "return a book":
                self.retourner_emprunt()
            case "edit loans":
                self.modifier_emprunts()
    # livre
    def lister_livres(self):
        self.clear_widgets()
        AfficherLivres(self.root)
    def ajouter_livres(self):
        self.clear_widgets()
        AjouterLivre(self.root)
    def modifier_livres(self):
        self.clear_widgets()
        ModifierLivre(self.root)

    # adherent
    def lister_adherent(self):
        self.clear_widgets()
        AfficherAdherents(self.root)

    def ajouter_adherent(self):
        self.clear_widgets()
        AjouterAdherent(self.root)

    def modifier_adherent(self):
        self.clear_widgets()
        ModifierAdherent(self.root)

    # emprunt
    def lister_emprunt(self):
        self.clear_widgets()
        AfficherEmprunts(self.root)

    def prendre_emprunt(self):
        self.clear_widgets()
        PrendreEmprunt(self.root)

    def retourner_emprunt(self):
        self.clear_widgets()
        RetourneEmprunt(self.root)

    def modifier_emprunts(self):
        self.clear_widgets()
        from emprunt import ModifierEmprunt
        ModifierEmprunt(self.root)

    # fermer le widndow actuel
    def clear_widgets(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, Frame):
                widget.destroy()

