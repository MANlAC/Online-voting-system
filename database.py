import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DATABASE_URL", os.path.join(BASE_DIR, "voting_system.db"))


def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id INTEGER UNIQUE,
            name TEXT,
            password TEXT,
            role TEXT,
            has_voted INTEGER DEFAULT 0
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            votes INTEGER DEFAULT 0
        )
        """
    )

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (voter_id, name, password, role, has_voted) VALUES (?, ?, ?, ?, ?)",
            (101, "Test User", "1234", "Voter", 0),
        )
        cursor.execute(
            "INSERT INTO users (voter_id, name, password, role, has_voted) VALUES (?, ?, ?, ?, ?)",
            (999, "Admin", "admin123", "Admin", 0),
        )

    cursor.execute("SELECT COUNT(*) FROM candidates")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO candidates (name, votes) VALUES (?, ?)",
            [
                ("DONALD TRUMP", 0),
                ("VLADMIR PUTIN", 0),
                ("BARACK OBAMA", 0),
            ],
        )

    db.commit()
    db.close()


init_db()
db = get_db_connection()
cursor = db.cursor()