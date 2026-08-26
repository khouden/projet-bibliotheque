import tkinter.messagebox
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from db import connect
import re

bgColor = "#00c9a7"
prColor = "#12192c"
prLightColor = "#c4fff3"
textHolderColor = "#7a7e89"


# validation fonction
def valider_donnees(nom, tel, email):
    # Vérification du nom (au moins 2 lettres alphabétiques)
    if not re.match(r'^[a-zA-Z\s]{2,}$', nom):
        if len(nom) == 0:
            messagebox.showerror("Erreur", "Le nom est obligatoire.")
        else:
            messagebox.showerror("Erreur", "Le nom doit contenir au moins 2 lettres alphabétiques.")
        return False

    # Vérification du téléphone (optionnel, format international)
    if tel:
        if not re.match(r'^\+?[\d\s\-\(\)\.]+$', tel.strip()):
            messagebox.showerror("Erreur", "Le numéro de téléphone contient des caractères invalides.")
            return False
        chiffres = re.sub(r'\D', '', tel)
        if not 7 <= len(chiffres) <= 15:
            messagebox.showerror("Erreur", "Le numéro de téléphone doit contenir entre 7 et 15 chiffres.")
            return False

    # Vérification de l'email (format email)
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        if len(email) == 0:
            messagebox.showerror("Erreur", "L'email est obligatoire.")
        else:
            messagebox.showerror("Erreur", "L'email doit être valide.")
        return False

    return True


def clearPage(root):
    for widget in root.winfo_children():
        if isinstance(widget, Frame):
            widget.destroy()


class AfficherEmprunts():
    def __init__(self, root):
        self.root = root
        self.root.config(bg=bgColor)
        self.root.title("Bibliothèque - Emprunt")

        # content frame
        self.contentframe = Frame(self.root, bg=bgColor, padx=50, pady=50)
        self.contentframe.pack(expand=True, fill="both")
        self.afficherTable()

        # style

        self.style = ttk.Style()
        self.style.configure("Custom.Treeview",
                             background="white",
                             foreground="black",
                             rowheight=25,
                             fieldbackground="white",
                             font=('Rubik', 10))

        self.style.configure("Custom.Treeview.Heading",
                             background="red",
                             foreground="black",
                             font=('Rubik', 11))

        self.style.map('Custom.Treeview',
                       background=[('selected', bgColor)],
                       foreground=[('selected', 'white')])

    def afficherTable(self):
        connection = connect()

        cursor = connection.cursor()
        cursor.execute("select e.idEmp, a.nom, l.titre, e.dateemprunt, e.status from emprunt e "
                       "join adherent a on e.idAdh = a.idAdh join livre l on e.idLiv = l.idLiv order by e.idEmp")
        data = cursor.fetchall()
        columns = ('ID', 'Nom Adherent', 'Titre de Livre', 'Date emprunt', 'Status')
        self.tree = ttk.Treeview(self.contentframe, columns=columns, show="headings", style="Custom.Treeview")
        self.tree.tag_configure("oddrow", background="lightblue")

        # Create a scrollbar
        self.tree_scroll = ttk.Scrollbar(self.tree)
        self.tree_scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.config(command=self.tree.yview)

        for col in columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.trierColumn(self.tree, _col, False))
            self.tree.column(col, width=100, stretch=True)

        for i, item in enumerate(data):
            self.tree.insert("", "end", values=item, tags=("oddrow" if i % 2 == 1 else ""))

        self.tree.pack(fill="both", expand=True)
        cursor.close()
        connection.close()
        self.rechercheAdherent(self.tree)

    def trierColumn(self, treeview, col, reverse):
        l = [(treeview.set(k, col), k) for k in treeview.get_children('')]

        # Sort the list
        try:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            l.sort(key=lambda t: t[0], reverse=reverse)

        # Reorder items in the treeview
        for index, (val, k) in enumerate(l):
            treeview.move(k, '', index)

        for i, child in enumerate(self.tree.get_children('')):
            if i % 2 == 0:
                self.tree.item(child, tags=("oddrow",))
            else:
                self.tree.item(child, tags=())

        treeview.heading(col, text=col, command=lambda: self.trierColumn(treeview, col, not reverse))

    def rechercheAdherent(self, tree):
        search_frame = Frame(self.contentframe, bg=bgColor)
        search_frame.pack(fill="x", padx=5, pady=5)

        search_label = Label(search_frame, text="Search:", bg=bgColor, font=('Rubik', 12))
        search_label.pack(side="left")

        search_entry = Entry(search_frame, font=('Rubik', 11))
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        def search_tree():
            query = search_entry.get()
            connection = connect()

            cursor = connection.cursor()
            cursor.execute(
                "SELECT e.idEmp, a.nom, l.titre, e.dateemprunt, e.status FROM emprunt e "
                "JOIN adherent a ON e.idAdh = a.idAdh JOIN livre l ON e.idLiv = l.idLiv "
                "WHERE (COALESCE(e.idEmp,'') || ' ' || COALESCE(a.nom,'') || ' ' || COALESCE(l.titre,'') || ' ' || "
                "COALESCE(e.dateemprunt,'') || ' ' || COALESCE(e.status,'')) LIKE ?",
                ('%' + query + '%',))
            data = cursor.fetchall()

            tree.delete(*tree.get_children())
            for i in range(len(data)):
                item = data[i]
                self.tree.insert("", "end", values=item, tags=("oddrow" if i % 2 == 1 else ""))

        search_button = Button(search_frame, text="Search", command=search_tree, font=('Rubik', 12), bg=prColor,
                               relief="solid", cursor="hand2", fg="white", activebackground=bgColor,
                               activeforeground="black")
        search_button.pack(side="right")


class PrendreEmprunt():
    def __init__(self, root):
        self.root = root
        self.root.config(bg=bgColor)
        self.root.title("Bibliothèque - Ajouter Emprunt - Prendre Livre")

        # ajouter style au combobox
        self.root.option_add('*TCombobox*Listbox.selectBackground', prColor)
        self.root.option_add("*TCombobox*Listbox*Font", ("Rubik", 12))

        # content frame
        self.contentframe = Frame(self.root, bg=bgColor)
        self.contentframe.pack(expand=True, fill="both")

        # image
        self.ajouteimage = PhotoImage(file="ajouter_emprunt.png")
        self.labelImage = Label(self.contentframe, image=self.ajouteimage, border=0)
        self.labelImage.image = self.ajouteimage
        self.labelImage.place(x=0, y=0)

        self.frame = Frame(self.contentframe, width=400, height=350, bg=bgColor)
        self.frame.place(x=460, y=90)

        self.form_options = Frame(self.frame, bg=bgColor, height=300, width=300)
        self.form_options.pack(padx=10, pady=10)

        # title
        self.title = Label(self.form_options, text="Prendre un livre", fg=prColor, font=('Rubik', 23), bg=bgColor)
        self.title.grid(row=0, column=1, columnspan=2, rowspan=2, padx=10, pady=10, sticky="s")

        # adherent combobox
        self.adherent_label = Label(self.form_options, text="Adherent:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        self.adherent_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.adherent_combobox = ttk.Combobox(self.form_options, font=('Rubik', 12), width=30, state="readonly")
        self.adherent_combobox.grid(row=2, column=1, padx=10, pady=10, sticky="w")


        # livre combobox
        self.livre_label = Label(self.form_options, text="Livre:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        self.livre_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.livre_combobox = ttk.Combobox(self.form_options, font=('Rubik', 12), state="readonly", width=30)
        self.livre_combobox.grid(row=3, column=1, padx=10, pady=10, sticky="w")



        # date Entry
        self.adherent_label = Label(self.form_options, text="Date:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        self.adherent_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.date_entry = DateEntry(self.form_options, width=30, background=prColor, font=('Rubik', 12),
                               foreground="white", borderwidth=2, state="readonly", date_pattern='dd/mm/yyyy')
        self.date_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")


        self.modify_button = Button(self.form_options, width=16, text="Ajouter Emprunt", bg=bgColor, fg=prColor,
                                    relief="solid",
                                    font=('Rubik', 12), cursor="hand2", activebackground=prColor,
                                    activeforeground=bgColor,
                                    pady=5, command=self.prendre_livre)
        self.modify_button.grid(row=8, column=1, columnspan=2, padx=10, pady=10)
        self.fill_combobox()

    def prendre_livre(self):
        if not self.livre_combobox.get() or not self.adherent_combobox.get():
            messagebox.showinfo("Erreur", "Vous devez sélectionner toutes les entrées.")
            return
        date_emprunt = datetime.strptime(self.date_entry.get(), '%d/%m/%Y')
        date_emprunt_mysql = date_emprunt.strftime('%Y-%m-%d')
        aujourdhui = datetime.today().date()
        if aujourdhui > date_emprunt.date():
            messagebox.showinfo("Validation de la date", "La date doit être supérieure ou égale à la date d'aujourd'hui.")
            return
        livre_id = self.livre_combobox.get().split('-')[0].strip()
        adherent_id = self.adherent_combobox.get().split('-')[0].strip()

        connection = connect()
        cursor = connection.cursor()

        cursor.execute("INSERT INTO Emprunt (idAdh, idLiv, dateemprunt, status) VALUES (?, ?, ?, ?)",
                       (adherent_id, livre_id, date_emprunt_mysql, "sortie"))
        cursor.execute("UPDATE livre SET disponible = 'non' WHERE idLiv = ?", (livre_id,))
        connection.commit()
        cursor.close()
        connection.close()
        messagebox.showinfo("Success", "L'emprunt a été ajouté avec succès.")
        clearPage(self.root)
        AfficherEmprunts(self.root)

    def fill_combobox(self):
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT idLiv, titre FROM Livre where disponible = 'oui'")
        livres = cursor.fetchall()
        self.livre_combobox["values"] = [f"{livre[0]} - {livre[1]}" for livre in livres]

        cursor.execute("SELECT idAdh, nom FROM Adherent")
        adherents = cursor.fetchall()
        self.adherent_combobox["values"] = [f"{adherent[0]} - {adherent[1]}" for adherent in adherents]



class RetourneEmprunt():
    def __init__(self, root):
        self.root = root
        self.root.config(bg=bgColor)
        self.root.title("Bibliothèque - Ajouter Emprunt - Retourner un Livre")

        # ajouter style au combobox
        # add style to combobox
        self.root.option_add('*TCombobox*Listbox.selectBackground', prColor)
        self.root.option_add("*TCombobox*Listbox*Font", ("Rubik", 12))

        # content frame
        self.contentframe = Frame(self.root, bg=bgColor)
        self.contentframe.pack(expand=True, fill="both")

        # image
        self.ajouteimage = PhotoImage(file="ajouter_emprunt.png")
        self.labelImage = Label(self.contentframe, image=self.ajouteimage, border=0)
        self.labelImage.image = self.ajouteimage
        self.labelImage.place(x=0, y=0)

        self.frame = Frame(self.contentframe, width=400, height=350, bg=bgColor)
        self.frame.place(x=460, y=90)

        self.form_options = Frame(self.frame, bg=bgColor, height=300, width=300)
        self.form_options.pack(padx=10, pady=10)

        # title
        self.title = Label(self.form_options, text="Retourner un livre", fg=prColor, font=('Rubik', 23), bg=bgColor)
        self.title.grid(row=0, column=1, columnspan=2, rowspan=2, padx=10, pady=10, sticky="s")

        # adherent combobox
        self.adherent_label = Label(self.form_options, text="Adherent:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        self.adherent_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.adherent_combobox = ttk.Combobox(self.form_options, font=('Rubik', 12), state="readonly", width=30)
        self.adherent_combobox.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.adherent_combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)


        # livre combobox

        self.livre_label = Label(self.form_options, text="Livre:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        self.livre_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.livre_combobox = ttk.Combobox(self.form_options, font=('Rubik', 12), state="readonly", width=30)
        self.livre_combobox.grid(row=3, column=1, padx=10, pady=10, sticky="w")


        # date Entry
        self.adherent_label = Label(self.form_options, text="Date:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        self.adherent_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.date_entry = Entry(self.form_options, font=('Rubik', 12), fg=prColor, bg="lightblue", border=1, width=32,
                                 highlightcolor="black", relief="solid")
        self.date_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        self.date_entry.insert(0,datetime.today().date().strftime('%d/%m/%Y'))
        self.date_entry.config(state='readonly')


        self.modify_button = Button(self.form_options, width=16, text="Ajouter Emprunt", bg=bgColor, fg=prColor,
                                    relief="solid",
                                    font=('Rubik', 12), cursor="hand2", activebackground=prColor,
                                    activeforeground=bgColor,
                                    pady=5, command=self.retourne_livre)
        self.modify_button.grid(row=8, column=1, columnspan=2, padx=10, pady=10)
        self.fill_combobox()

    def retourne_livre(self):
        if not self.livre_combobox.get() or not self.adherent_combobox.get():
            messagebox.showinfo("Erreur", "Vous devez sélectionner toutes les entrées.")
            return
        date_emprunt = datetime.strptime(self.date_entry.get(), '%d/%m/%Y')
        date_emprunt_mysql = date_emprunt.strftime('%Y-%m-%d')
        aujourdhui = datetime.today().date()
        if aujourdhui > date_emprunt.date():
            messagebox.showinfo("Validation de la date", "La date doit être supérieure ou égale à la date d'aujourd'hui.")
            return
        livre_id = self.livre_combobox.get().split('-')[0].strip()
        adherent_id = self.adherent_combobox.get().split('-')[0].strip()

        connection = connect()
        cursor = connection.cursor()

        cursor.execute("INSERT INTO Emprunt (idAdh, idLiv, dateemprunt, status) VALUES (?, ?, ?, ?)",
                       (adherent_id, livre_id, date_emprunt_mysql, "entree"))
        cursor.execute("UPDATE livre SET disponible = 'oui' WHERE idLiv = ?", (livre_id,))
        connection.commit()
        cursor.close()
        connection.close()
        messagebox.showinfo("Success", "L'emprunt a été ajouté avec succès.")
        clearPage(self.root)
        AfficherEmprunts(self.root)

    def fill_combobox(self):
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT Adherent.idAdh, Adherent.nom FROM Adherent "
                       "JOIN Emprunt ON Emprunt.idAdh = Adherent.idAdh "
                       "JOIN Livre ON Livre.idLiv = Emprunt.idLiv "
                       "WHERE Emprunt.status = 'sortie' AND Livre.disponible = 'non'")
        adherents = cursor.fetchall()
        self.adherent_combobox["values"] = [f"{adherent[0]} - {adherent[1]}" for adherent in adherents]






    def on_combobox_select(self, event):
        adherent_id = self.adherent_combobox.get().split('-')[0].strip()
        connection = connect()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT Livre.idLiv, Livre.titre, Livre.pages, Livre.nomauteur, Livre.prix, Livre.disponible FROM "
            "Adherent JOIN Emprunt ON Adherent.idAdh = Emprunt.idAdh JOIN Livre ON Emprunt.IdLiv = Livre.idLiv WHERE "
            "Adherent.idAdh = ? AND Emprunt.status = 'sortie' and Livre.disponible = 'non'",
            (adherent_id,))
        livres = cursor.fetchall()
        self.livre_combobox["values"] = [f"{livre[0]} - {livre[1]}" for livre in livres]
        connection.commit()
        cursor.close()
        connection.close()

