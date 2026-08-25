# AGENTS.md

Context file for AI agents working on this repository. Read this before making any change.

## Project Overview

**projet-bibliotheque** ("library project") is a French-language **desktop Library Management System** built as a school/team project by Abdellah Khouden, Abderrahim Bensaid, and Othman Elhyane (supervised by Mr. Abdellah Sair).

It manages three entities:
- **Livre** (books): add, list/search/sort, modify, delete
- **Adherent** (members): add, list/search/sort, modify, delete
- **Emprunt** (loans): take a book (status `sortie`), return a book (status `entree`), list/search loans

Authentication is a single login screen backed by a `login` table in MySQL.

## Tech Stack

- **Python 3** (uses `match/case`, so requires **3.10+**)
- **GUI**: Tkinter / ttk (`PhotoImage` for PNGs, no Pillow)
- **Calendar widget**: `tkcalendar` (`DateEntry`)
- **Database**: MySQL via `mysql-connector-python`
- No virtual env, no `requirements.txt`, no linter/test config committed.
  Implicit dependencies to install: `mysql-connector-python`, `tkcalendar`.

## How to Run

```powershell
python main.py
```

Requirements:
- A local MySQL server must be running with database `bibliotheque`
- Connection assumed everywhere: `host=localhost, user=root, password=""` (empty password, XAMPP/WAMP-style default)
- Rubik font installed (UI falls back gracefully if missing)

## File Map

| File | Role |
|---|---|
| `main.py` | Entry point. Creates root window (925x600), starts `Login`. The direct `MainMenu(root)` call is commented out - login navigates to it on success. |
| `login.py` | Login screen class `Login`. Validates credentials against `login` table, then swaps content frame for `MainMenu`. |
| `mainMenu.py` | `MainMenu`: menubar (options/Livre/Adherent/Emprunt) + home screen with 3 comboboxes acting as quick navigation. Routes to page classes via `match/case`. |
| `livre.py` | Book pages: `AfficherLivres` (Treeview + search + column sort), `AjouterLivre`, `ModifierLivre` (also delete). Contains shared `valider_donnees()` and `clearPage()`. |
| `adherent.py` | Member pages: `AfficherAdherents`, `AjouterAdherent`, `ModifierAdherent` (also delete). Own copies of `valider_donnees()` / `clearPage()`. |
| `emprunt.py` | Loan pages: `AfficherEmprunts`, `PrendreEmprunt` (checkout), `RetourneEmprunt` (return). Uses `tkcalendar.DateEntry`. |
| `code in one file.py` | Legacy monolithic prototype (~441 lines). Reference only - do not import or edit. |
| `*.png` | UI assets loaded by relative path: `icon.png`, `login2.png`, `background.png`, `ajouter_livre.png`, `ajouter_adherent.png`, `ajouter_emprunt.png`. Must stay in repo root (app breaks if run from another cwd). |

## Database Schema (database: `bibliotheque`)

No schema file is committed. Tables inferred from queries in the code:

```sql
login    (username, password)                        -- plaintext credentials
livre    (idLiv PK, titre, nomauteur, pages, prix,
          disponible 'oui'|'non')                    -- 'oui' = available on shelf
adherent (idAdh PK, nom, tel, email)                 -- tel: Moroccan 06/07/05XXXXXXXX
emprunt  (idEmp PK AUTO_INC, idAdh FK->adherent,
          idLiv FK->livre, dateemprunt DATE,
          status 'sortie'|'entree')                  -- sortie=checked out, entree=returned
```

Loan lifecycle: `PrendreEmprunt` inserts an emprunt row with status `sortie` and sets `livre.disponible = 'non'`. `RetourneEmprunt` inserts a row with status `entree` and sets `disponible = 'oui'`. Deletes of books/members with existing loans are blocked by FK constraints (caught by bare excepts showing an error messagebox).

## Architecture & Conventions

- **Single-window SPA pattern**: one `Tk` root forever. Each page is a class taking `root` in `__init__` and packing a `Frame` into it. Navigation = destroy all child `Frame`s (`clearPage()` / `clear_widgets()`) then instantiate the next page class. There is no router.
- **DB access**: raw `mysql.connector.connect(...)` opened/closed inside every method. No connection pooling, no ORM, no DAO layer. Queries are parameterized (%s) except search, which interpolates a hardcoded column list into `CONCAT_WS`.
- **Validation**: per-module `valider_donnees()` functions with regex checks (author/member name letters-only, tel `^(06|07|05)\d{8}$`, email format, positive int pages, positive float prix) + `messagebox.showerror` feedback.
- **UI constants** duplicated at top of every module:
  - `bgColor = "#00c9a7"` (teal background), `prColor = "#12192c"` (dark navy), `textHolderColor = "#7a7e89"`
  - Font: `('Rubik', size)`
- **Treeview tables**: styled as `"Custom.Treeview"`, zebra rows via `oddrow` tag, sortable columns by clicking headings (`trierColumn`), search bar filtering via SQL LIKE.
- **Combobox ID convention**: option text is `"ID - label"`; code parses the ID with `.split('-')[0].strip()` before SQL calls. Preserve this format when touching comboboxes.
- All user-facing strings are **French**. Keep them French.

## Known Quirks / Gotchas

1. `ModifierLivre.modifier_livre` (livre.py ~line 414) references `self.disponible_var`, which no longer exists (checkbox commented out) -> clicking "Modifier Livre" raises AttributeError. Bug present in HEAD.
2. DB credentials are hardcoded and repeated in every module (no config module). If you centralize them, update all 5 files.
3. `valider_donnees` in `emprunt.py` is dead code (copied from adherent.py, never called).
4. `RetourneEmprunt.retourne_livre` does not verify the selected book belongs to the selected adherent beyond combobox filtering.
5. Dates: UI uses `dd/mm/yyyy`, MySQL needs `%Y-%m-%d`; conversion happens via strptime/strftime in emprunt flows.
6. `mainMenu.quitter` calls `tkinter.messagebox` - works only because `messagebox` was imported elsewhere; keep imports intact if refactoring.
7. Assets load via bare relative filenames -> app must run from repo root.

## When Making Changes

- Match the existing style: French labels/messages, duplicated color constants, page-class pattern, parameterized SQL.
- Do not introduce frameworks (Flask, SQLAlchemy, etc.) unless explicitly asked.
- There are no tests or linting configured; verify changes by running `python main.py` against a local `bibliotheque` database.
