# AGENTS.md

Context file for AI agents working on this repository. Read this before making any change.

## Project Overview

**projet-bibliotheque** ("library project") is a French-language **standalone desktop Library Management System** built as a school/team project by Abdellah Khouden, Abderrahim Bensaid, and Othman Elhyane (supervised by Mr. Abdellah Sair).

It manages three entities:
- **Livre** (books): add, list/search/sort, modify, delete
- **Adherent** (members): add, list/search/sort, modify, delete
- **Emprunt** (loans): take a book (status `sortie`), return a book (status `entree`), list/search loans

Authentication is **password-only** (no username). On first launch a setup screen asks the user to define their password (stored as a PBKDF2 hash with `must_change=1`); afterwards a single login field is shown.

## Tech Stack

- **Python 3.10+** (uses `match/case`)
- **GUI**: Tkinter / ttk (`PhotoImage` for PNGs, no Pillow)
- **Calendar widget**: `tkcalendar` (`DateEntry`)
- **Database**: SQLite via stdlib `sqlite3`, wrapped by `db.py`. The database is a single file `bibliotheque.db`, created automatically next to the app on first launch. No server, no credentials.
- Only external dependency: `tkcalendar` (`requirements.txt`). No virtual env committed.

## How to Run

```powershell
pip install -r requirements.txt
python main.py
```

Log in with your password (first launch opens the "First use" screen to define it). Delete `bibliotheque.db` to reset to factory state (setup screen reappears on next start).

## File Map

| File | Role |
|---|---|
| `main.py` | Entry point. Calls `init_db()` then creates root window (925x600) and starts `Login`. |
| `login.py` | `Login`: single password field, verifies PBKDF2 hash via `db.verify_password`, then swaps content frame for `MainMenu`. Also hosts `FirstSetup`, the first-run "define your password" screen. |
| `mainMenu.py` | `MainMenu`: menubar (options/Livre/Adherent/Emprunt) + home screen with 3 comboboxes acting as quick navigation. Routes to page classes via `match/case`. |
| `db.py` | SQLite layer: `connect()` (foreign keys ON), `init_db()` (schema bootstrap + legacy-table migration), `needs_setup()`/`set_password()`, `hash_password`/`verify_password` (PBKDF2-HMAC-SHA256, stored as `salt$digest` hex). |
| `paths.py` | `asset_path(filename)`: resolves PNG assets relative to the script dir, or `sys._MEIPASS` when frozen by PyInstaller. |
| `livre.py` | Book pages: `AfficherLivres` (Treeview + search + column sort), `AjouterLivre`, `ModifierLivre` (also delete). Shared `valider_donnees()` and `clearPage()`. |
| `adherent.py` | Member pages: `AfficherAdherents`, `AjouterAdherent`, `ModifierAdherent` (also delete). Own copy of `valider_donnees()` / `clearPage()`. |
| `emprunt.py` | Loan pages: `AfficherEmprunts`, `PrendreEmprunt` (checkout), `RetourneEmprunt` (return = UPDATE existing row). Uses `tkcalendar.DateEntry`. |
| `TODO.md` | Remaining roadmap to a shippable Windows exe. Keep in sync with actual progress. |
| `code in one file.py` | Legacy monolithic MySQL-era prototype (~441 lines). Reference only - do not import or edit. |
| `*.png` | UI assets loaded via `asset_path`: `icon.png`, `login2.png`, `background.png`, `ajouter_livre.png`, `ajouter_adherent.png`, `ajouter_emprunt.png`. Must stay in repo root. |
| `bibliotheque.db` | Runtime artifact (gitignored). Never commit; safe to delete. |

## Database Schema (SQLite, file `bibliotheque.db`)

Created by `db.init_db()` if missing:

```sql
CREATE TABLE login (
    id INTEGER PRIMARY KEY CHECK (id = 1),   -- single-row table
    password TEXT NOT NULL,                  -- format: hex_salt$hex_digest (PBKDF2-SHA256, 100k iters)
    must_change INTEGER NOT NULL DEFAULT 1   -- 1 = password not yet defined -> FirstSetup screen
);
CREATE TABLE livre (
    idLiv INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    nomauteur TEXT NOT NULL,
    pages INTEGER,
    prix REAL,
    disponible TEXT NOT NULL DEFAULT 'oui' CHECK (disponible IN ('oui','non'))
);
CREATE TABLE adherent (
    idAdh INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    tel TEXT,                            -- optional; international format, 7-15 digits
    email TEXT
);
CREATE TABLE emprunt (
    idEmp INTEGER PRIMARY KEY AUTOINCREMENT,
    idAdh INTEGER NOT NULL REFERENCES adherent(idAdh),
    idLiv INTEGER NOT NULL REFERENCES livre(idLiv),
    dateemprunt TEXT NOT NULL,           -- 'YYYY-MM-DD'
    status TEXT NOT NULL CHECK (status IN ('sortie','entree'))
);
```

Loan lifecycle: `PrendreEmprunt` INSERTs an emprunt (`sortie`) + sets `disponible='non'`. `RetourneEmprunt` UPDATEs the existing `sortie` row to `entree` (guarded by `cursor.rowcount`) + sets `disponible='oui'`. Foreign keys are enforced (`PRAGMA foreign_keys=ON`), so deleting a livre/adherent that has emprunts raises `sqlite3.IntegrityError`, caught in the delete flows with a friendly messagebox.

## Architecture & Conventions

- **Single-window SPA pattern**: one `Tk` root forever. Each page is a class taking `root` in `__init__` and packing a `Frame` into it. Navigation = destroy all child `Frame`s (`clearPage()` / `clear_widgets()`) then instantiate the next page class. There is no router.
- **DB access**: `from db import connect`; open/close inside each method. Parameterized `?` placeholders everywhere. Search filters use `(COALESCE(col,'') || ' ' || ...) LIKE ?` concatenation chains.
- **Validation**: `valider_donnees()` per module with regex checks. Tel is **optional**, validated as international format (optional `+`, digits/spaces/dashes/parens/dots, 7-15 digits). Author/member name letters-only; positive int pages; positive float prix. Errors via `messagebox.showerror` in French.
- **Error handling**: delete flows catch `sqlite3.IntegrityError` (FK block) separately from generic `sqlite3.Error`; connections closed in `finally`.
- **UI constants** duplicated at top of every module:
  - `bgColor = "#00c9a7"` (teal background), `prColor = "#12192c"` (dark navy), `textHolderColor = "#7a7e89"`
  - Font: `('Rubik', size)`
- **Treeview tables**: styled `"Custom.Treeview"`, zebra rows via `oddrow` tag, sortable columns (`trierColumn`), SQL-LIKE search bar.
- **Combobox ID convention**: option text is `"ID - label"`; parsed with `.split('-')[0].strip()` before SQL calls. Preserve this format when touching comboboxes.
- All user-facing strings are **English** (UI translated 2026; keep them English).
- **Loan status tokens stay French in the database**: `'sortie'`/`'entree'` are stored values guarded by a CHECK constraint and used in query filters. `AfficherEmprunts` maps them to `Borrowed`/`Returned` for display via `STATUS_LABELS`. Never translate the tokens themselves without migrating existing rows + the CHECK constraint.

## Known Quirks / Gotchas

1. `valider_donnees` in `emprunt.py` is dead code (copied from adherent.py, never called) - kept in sync anyway.
2. The date field on the return screen is display-only; the schema stores a single `dateemprunt` (borrow date). Return date is not recorded anywhere.
3. `mainMenu.quitter` calls `tkinter.messagebox.askyesno` - works only because `messagebox` was imported elsewhere; keep imports intact if refactoring.
4. Modifier pages stash the selected row's ID in `self.selected_book_id` / `self.selected_adherent_id` set by `selecterCol`.
5. Assets load via `asset_path`, so cwd no longer matters, but PNGs must ship alongside the code (or be `--add-data`-bundled when freezing).
6. Window is fixed 925x600, non-resizable; layouts use absolute `place()` coordinates.
7. `code in one file.py` predates the SQLite migration and still references MySQL - ignore it.

## When Making Changes

- Match the existing style: French labels/messages, duplicated color constants, page-class pattern, parameterized SQL through `db.connect()`.
- Do not introduce frameworks (Flask, SQLAlchemy, etc.) unless explicitly asked.
- There are no tests or linting configured; verify changes by running `python main.py` and exercising the affected pages against the local `bibliotheque.db`.
