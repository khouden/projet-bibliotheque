# TODO — projet-bibliotheque roadmap

## ✅ Done (v1.0 core)

- [x] Fix crash bugs: `disponible_var` refs, `modifier_emprunt` misroute, negative pages/prix TypeError
- [x] Migrate MySQL -> SQLite (`db.py`, bootstrap + seed, `?` placeholders, `COALESCE||` search, proper JOINs)
- [x] Bare excepts -> targeted `sqlite3.IntegrityError`/`Error` handlers
- [x] `requirements.txt` (tkcalendar only)
- [x] cwd-independent asset paths (`paths.py`)
- [x] PBKDF2-HMAC-SHA256 password hashing + legacy plaintext upgrade
- [x] Password-only auth with first-run "define your password" screen (no default credentials)
- [x] Return = UPDATE existing `sortie` row (rowcount guard), no duplicate rows
- [x] Optional international phone validation (7-15 digits)
- [x] Full English UI translation (+ status display mapping `Borrowed`/`Returned`)
- [x] Enter-key submit on login/setup forms
- [x] Multi-size `icon.ico`, PyInstaller onefile exe builds and runs
- [x] Docs: AGENTS.md + README.md reflect current architecture

## 🔴 P0 — before release

- [x] Global crash handler: catch uncaught exceptions, write `error.log`, show friendly dialog (windowed exe hides tracebacks)
- [x] "Change password" entry in Options menu (reuse `db.set_password()`)
- [x] Due dates: store expected return date, highlight overdue loans red in list, "N days late" hint
- [x] Loan edit/delete pages (fix data-entry mistakes)

## 🟡 P1 — cheap wins / polish

- [ ] CSV export buttons for books/members/loans
- [ ] Home dashboard stats on background image (total books · available · members · active loans)
- [ ] Live search (filter as you type) + Clear button on all list pages
- [ ] High-DPI awareness call so text isn't blurry on modern laptops
- [ ] Double-click a row in a list -> opens Edit page preselected

## 🟢 P2 — optional / v2

- [ ] Exe version info resource (product name/version in file Properties)
- [ ] Inno Setup installer (vs portable exe)
- [ ] DB backup copy (`bibliotheque.db.bak`) on exit
- [ ] Borrow history per member/book view

## 📦 Release checklist

- [ ] Rebuild exe after any code change
- [ ] Test exe on a clean machine without Python
- [ ] Full manual pass: first-use setup, login, books CRUD, members CRUD, borrow/return cycle, overdue display, change password
