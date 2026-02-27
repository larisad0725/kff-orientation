import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")


# ---------------- CONNECTION ----------------

def get_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        conn = sqlite3.connect("church.db")
        conn.row_factory = sqlite3.Row
        return conn


def _ph():
    return "%s" if DATABASE_URL else "?"


# ---------------- USER EXISTS ----------------

def user_exists(email):
    conn = get_connection()
    cursor = conn.cursor()

    if DATABASE_URL:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    else:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))

    user = cursor.fetchone()
    conn.close()
    return user is not None


# ---------------- INIT DB ----------------

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    if DATABASE_URL:
        # ================= POSTGRES =================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cohorts (
                id SERIAL PRIMARY KEY,
                track_id INTEGER REFERENCES tracks(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cohort_members (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                cohort_id INTEGER REFERENCES cohorts(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id SERIAL PRIMARY KEY,
                track_id INTEGER REFERENCES tracks(id) ON DELETE CASCADE,
                week INTEGER NOT NULL,
                title TEXT NOT NULL,
                key_scripture TEXT,
                video_url TEXT,
                facilitator_notes TEXT,
                participant_content TEXT,
                homework_instructions TEXT,
                is_published BOOLEAN DEFAULT FALSE
            )
        """)

    else:
        # ================= SQLITE =================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cohorts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER,
                name TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                FOREIGN KEY(track_id) REFERENCES tracks(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cohort_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                cohort_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(cohort_id) REFERENCES cohorts(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER,
                week INTEGER NOT NULL,
                title TEXT NOT NULL,
                key_scripture TEXT,
                video_url TEXT,
                facilitator_notes TEXT,
                participant_content TEXT,
                homework_instructions TEXT,
                is_published INTEGER DEFAULT 0,
                FOREIGN KEY(track_id) REFERENCES tracks(id)
            )
        """)

    conn.commit()
    conn.close()