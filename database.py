import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        conn = sqlite3.connect("church.db")
        conn.row_factory = sqlite3.Row
        return conn


# ---------------- USER HELPERS ----------------

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


# ---------------- DATABASE INIT ----------------

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    if DATABASE_URL:
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
        CREATE TABLE IF NOT EXISTS cohorts (
            id SERIAL PRIMARY KEY,
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
            title TEXT NOT NULL,
            week INTEGER NOT NULL,
            content TEXT,
            is_published BOOLEAN DEFAULT FALSE
        )
        """)

    else:
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
        CREATE TABLE IF NOT EXISTS cohorts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cohort_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            cohort_id INTEGER
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            week INTEGER NOT NULL,
            content TEXT,
            is_published INTEGER DEFAULT 0
        )
        """)

    conn.commit()
    conn.close()