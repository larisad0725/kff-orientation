import sqlite3
from datetime import datetime

DB_NAME = "church.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        cohort_id INTEGER,
        created_at TEXT NOT NULL
    )
    """)

    # COHORTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cohorts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    )
    """)

    # COHORT SCHEDULE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cohort_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cohort_id INTEGER NOT NULL,
        week_number INTEGER NOT NULL,
        unlock_date TEXT,
        due_date TEXT
    )
    """)

    # MODULES (Fixed 8)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week_number INTEGER UNIQUE NOT NULL,
        title TEXT,
        video_url TEXT,
        content TEXT,
        reflection_required INTEGER DEFAULT 1,
        reading_required INTEGER DEFAULT 1
    )
    """)

    # PROGRESS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        week_number INTEGER,
        completed INTEGER DEFAULT 0,
        completed_at TEXT
    )
    """)

    # REFLECTIONS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reflections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        week_number INTEGER,
        submission TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()

    # Seed 8 modules if not exist
    for week in range(1, 9):
        cursor.execute("""
            INSERT OR IGNORE INTO modules (week_number, title)
            VALUES (?, ?)
        """, (week, f"Week {week}"))

    conn.commit()
    conn.close()


def user_exists(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None