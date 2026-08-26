import tkinter.messagebox
from tkinter import *
from tkinter import ttk, messagebox
from db import connect
from paths import asset_path
import re
import sqlite3

bgColor = "#00c9a7"
prColor = "#12192c"
prLightColor = "#c4fff3"
textHolderColor = "#7a7e89"

# validation fonction
def valider_donnees(titre, pages, prix, auteur):
    # Vérifier que le titre contient au moins 2 caractères alphanumériques
    if len(titre) < 2:
        if len(titre) == 0:
            messagebox.showerror("Erreur", "Le titre est obligatoire.")
        else:
            messagebox.showerror("Erreur", "Le titre doit contenir au moins 2 caractères.")
        return False

    # Vérifier que l'auteur contient au moins 2 caractères alphabétiques
    if not re.match(r'^[a-zA-Z\s]{2,}$', auteur):
        if len(auteur) == 0:
            messagebox.showerror("Erreur", "Le nom de l'auteur est obligatoire.")
        else:
            messagebox.showerror("Erreur", "Le nom de l'auteur doit contenir au moins 2 caractères alphabétiques.")
        return False

    # Vérifier que les pages sont un entier positif
    try:
        pages_int = int(pages)
        if pages_int <= 0:
            raise ValueError
    except ValueError:
        if len(pages) == 0:
            messagebox.showerror("Erreur", "Le nombre de pages est obligatoire.")
        else:
            messagebox.showerror("Erreur", "Le nombre de pages doit être un entier positif.")
        return False

    # Vérifier que le prix est un flottant positif
    try:
        prix_float = float(prix)
        if prix_float <= 0:
            raise ValueError
    except ValueError:
        if len(prix) == 0:
            messagebox.showerror("Erreur", "Le prix est obligatoire.")
        else:
            messagebox.showerror("Erreur", "Le prix doit être un nombre flottant positif.")
        return False



    return True

# fonction pour supprimer le contenu de la page
def clearPage(root):
    for widget in root.winfo_children():
        if isinstance(widget, Frame):
            widget.destroy()


class AfficherLivres():
    def __init__(self, root):
        self.root = root
        self.root.config(bg=bgColor)
        self.root.title("Bibliothèque - Afficher Livres")

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
        cursor.execute("Select * from livre")
        data = cursor.fetchall()
        columns = ('ID', 'Titre', 'Auteur', 'Pages', 'Prix', 'Disponible')
        self.tree = ttk.Treeview(self.contentframe, columns=columns, show="headings", style="Custom.Treeview")
        self.tree.tag_configure("oddrow", background="lightblue")

        # Create a scrollbar
        self.tree_scroll = ttk.Scrollbar(self.tree)
        self.tree_scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.config(command=self.tree.yview)


        self.tree.heading('ID', text='ID')
        self.tree.column('ID', width=20)

        self.tree.heading('Titre', text='Titre')
        self.tree.column('Titre', width=200)

        self.tree.heading('Auteur', text='Auteur')
        self.tree.column('Auteur', width=80)

        self.tree.heading('Pages', text='Pages')
        self.tree.column('Pages', width=80)

        self.tree.heading('Prix', text='Prix')
        self.tree.column('Prix', width=50)

        self.tree.heading('Disponible', text='Disponible')
        self.tree.column('Disponible', width=100)

        for col in columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.trierColumn(self.tree, _col, False))


        for i, item in enumerate(data):
            self.tree.insert("", "end", values=item, tags=("oddrow" if i % 2 == 1 else ""))

        self.tree.pack(fill="both", expand=True)
        cursor.close()
        connection.close()
        self.rechercheLivre(self.tree)

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

    def rechercheLivre(self, tree):
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
            cursor.execute("SELECT * FROM livre WHERE (COALESCE(idLiv,'') || ' ' || COALESCE(titre,'') || ' ' || "
                           "COALESCE(nomauteur,'') || ' ' || COALESCE(pages,'') || ' ' || COALESCE(prix,'') || ' ' || "
                           "COALESCE(disponible,'')) LIKE ?",
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


class AjouterLivre():
    def __init__(self, root):
        self.root = root
        self.root.config(bg=bgColor)
        self.root.title("Bibliothèque - Ajouter Livre")

        # content frame
        self.contentframe = Frame(self.root, bg=bgColor)
        self.contentframe.pack(expand=True, fill="both")

        #image
        self.ajouteimage= PhotoImage(file=asset_path("ajouter_livre.png"))
        self.labelImage = Label(self.contentframe, image=self.ajouteimage, border=0)
        self.labelImage.image = self.ajouteimage
        self.labelImage.place(x=0, y=0)

        self.frame = Frame(self.contentframe, width=350, height=350, bg=bgColor)
        self.frame.place(x=520, y=90)

        self.form_options = Frame(self.frame, bg=bgColor, height=300, width=300)
        self.form_options.pack( padx=10, pady=10)

        # title
        self.title = Label(self.form_options, text="Ajouter livre", fg=prColor, font=('Rubik', 23), bg=bgColor)
        self.title.grid(row=0, column=0, columnspan=3, rowspan=2,padx=10, pady=10, sticky="e")


        # titre entry
        title_label = Label(self.form_options, text="Titre:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        title_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.titre_entry = Entry(self.form_options, font=('Rubik', 12), fg=prColor, bg="lightblue", border=1,
                                 highlightcolor="black", relief="solid")
        self.titre_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # auteur entry
        auteur_label = Label(self.form_options, text="Auteur:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        auteur_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.auteur_entry = Entry(self.form_options, font=('Rubik', 12), fg=prColor, bg="lightblue", border=1,
                                  highlightcolor="black", relief="solid")
        self.auteur_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # pages entry
        pages_label = Label(self.form_options, text="Pages:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        pages_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.pages_entry = Entry(self.form_options, font=('Rubik', 12), fg=prColor, bg="lightblue", border=1,
                                 highlightcolor="black", relief="solid")
        self.pages_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # prix entry
        prix_label = Label(self.form_options, text="Prix:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        prix_label.grid(row=6, column=0, padx=10, pady=10, sticky="e")
        self.prix_entry = Entry(self.form_options, font=('Rubik', 12), fg=prColor, bg="lightblue", border=1,
                                highlightcolor="black", relief="solid")
        self.prix_entry.grid(row=6, column=1, padx=10, pady=10, sticky="w")

        # disponible checkbox
        #self.disponible_var = StringVar(value="oui")
        #self.disponible_check = Checkbutton(self.form_options, text="Disponible", variable=self.disponible_var,
        #                                   onvalue="oui",
        #                                   offvalue="non", bg=bgColor, fg=prColor, font=('Rubik', 11),
        #                                   activebackground=bgColor,
        #                                   cursor="hand2")
        #self.disponible_check.grid(row=7, column=1, padx=10, pady=10)

        self.modify_button = Button(self.form_options, width=16, text="Ajouter Livre", bg=bgColor, fg=prColor,
                                    relief="solid",
                                    font=('Rubik', 12), cursor="hand2", activebackground=prColor,
                                    activeforeground=bgColor,
                                    pady=5, command=self.ajouter_livre)
        self.modify_button.grid(row=8, column=1, columnspan=2, padx=10, pady=10)

    def ajouter_livre(self):
        titre = self.titre_entry.get().strip()
        pages = self.pages_entry.get().strip()
        prix = self.prix_entry.get().strip()
        auteur = self.auteur_entry.get().strip()
        #disponible = self.disponible_var.get()

        if valider_donnees(titre,pages,prix, auteur):
            connection = connect()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Livre (titre,  nomauteur, pages, prix, disponible) VALUES (?, ?, ?, ?, ?)",
                           (titre, auteur, pages, prix, "oui"))
            connection.commit()
            messagebox.showinfo("Success", "le livre a été ajouté avec succés")
            clearPage(self.root)
            AfficherLivres(self.root)


class ModifierLivre():
    def __init__(self, root):
        self.root = root
        self.root.config(bg=bgColor)
        self.root.title("Bibliothèque - Modifier Livre")

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
                             font=('Rubik', 12))

        self.style.map('Custom.Treeview',
                       background=[('selected', bgColor)],
                       foreground=[('selected', 'white')])



        # content frame
        self.contentframe = Frame(self.root, bg=bgColor, padx=50, pady=50)
        self.contentframe.pack(expand=True, fill="both")



        self.tree = ttk.Treeview(self.contentframe, columns = ('ID', 'Titre', 'Auteur', 'Pages', 'Prix', 'Disponible'),
                                 show="headings", style="Custom.Treeview")

        # Create a scrollbar
        self.tree_scroll = ttk.Scrollbar(self.tree)
        self.tree_scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.config(command=self.tree.yview)


        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda _col=col: self.trierColumn(self.tree, _col, False))

        self.tree.heading('ID', text='ID')
        self.tree.column('ID', width=20)

        self.tree.heading('Titre', text='Titre')
        self.tree.column('Titre', width=200)

        self.tree.heading('Auteur', text='Auteur')
        self.tree.column('Auteur', width=80)

        self.tree.heading('Pages', text='Pages')
        self.tree.column('Pages', width=80)

        self.tree.heading('Prix', text='Prix')
        self.tree.column('Prix', width=50)

        self.tree.heading('Disponible', text='Disponible')
        self.tree.column('Disponible', width=100)

        self.tree.bind("<<TreeviewSelect>>", self.selecterCol)
        self.tree.tag_configure("oddrow", background="lightblue")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.form_options = Frame(self.contentframe, bg=bgColor, height=300)
        self.form_options.pack(fill="x", padx=10, pady=10)

        # titre entry
        title_label = Label(self.form_options, text="Titre:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.titre_entry = Entry(self.form_options, font=('Rubik', 12), fg=prColor, bg="lightblue", border=1,
                                 highlightcolor="black", relief="solid")
        self.titre_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        #auteur entry
        auteur_label = Label(self.form_options, text="Auteur:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        auteur_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.auteur_entry = Entry(self.form_options, font=('Rubik', 12), fg=prColor, bg="lightblue", border=1,
                                 highlightcolor="black", relief="solid")
        self.auteur_entry.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        #pages entry
        pages_label = Label(self.form_options, text="Pages:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        pages_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.pages_entry = Entry(self.form_options, font=('Rubik', 12), fg=prColor,  bg="lightblue", border=1,
                                 highlightcolor="black", relief="solid")
        self.pages_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # prix entry
        prix_label = Label(self.form_options, text="Prix:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        prix_label.grid(row=1, column=2, padx=10, pady=10, sticky="e")
        self.prix_entry = Entry(self.form_options, font=('Rubik', 12), fg=prColor, bg="lightblue", border=1,
                                 highlightcolor="black", relief="solid")
        self.prix_entry.grid(row=1, column=3, padx=10, pady=10, sticky="w")



        self.modify_button = Button(self.form_options, width=16, text="Modifier Livre", bg=bgColor, fg=prColor, relief="solid",
                               font=('Rubik', 12), cursor="hand2", activebackground=prColor, activeforeground=bgColor,
                               pady=5, command=self.modifier_livre)
        self.modify_button.grid(row=0, column=4, columnspan=2, padx=10, pady=10)

        self.supprimer_button = Button(self.form_options, width=16, text="Supprimer Livre", bg="#e74c3c", fg=prColor, relief="solid",
                               font=('Rubik', 12), cursor="hand2", activebackground=prColor, activeforeground=bgColor,
                               pady=5, command=self.supprimer_livre)
        self.supprimer_button.grid(row=1, column=4, columnspan=2, padx=10, pady=10)

        self.afficherInfo()

    def afficherInfo(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Livre")
        data = cursor.fetchall()
        for i in range(len(data)):
            item = data[i]
            self.tree.insert("", "end", values=item, tags=("oddrow" if i % 2 == 1 else ""))

    def modifier_livre(self):
        if not self.tree.selection() :
            tkinter.messagebox.showwarning("invalid choix","veuillez selectionner une livre!")
            return
        titre = self.titre_entry.get().strip()
        pages = self.pages_entry.get().strip()
        prix = self.prix_entry.get().strip()
        auteur = self.auteur_entry.get().strip()
        if valider_donnees(titre, pages, prix, auteur):
            connection = connect()
            cursor = connection.cursor()
            cursor.execute("UPDATE Livre SET titre=?, pages=?, nomauteur=?, prix=? WHERE idLiv=?",
                           (titre, pages, auteur, prix, self.selected_book_id))
            connection.commit()
            messagebox.showinfo("Success", "le livre a été modifier avec succés")
            self.afficherInfo()
            self.titre_entry.delete(0, END)
            self.auteur_entry.delete(0, END)
            self.pages_entry.delete(0, END)
            self.prix_entry.delete(0, END)

    def supprimer_livre(self):
        if not self.tree.selection() :
            tkinter.messagebox.showwarning("invalid choix","veuillez selectionner une livre!")
            return
        selected_item = self.tree.selection()
        if selected_item:
            response = messagebox.askyesno("Confirm", "Êtes vous sure de supprimer cette livre?")
            if response:
                connection = connect()
                cursor = connection.cursor()
                try:
                    cursor.execute("DELETE FROM Livre WHERE idLiv=?", (self.selected_book_id,))
                    connection.commit()
                    messagebox.showinfo("Success", "Le livre a été supprimé avec succé")
                    self.afficherInfo()
                    self.titre_entry.delete(0, END)
                    self.auteur_entry.delete(0, END)
                    self.pages_entry.delete(0, END)
                    self.prix_entry.delete(0, END)
                except sqlite3.IntegrityError:
                    messagebox.showerror("Erreur",
                                         "vous ne pouvez pas supprimer cet livre, cet livre a déja un emprunt")
                except sqlite3.Error as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la suppression du livre : {e}")
                finally:
                    cursor.close()
                    connection.close()

    def selecterCol(self, event):
        if not self.tree.selection():
            self.titre_entry.delete(0, END)
            self.auteur_entry.delete(0, END)
            self.pages_entry.delete(0, END)
            self.prix_entry.delete(0, END)
            return
        selected_item = self.tree.selection()[0]
        selected_values = self.tree.item(selected_item, "values")

        self.selected_book_id = selected_values[0]
        self.titre_entry.delete(0, END)
        self.titre_entry.insert(0, selected_values[1])
        self.auteur_entry.delete(0, END)
        self.auteur_entry.insert(0, selected_values[2])
        self.pages_entry.delete(0, END)
        self.pages_entry.insert(0, selected_values[3])
        self.prix_entry.delete(0, END)
        self.prix_entry.insert(0, selected_values[4])


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



