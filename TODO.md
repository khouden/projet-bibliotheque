# TODO — Make projet-bibliotheque a shippable Windows app

Decisions made: **migrated MySQL -> SQLite**, **modifier_emprunt deleted**.

## High priority — crash bugs & migration  ✅ DONE

- [x] Fix `livre.py` AttributeError: remove `self.disponible_var` references
- [x] Delete `modifier_emprunt()` from `mainMenu.py`
- [x] Create `db.py`: sqlite3 connection helper + first-run schema bootstrap (tables + seeded login row)
- [x] Migrate all modules from `mysql.connector` to `sqlite3` (`?` placeholders, `COALESCE||` search chains, proper JOINs)
- [x] Verify: compile + db smoke tests (FK block, CHECK constraints, idempotent seed) + app launch

## Medium priority — robustness & hygiene  ✅ DONE

- [x] Replace bare excepts with `sqlite3.IntegrityError` / `sqlite3.Error` catches in delete flows (+ `finally` close)
- [x] Create `requirements.txt` (tkcalendar only; sqlite3 is stdlib)
- [x] Resolve PNG asset paths via `paths.asset_path()` (`__file__` + PyInstaller `sys._MEIPASS`)
- [x] Hash login passwords (PBKDF2-HMAC-SHA256, salted), seed hash at bootstrap, auto-upgrade legacy plaintext rows
- [x] Change `RetourneEmprunt` to UPDATE existing `sortie` row instead of INSERT new row (rowcount guard)
- [x] Optional international tel validation (empty allowed, 7-15 digits, `+`/spaces/dashes/parens/dots)
- [x] Update `AGENTS.md` + `README.md` to reflect SQLite architecture

## Low priority — packaging

- [x] Convert `icon.png` to multi-size `icon.ico` (16→256px)
- [x] Build `.exe` with PyInstaller onefile/windowed — verified launch + DB creation next to exe (22.9 MB)
- [ ] Test the exe on a clean machine without Python installed (copy `dist\bibliotheque.exe` alone)

## Optional enhancements

- [ ] Emprunt edit/delete pages + due date column / late-loan highlighting
