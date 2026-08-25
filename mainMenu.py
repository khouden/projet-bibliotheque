from tkinter import *
from tkinter import ttk, messagebox

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
        self.root.title("Bibliothèque - Main")
        self.contentframe = Frame(self.root, bg=bgColor)
        self.contentframe.pack(expand=True, fill="both")
        self.bg_image = PhotoImage(file="background.png")

        self.background_label = Label(self.contentframe, image=self.bg_image)
        self.background_label.pack()

        # livres combobox
        self.livre_combobox = ttk.Combobox(self.contentframe, font=('Rubik', 12), state="readonly", width=18)
        self.livre_combobox.place(x= 120, y = 430)
        self.livre_combobox["values"]= ['afficher livres', 'ajouter un livre', 'modifier livres']
        self.livre_combobox.bind("<<ComboboxSelected>>", self.choisir_livre)

        # adherents combobox
        self.adherent_combobox = ttk.Combobox(self.contentframe, font=('Rubik', 12), state="readonly", width=18)
        self.adherent_combobox.place(x=363, y=430)
        self.adherent_combobox["values"]= ['afficher adherents', 'ajouter adherent', 'modifier adherent']
        self.adherent_combobox.bind("<<ComboboxSelected>>", self.choisir_adherent)

        # emprunts combobox
        self.emprunt_combobox = ttk.Combobox(self.contentframe, font=('Rubik', 12), state="readonly", width=18)
        self.emprunt_combobox.place(x=606, y=430)
        self.emprunt_combobox["values"] = ['afficher emprunts', 'prendre un livre', 'retourner un livre']
        self.emprunt_combobox.bind("<<ComboboxSelected>>", self.choisir_emprunt)

    def create_menus(self):
        self.menu = Menu(self.root, bg=prColor, fg="white", activebackground=prColor, activeforeground="white")
        self.root.config(menu=self.menu)

        self.options_menu = Menu(self.menu, tearoff=0, bg=prColor, fg="white", activebackground=bgColor,
                                 activeforeground="white", font=('Rubik', 12))

        self.menu.add_cascade(label="options", menu=self.options_menu)
        self.options_menu.add_command(label="Acceuil", command=self.home)
        self.options_menu.add_separator()
        self.options_menu.add_command(label="Quitter", command=self.quitter)

        self.livre_menu = Menu(self.menu, tearoff=0, bg=prColor, fg="white", activebackground=bgColor,
                               activeforeground="white", font=('Rubik', 12))

        self.menu.add_cascade(label="Livre", menu=self.livre_menu)
        self.livre_menu.add_command(label="Lister livres", command=self.lister_livres)
        self.livre_menu.add_command(label="Ajouter livre", command=self.ajouter_livres)
        self.livre_menu.add_command(label="Modifier livre", command=self.modifier_livres)
        # self.livre_menu.add_command(label="Supprimer livre", command=self.modifier_livres)

        self.adherent_menu = Menu(self.menu, tearoff=0, bg=prColor, fg="white", activebackground=bgColor,
                                  activeforeground="white", font=('Rubik', 12))
        self.menu.add_cascade(label="Adherent", menu=self.adherent_menu)
        self.adherent_menu.add_command(label="Lister adherents", command=self.lister_adherent)
        self.adherent_menu.add_command(label="Ajouter adherent", command=self.ajouter_adherent)
        self.adherent_menu.add_command(label="Modifier adherent", command=self.modifier_adherent)
        self.emprunt_menu = Menu(self.menu, tearoff=0, bg=prColor, fg="white", activebackground=bgColor,
                                 activeforeground="white", font=('Rubik', 12))

        self.menu.add_cascade(label="Emprunt", menu=self.emprunt_menu)
        self.emprunt_menu.add_command(label="Lister emprunts", command=self.lister_emprunt)

        # prendre livre
        self.prendre_menu = Menu(self.emprunt_menu, tearoff=0, bg=prColor, fg="white", activebackground=bgColor,
                                 activeforeground="white", font=('Rubik', 12))
        self.emprunt_menu.add_cascade(label="Ajouter emprunt", menu=self.prendre_menu)

        self.prendre_menu.add_command(label="Prendre un livre", command=self.prendre_emprunt)

        self.prendre_menu.add_command(label="Retourner un livre", command=self.retourner_emprunt)

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
        if tkinter.messagebox.askyesno("Quitter", "Voulez vous quitter ?"):
            exit()



    # choisir une choix
    def choisir_livre(self, event):
        match self.livre_combobox.get():
            case "afficher livres":
                self.lister_livres()
            case "ajouter un livre":
                self.ajouter_livres()
            case "modifier livres":
                self.modifier_livres()
    def choisir_adherent(self, event):
        match self.adherent_combobox.get():
            case "afficher adherents":
                self.lister_adherent()
            case "ajouter adherent":
                self.ajouter_adherent()
            case "modifier adherent":
                self.modifier_adherent()
    def choisir_emprunt(self, event):
        match self.emprunt_combobox.get():
            case "afficher emprunts":
                self.lister_emprunt()
            case "prendre un livre":
                self.prendre_emprunt()
            case "retourner un livre":
                self.retourner_emprunt()
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

    # fermer le widndow actuel
    def clear_widgets(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, Frame):
                widget.destroy()

