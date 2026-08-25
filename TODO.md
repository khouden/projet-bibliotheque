# TODO — Make projet-bibliotheque a shippable Windows app

Decisions made: **migrate MySQL -> SQLite**, **delete modifier_emprunt**.

## High priority — crash bugs & migration

- [ ] Fix `livre.py` AttributeError: remove `self.disponible_var` references (~lines 414, 470)
- [ ] Delete `modifier_emprunt()` from `mainMenu.py`
- [ ] Create `db.py`: sqlite3 connection helper + first-run schema bootstrap (tables + seeded login row)
- [ ] Migrate `login/livre/adherent/emprunt/mainMenu` from `mysql.connector` to `sqlite3`
  - `%s` placeholders -> `?`
  - `CONCAT_WS('', cols) LIKE` -> `cols joined with || LIKE`
  - `AUTO_INCREMENT` -> `INTEGER PRIMARY KEY AUTOINCREMENT`
- [ ] Verify full flow after fixes: `python main.py`, exercise login/livre/adherent/emprunt pages

## Medium priority — robustness & hygiene

- [ ] Replace bare excepts with `sqlite3.Error` catches in delete flows
- [ ] Create `requirements.txt` (tkcalendar only; sqlite3 is stdlib)
- [ ] Resolve PNG asset paths via `os.path` relative to `__file__` (+ PyInstaller `sys._MEIPASS` support)
- [ ] Hash login passwords (sha256), seed hash at bootstrap, compare hashes in `Login.login()`
- [ ] Change `RetourneEmprunt` to UPDATE existing `sortie` row instead of INSERT new row
- [ ] Update `AGENTS.md` + `README.md` to reflect SQLite architecture

## Low priority — packaging & extras

- [ ] Convert `icon.png` to `icon.ico` for exe/taskbar icon
- [ ] Build `.exe` with PyInstaller (`--windowed --add-data "*.png;."`) and test launch on clean machine
- [ ] Optional: add emprunt edit/delete pages + due date column
