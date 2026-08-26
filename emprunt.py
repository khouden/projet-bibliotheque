import tkinter.messagebox
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from db import connect
from paths import asset_path
import re

bgColor = "#00c9a7"
prColor = "#12192c"
prLightColor = "#c4fff3"
textHolderColor = "#7a7e89"

LOAN_DAYS = 14


# validation function
def valider_donnees(nom, tel, email):
    # Name must contain at least 2 alphabetic characters
    if not re.match(r'^[a-zA-Z\s]{2,}$', nom):
        if len(nom) == 0:
            messagebox.showerror("Error", "Name is required.")
        else:
            messagebox.showerror("Error", "Name must contain at least 2 alphabetic characters.")
        return False

    # Phone is optional; international format when provided
    if tel:
        if not re.match(r'^\+?[\d\s\-\(\)\.]+$', tel.strip()):
            messagebox.showerror("Error", "Phone number contains invalid characters.")
            return False
        chiffres = re.sub(r'\D', '', tel)
        if not 7 <= len(chiffres) <= 15:
            messagebox.showerror("Error", "Phone number must contain between 7 and 15 digits.")
            return False

    # Email must be a valid address
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        if len(email) == 0:
            messagebox.showerror("Error", "Email is required.")
        else:
            messagebox.showerror("Error", "Email must be valid.")
        return False

    return True


# clear the current page content
def clearPage(root):
    for widget in root.winfo_children():
        if isinstance(widget, Frame):
            widget.destroy()


STATUS_LABELS = {"sortie": "Borrowed", "entree": "Returned"}

OVERDUE_BG = "#ffb3b3"


def format_emprunt_row(item, today):
    """Return (display_values, tags); tags is ('overdue',) or None for zebra rows."""
    values = list(item)
    status = values[-1]
    values[-1] = STATUS_LABELS.get(status, status)
    for idx in (3, 4):
        raw = values[idx]
        if raw:
            try:
                values[idx] = datetime.strptime(raw, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                pass
    due = values[4]
    if status == "sortie" and due:
        try:
            if today > datetime.strptime(due, "%d/%m/%Y").date():
                return values, ("overdue",)
        except ValueError:
            pass
    return values, None


class AfficherEmprunts():
    def __init__(self, root):
        self.root = root
        self.root.config(bg=bgColor)
        self.root.title("Library - Loans")

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
        cursor.execute("select e.idEmp, a.nom, l.titre, e.dateemprunt, e.dateretourprevue, e.status from emprunt e "
                       "join adherent a on e.idAdh = a.idAdh join livre l on e.idLiv = l.idLiv order by e.idEmp")
        data = cursor.fetchall()
        columns = ('ID', 'Member', 'Book Title', 'Loan Date', 'Due Date', 'Status')
        self.tree = ttk.Treeview(self.contentframe, columns=columns, show="headings", style="Custom.Treeview")
        self.tree.tag_configure("oddrow", background="lightblue")
        self.tree.tag_configure("overdue", background=OVERDUE_BG)

        # Create a scrollbar
        self.tree_scroll = ttk.Scrollbar(self.tree)
        self.tree_scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.config(command=self.tree.yview)

        for col in columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.trierColumn(self.tree, _col, False))
            self.tree.column(col, width=100, stretch=True)

        today = datetime.today().date()
        for i, item in enumerate(data):
            values, tags = format_emprunt_row(item, today)
            if tags is None:
                tags = ("oddrow",) if i % 2 == 1 else ()
            self.tree.insert("", "end", values=values, tags=tags)

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
                "SELECT e.idEmp, a.nom, l.titre, e.dateemprunt, e.dateretourprevue, e.status FROM emprunt e "
                "JOIN adherent a ON e.idAdh = a.idAdh JOIN livre l ON e.idLiv = l.idLiv "
                "WHERE (COALESCE(e.idEmp,'') || ' ' || COALESCE(a.nom,'') || ' ' || COALESCE(l.titre,'') || ' ' || "
                "COALESCE(e.dateemprunt,'') || ' ' || COALESCE(e.dateretourprevue,'') || ' ' || "
                "COALESCE(e.status,'')) LIKE ?",
                ('%' + query + '%',))
            data = cursor.fetchall()

            tree.delete(*tree.get_children())
            today = datetime.today().date()
            for i in range(len(data)):
                values, tags = format_emprunt_row(data[i], today)
                if tags is None:
                    tags = ("oddrow",) if i % 2 == 1 else ()
                self.tree.insert("", "end", values=values, tags=tags)

        search_button = Button(search_frame, text="Search", command=search_tree, font=('Rubik', 12), bg=prColor,
                               relief="solid", cursor="hand2", fg="white", activebackground=bgColor,
                               activeforeground="black")
        search_button.pack(side="right")


class PrendreEmprunt():
    def __init__(self, root):
        self.root = root
        self.root.config(bg=bgColor)
        self.root.title("Library - Borrow a Book")

        # ajouter style au combobox
        self.root.option_add('*TCombobox*Listbox.selectBackground', prColor)
        self.root.option_add("*TCombobox*Listbox*Font", ("Rubik", 12))

        # content frame
        self.contentframe = Frame(self.root, bg=bgColor)
        self.contentframe.pack(expand=True, fill="both")

        # image
        self.ajouteimage = PhotoImage(file=asset_path("ajouter_emprunt.png"))
        self.labelImage = Label(self.contentframe, image=self.ajouteimage, border=0)
        self.labelImage.image = self.ajouteimage
        self.labelImage.place(x=0, y=0)

        self.frame = Frame(self.contentframe, width=400, height=350, bg=bgColor)
        self.frame.place(x=460, y=90)

        self.form_options = Frame(self.frame, bg=bgColor, height=300, width=300)
        self.form_options.pack(padx=10, pady=10)

        # title
        self.title = Label(self.form_options, text="Borrow a book", fg=prColor, font=('Rubik', 23), bg=bgColor)
        self.title.grid(row=0, column=1, columnspan=2, rowspan=2, padx=10, pady=10, sticky="s")

        # member combobox
        self.adherent_label = Label(self.form_options, text="Member:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        self.adherent_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.adherent_combobox = ttk.Combobox(self.form_options, font=('Rubik', 12), width=30, state="readonly")
        self.adherent_combobox.grid(row=2, column=1, padx=10, pady=10, sticky="w")


        # livre combobox
        self.livre_label = Label(self.form_options, text="Book:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        self.livre_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.livre_combobox = ttk.Combobox(self.form_options, font=('Rubik', 12), state="readonly", width=30)
        self.livre_combobox.grid(row=3, column=1, padx=10, pady=10, sticky="w")



        # date Entry
        self.adherent_label = Label(self.form_options, text="Date:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        self.adherent_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.date_entry = DateEntry(self.form_options, width=30, background=prColor, font=('Rubik', 12),
                               foreground="white", borderwidth=2, state="readonly", date_pattern='dd/mm/yyyy')
        self.date_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # due date Entry
        self.due_label = Label(self.form_options, text="Due date:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        self.due_label.grid(row=5, column=0, padx=10, pady=10, sticky="e")
        self.due_entry = DateEntry(self.form_options, width=30, background="#b23a48", font=('Rubik', 12),
                               foreground="white", borderwidth=2, state="readonly", date_pattern='dd/mm/yyyy')
        self.due_entry.grid(row=5, column=1, padx=10, pady=10, sticky="w")
        self.due_entry.set_date(datetime.today() + timedelta(days=LOAN_DAYS))


        self.modify_button = Button(self.form_options, width=16, text="Borrow", bg=bgColor, fg=prColor,
                                    relief="solid",
                                    font=('Rubik', 12), cursor="hand2", activebackground=prColor,
                                    activeforeground=bgColor,
                                    pady=5, command=self.prendre_livre)
        self.modify_button.grid(row=8, column=1, columnspan=2, padx=10, pady=10)
        self.fill_combobox()

    def prendre_livre(self):
        if not self.livre_combobox.get() or not self.adherent_combobox.get():
            messagebox.showinfo("Error", "Please select all fields.")
            return
        date_emprunt = self.date_entry.get_date()
        date_retour_prevue = self.due_entry.get_date()
        aujourdhui = datetime.today().date()
        if date_emprunt > aujourdhui:
            messagebox.showinfo("Date validation", "The loan date cannot be in the future.")
            return
        if date_retour_prevue < date_emprunt:
            messagebox.showinfo("Date validation", "The due date must be on or after the loan date.")
            return
        livre_id = self.livre_combobox.get().split('-')[0].strip()
        adherent_id = self.adherent_combobox.get().split('-')[0].strip()

        connection = connect()
        cursor = connection.cursor()

        cursor.execute("INSERT INTO Emprunt (idAdh, idLiv, dateemprunt, dateretourprevue, status) VALUES (?, ?, ?, ?, ?)",
                       (adherent_id, livre_id, date_emprunt.strftime('%Y-%m-%d'),
                        date_retour_prevue.strftime('%Y-%m-%d'), "sortie"))
        cursor.execute("UPDATE livre SET disponible = 'non' WHERE idLiv = ?", (livre_id,))
        connection.commit()
        cursor.close()
        connection.close()
        messagebox.showinfo("Success", "Loan recorded successfully.")
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
        self.root.title("Library - Return a Book")

        # ajouter style au combobox
        # add style to combobox
        self.root.option_add('*TCombobox*Listbox.selectBackground', prColor)
        self.root.option_add("*TCombobox*Listbox*Font", ("Rubik", 12))

        # content frame
        self.contentframe = Frame(self.root, bg=bgColor)
        self.contentframe.pack(expand=True, fill="both")

        # image
        self.ajouteimage = PhotoImage(file=asset_path("ajouter_emprunt.png"))
        self.labelImage = Label(self.contentframe, image=self.ajouteimage, border=0)
        self.labelImage.image = self.ajouteimage
        self.labelImage.place(x=0, y=0)

        self.frame = Frame(self.contentframe, width=400, height=350, bg=bgColor)
        self.frame.place(x=460, y=90)

        self.form_options = Frame(self.frame, bg=bgColor, height=300, width=300)
        self.form_options.pack(padx=10, pady=10)

        # title
        self.title = Label(self.form_options, text="Return a book", fg=prColor, font=('Rubik', 23), bg=bgColor)
        self.title.grid(row=0, column=1, columnspan=2, rowspan=2, padx=10, pady=10, sticky="s")

        # member combobox
        self.adherent_label = Label(self.form_options, text="Member:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        self.adherent_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.adherent_combobox = ttk.Combobox(self.form_options, font=('Rubik', 12), state="readonly", width=30)
        self.adherent_combobox.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.adherent_combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)


        # livre combobox

        self.livre_label = Label(self.form_options, text="Book:", bg=bgColor, fg=prColor, font=('Rubik', 12))
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


        self.modify_button = Button(self.form_options, width=16, text="Return", bg=bgColor, fg=prColor,
                                    relief="solid",
                                    font=('Rubik', 12), cursor="hand2", activebackground=prColor,
                                    activeforeground=bgColor,
                                    pady=5, command=self.retourne_livre)
        self.modify_button.grid(row=8, column=1, columnspan=2, padx=10, pady=10)
        self.fill_combobox()

    def retourne_livre(self):
        if not self.livre_combobox.get() or not self.adherent_combobox.get():
            messagebox.showinfo("Error", "Please select all fields.")
            return
        livre_id = self.livre_combobox.get().split('-')[0].strip()
        adherent_id = self.adherent_combobox.get().split('-')[0].strip()

        connection = connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE Emprunt SET status='entree' WHERE idAdh=? AND idLiv=? AND status='sortie'",
                       (adherent_id, livre_id))
        if cursor.rowcount == 0:
            cursor.close()
            connection.close()
            messagebox.showerror("Error", "No active loan found for this member and book.")
            return
        cursor.execute("UPDATE livre SET disponible='oui' WHERE idLiv=?", (livre_id,))
        connection.commit()
        cursor.close()
        connection.close()
        messagebox.showinfo("Success", "Book returned successfully.")
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


class ModifierEmprunt():
    def __init__(self, root):
        self.root = root
        self.root.config(bg=bgColor)
        self.root.title("Library - Edit Loan")

        self.style = ttk.Style()
        self.style.configure("Custom.Treeview",
                             background="white", foreground="black", rowheight=25,
                             fieldbackground="white", font=('Rubik', 10))
        self.style.configure("Custom.Treeview.Heading",
                             background=prColor, foreground="white", font=('Rubik', 12))
        self.style.map('Custom.Treeview',
                       background=[('selected', bgColor)], foreground=[('selected', 'white')])

        self.contentframe = Frame(self.root, bg=bgColor, padx=50, pady=50)
        self.contentframe.pack(expand=True, fill="both")

        columns = ('ID', 'Member', 'Book Title', 'Loan Date', 'Due Date', 'Status')
        self.tree = ttk.Treeview(self.contentframe, columns=columns, show="headings",
                                 style="Custom.Treeview")
        self.tree_scroll = ttk.Scrollbar(self.tree)
        self.tree_scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.config(command=self.tree.yview)

        for col in columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.trierColumn(self.tree, _col, False))
            self.tree.column(col, width=100, stretch=True)

        self.tree.column('ID', width=40)
        self.tree.column('Member', width=140)
        self.tree.column('Book Title', width=160)
        self.tree.column('Loan Date', width=110)
        self.tree.column('Due Date', width=110)

        self.tree.bind("<<TreeviewSelect>>", self.selecterCol)
        self.tree.tag_configure("oddrow", background="lightblue")
        self.tree.tag_configure("overdue", background=OVERDUE_BG)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.form_options = Frame(self.contentframe, bg=bgColor, height=300)
        self.form_options.pack(fill="x", padx=10, pady=10)

        self.member_combobox = ttk.Combobox(self.form_options, font=('Rubik', 11), width=20)
        self.member_combobox.grid(row=0, column=0, padx=10, pady=10)
        member_label = Label(self.form_options, text="Member:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        member_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.member_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.book_combobox = ttk.Combobox(self.form_options, font=('Rubik', 11), width=20)
        self.book_combobox.grid(row=0, column=2, padx=10, pady=10)
        book_label = Label(self.form_options, text="Book:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        book_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.book_combobox.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        loan_date_label = Label(self.form_options, text="Loan date:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        loan_date_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.loan_date_entry = DateEntry(self.form_options, width=18, background=prColor, font=('Rubik', 11),
                                         foreground="white", borderwidth=2, state="readonly",
                                         date_pattern='dd/mm/yyyy')
        self.loan_date_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        due_date_label = Label(self.form_options, text="Due date:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        due_date_label.grid(row=1, column=2, padx=10, pady=10, sticky="e")
        self.due_date_entry = DateEntry(self.form_options, width=18, background="#b23a48", font=('Rubik', 11),
                                        foreground="white", borderwidth=2, date_pattern='dd/mm/yyyy')
        self.due_date_entry.grid(row=1, column=3, padx=10, pady=10, sticky="w")

        status_label = Label(self.form_options, text="Status:", bg=bgColor, fg=prColor, font=('Rubik', 12))
        status_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.status_combobox = ttk.Combobox(self.form_options, font=('Rubik', 11), width=18,
                                            values=["Borrowed", "Returned"], state="readonly")
        self.status_combobox.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.modify_button = Button(self.form_options, width=16, text="Edit Loan", bg=bgColor, fg=prColor,
                                    relief="solid", font=('Rubik', 12), cursor="hand2",
                                    activebackground=prColor, activeforeground=bgColor,
                                    pady=5, command=self.modifier_emprunt)
        self.modify_button.grid(row=0, column=4, columnspan=2, padx=10, pady=10)

        self.supprimer_button = Button(self.form_options, width=16, text="Delete Loan", bg="#e74c3c", fg=prColor,
                                       relief="solid", font=('Rubik', 12), cursor="hand2",
                                       activebackground=prColor, activeforeground=bgColor,
                                       pady=5, command=self.supprimer_emprunt)
        self.supprimer_button.grid(row=1, column=4, columnspan=2, padx=10, pady=10)

        self.afficherInfo()
        self.fill_comboboxes()

    def selecterCol(self, event):
        if not self.tree.selection():
            return
        selected_item = self.tree.selection()[0]
        selected_values = self.tree.item(selected_item, "values")

        self.selected_emprunt_id = selected_values[0]

        self.member_combobox.set(selected_values[1])
        self.book_combobox.set(selected_values[2])
        self.loan_date_entry.set_date(datetime.strptime(selected_values[3], '%d/%m/%Y').date())
        self.due_date_entry.set_date(datetime.strptime(selected_values[4], '%d/%m/%Y').date())
        self.status_combobox.set(selected_values[5])

        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT idAdh FROM emprunt WHERE idEmp=?", (self.selected_emprunt_id,))
        row = cursor.fetchone()
        self.original_book_id = None
        self.original_status = None
        if row:
            cursor.execute(
                "SELECT e.idLiv, e.status FROM emprunt e WHERE e.idEmp=?",
                (self.selected_emprunt_id,))
            row2 = cursor.fetchone()
            if row2:
                self.original_book_id = row2[0]
                self.original_status = row2[1]
        cursor.close()
        connection.close()

    def afficherInfo(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("select e.idEmp, a.nom, l.titre, e.dateemprunt, e.dateretourprevue, e.status from emprunt e "
                       "join adherent a on e.idAdh = a.idAdh join livre l on e.idLiv = l.idLiv order by e.idEmp")
        data = cursor.fetchall()
        today = datetime.today().date()
        for i, item in enumerate(data):
            values, tags = format_emprunt_row(item, today)
            if tags is None:
                tags = ("oddrow",) if i % 2 == 1 else ()
            self.tree.insert("", "end", values=values, tags=tags)
        cursor.close()
        connection.close()

    def fill_comboboxes(self):
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT idAdh, nom FROM adherent ORDER BY idAdh")
        self.member_combobox["values"] = [f"{r[0]} - {r[1]}" for r in cursor.fetchall()]
        cursor.execute("SELECT idLiv, titre FROM livre ORDER BY idLiv")
        self.book_combobox["values"] = [f"{r[0]} - {r[1]}" for r in cursor.fetchall()]
        cursor.close()
        connection.close()

    def modifier_emprunt(self):
        if not self.tree.selection():
            messagebox.showwarning("Invalid choice", "Please select a loan!")
            return
        member_text = self.member_combobox.get().strip()
        book_text = self.book_combobox.get().strip()
        status_text = self.status_combobox.get()
        if not member_text or not book_text:
            messagebox.showerror("Error", "Please select a member and a book.")
            return
        try:
            member_id = member_text.split('-')[0].strip()
            book_id = book_text.split('-')[0].strip()
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Invalid member or book selection.")
            return
        loan_date = self.loan_date_entry.get_date()
        due_date = self.due_date_entry.get_date()
        if due_date < loan_date:
            messagebox.showerror("Error", "Due date must be on or after loan date.")
            return
        status_map = {"Borrowed": "sortie", "Returned": "entree"}
        new_status = status_map.get(status_text)
        if not new_status:
            messagebox.showerror("Error", "Please select a valid status.")
            return

        connection = connect()
        cursor = connection.cursor()
        try:
            old_book_id = getattr(self, 'original_book_id', None)
            old_status = getattr(self, 'original_status', None)

            if old_book_id is not None and str(book_id) != str(old_book_id):
                cursor.execute("UPDATE livre SET disponible='oui' WHERE idLiv=?", (old_book_id,))

            if new_status == 'sortie':
                cursor.execute("UPDATE livre SET disponible='non' WHERE idLiv=?", (book_id,))
            else:
                cursor.execute("UPDATE livre SET disponible='oui' WHERE idLiv=?", (book_id,))

            cursor.execute(
                "UPDATE emprunt SET idAdh=?, idLiv=?, dateemprunt=?, dateretourprevue=?, status=? WHERE idEmp=?",
                (member_id, book_id, loan_date.strftime('%Y-%m-%d'),
                 due_date.strftime('%Y-%m-%d'), new_status, self.selected_emprunt_id))
            connection.commit()
            messagebox.showinfo("Success", "Loan updated successfully.")
            self.afficherInfo()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Cannot update: the selected book or member does not exist.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error updating loan: {e}")
        finally:
            cursor.close()
            connection.close()

    def supprimer_emprunt(self):
        if not self.tree.selection():
            messagebox.showwarning("Invalid choice", "Please select a loan!")
            return
        response = messagebox.askyesno("Confirm", "Are you sure you want to delete this loan?")
        if not response:
            return
        connection = connect()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT idLiv, status FROM emprunt WHERE idEmp=?", (self.selected_emprunt_id,))
            row = cursor.fetchone()
            cursor.execute("DELETE FROM emprunt WHERE idEmp=?", (self.selected_emprunt_id,))
            if row and row[1] == 'sortie':
                cursor.execute("UPDATE livre SET disponible='oui' WHERE idLiv=?", (row[0],))
            connection.commit()
            messagebox.showinfo("Success", "Loan deleted successfully.")
            self.afficherInfo()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error deleting loan: {e}")
        finally:
            cursor.close()
            connection.close()

    def trierColumn(self, treeview, col, reverse):
        data = [(treeview.set(k, col), k) for k in treeview.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]) if t[0] else 0, reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0], reverse=reverse)
        for index, (val, k) in enumerate(data):
            treeview.move(k, '', index)
        treeview.heading(col, command=lambda: self.trierColumn(treeview, col, not reverse))

