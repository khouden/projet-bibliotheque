import os
import sys
import sqlite3
import hashlib
import hmac

DB_NAME = "bibliotheque.db"

PBKDF2_ITERATIONS = 100_000


def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password, stored):
    parts = stored.split("$")
    if len(parts) != 2:
        return False
    try:
        salt = bytes.fromhex(parts[0])
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


def db_path():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, DB_NAME)


def connect():
    connection = sqlite3.connect(db_path())
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


SCHEMA = """
CREATE TABLE IF NOT EXISTS login (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    password TEXT NOT NULL,
    must_change INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS livre (
    idLiv INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    nomauteur TEXT NOT NULL,
    pages INTEGER,
    prix REAL,
    disponible TEXT NOT NULL DEFAULT 'oui' CHECK (disponible IN ('oui', 'non'))
);

CREATE TABLE IF NOT EXISTS adherent (
    idAdh INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    tel TEXT,
    email TEXT
);

CREATE TABLE IF NOT EXISTS emprunt (
    idEmp INTEGER PRIMARY KEY AUTOINCREMENT,
    idAdh INTEGER NOT NULL REFERENCES adherent(idAdh),
    idLiv INTEGER NOT NULL REFERENCES livre(idLiv),
    dateemprunt TEXT NOT NULL,
    dateretourprevue TEXT,
    status TEXT NOT NULL CHECK (status IN ('sortie', 'entree'))
);
"""


LOGIN_DDL = """
CREATE TABLE login (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    password TEXT NOT NULL,
    must_change INTEGER NOT NULL DEFAULT 1
)
"""


def _migrate_login_table(cursor):
    cols = [row[1] for row in cursor.execute("PRAGMA table_info(login)").fetchall()]
    if "username" not in cols:
        return
    row = cursor.execute("SELECT password FROM login").fetchone()
    legacy_password = row[0] if row else None
    cursor.execute("DROP TABLE login")
    cursor.execute(LOGIN_DDL)
    if legacy_password and "$" in legacy_password:
        cursor.execute("INSERT INTO login (id, password, must_change) VALUES (1, ?, 0)",
                       (legacy_password,))


def _migrate_emprunt_table(cursor):
    cols = [row[1] for row in cursor.execute("PRAGMA table_info(emprunt)").fetchall()]
    if "dateretourprevue" not in cols:
        cursor.execute("ALTER TABLE emprunt ADD COLUMN dateretourprevue TEXT")


def init_db():
    connection = connect()
    cursor = connection.cursor()
    cursor.executescript(SCHEMA)
    _migrate_login_table(cursor)
    _migrate_emprunt_table(cursor)
    cursor.execute("SELECT COUNT(*) FROM login")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO login (id, password, must_change) VALUES (1, ?, 1)",
                       (hash_password(os.urandom(16).hex()),))
    connection.commit()
    cursor.close()
    connection.close()


def needs_setup():
    connection = connect()
    cursor = connection.cursor()
    row = cursor.execute("SELECT must_change FROM login WHERE id = 1").fetchone()
    cursor.close()
    connection.close()
    return row is None or bool(row[0])


def set_password(password):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("INSERT OR REPLACE INTO login (id, password, must_change) VALUES (1, ?, 0)",
                   (hash_password(password),))
    connection.commit()
    cursor.close()
    connection.close()
