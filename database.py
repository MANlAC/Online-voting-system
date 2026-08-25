import os

DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    # PostgreSQL (Render, etc.)
    import psycopg2
    import psycopg2.extras

    def get_db_connection():
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        conn.autocommit = False
        return conn

    def get_cursor(conn):
        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def init_db():
        conn = get_db_connection()
        cur = get_cursor(conn)

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                voter_id INTEGER UNIQUE,
                name TEXT,
                password TEXT,
                role TEXT,
                has_voted INTEGER DEFAULT 0
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS candidates (
                id SERIAL PRIMARY KEY,
                name TEXT,
                bio TEXT DEFAULT '',
                photo TEXT DEFAULT '',
                votes INTEGER DEFAULT 0
            )
            """
        )

        cur.execute("SELECT COUNT(*) AS cnt FROM users")
        if cur.fetchone()["cnt"] == 0:
            from werkzeug.security import generate_password_hash
            cur.execute(
                "INSERT INTO users (voter_id, name, password, role, has_voted) VALUES (%s, %s, %s, %s, %s)",
                (101, "Test User", generate_password_hash("1234"), "Voter", 0),
            )
            cur.execute(
                "INSERT INTO users (voter_id, name, password, role, has_voted) VALUES (%s, %s, %s, %s, %s)",
                (999, "Admin", generate_password_hash("admin123"), "Admin", 0),
            )

        cur.execute("SELECT COUNT(*) AS cnt FROM candidates")
        if cur.fetchone()["cnt"] == 0:
            candidates = [
                ("DONALD TRUMP", "45th President of the United States"),
                ("VLADIMIR PUTIN", "President of the Russian Federation"),
                ("BARACK OBAMA", "44th President of the United States"),
            ]
            for name, bio in candidates:
                cur.execute(
                    "INSERT INTO candidates (name, bio, votes) VALUES (%s, %s, %s)",
                    (name, bio, 0),
                )

        conn.commit()
        cur.close()
        conn.close()

else:
    # SQLite fallback for local development
    import sqlite3

    DB_PATH = DATABASE_URL if DATABASE_URL else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "voting_system.db"
    )

    def get_db_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def get_cursor(conn):
        return conn.cursor()

    def init_db():
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
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

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                bio TEXT DEFAULT '',
                photo TEXT DEFAULT '',
                votes INTEGER DEFAULT 0
            )
            """
        )

        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            from werkzeug.security import generate_password_hash
            cur.execute(
                "INSERT INTO users (voter_id, name, password, role, has_voted) VALUES (?, ?, ?, ?, ?)",
                (101, "Test User", generate_password_hash("1234"), "Voter", 0),
            )
            cur.execute(
                "INSERT INTO users (voter_id, name, password, role, has_voted) VALUES (?, ?, ?, ?, ?)",
                (999, "Admin", generate_password_hash("admin123"), "Admin", 0),
            )

        cur.execute("SELECT COUNT(*) FROM candidates")
        if cur.fetchone()[0] == 0:
            candidates = [
                ("DONALD TRUMP", "45th President of the United States"),
                ("VLADIMIR PUTIN", "President of the Russian Federation"),
                ("BARACK OBAMA", "44th President of the United States"),
            ]
            for name, bio in candidates:
                cur.execute(
                    "INSERT INTO candidates (name, bio, votes) VALUES (?, ?, ?)",
                    (name, bio, 0),
                )

        conn.commit()
        conn.close()


# Determine the right SQL placeholder for the active database backend
_IS_PG = bool(DATABASE_URL and DATABASE_URL.startswith("postgres"))
PH = "%s" if _IS_PG else "?"


def new_conn_and_cursor():
    """Return (connection, cursor) as a convenience helper."""
    conn = get_db_connection()
    cur = get_cursor(conn)
    return conn, cur


init_db()
