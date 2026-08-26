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
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
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
    status TEXT NOT NULL CHECK (status IN ('sortie', 'entree'))
);
"""


def init_db():
    connection = connect()
    cursor = connection.cursor()
    cursor.executescript(SCHEMA)
    cursor.execute("SELECT COUNT(*) FROM login")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO login (username, password) VALUES (?, ?)",
                       ("admin", hash_password("admin")))
    else:
        cursor.execute("SELECT username, password FROM login")
        for username, password in cursor.fetchall():
            if "$" not in password:
                cursor.execute("UPDATE login SET password=? WHERE username=?",
                               (hash_password(password), username))
    connection.commit()
    cursor.close()
    connection.close()
