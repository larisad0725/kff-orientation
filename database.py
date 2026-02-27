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


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- USERS ----------------
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

    # ---------------- TRACKS ----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TEXT
        )
    """)

    # ---------------- COHORTS ----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cohorts (
            id SERIAL PRIMARY KEY,
            track_id INTEGER REFERENCES tracks(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT
        )
    """)

    # ---------------- COHORT MEMBERS ----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cohort_members (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            cohort_id INTEGER REFERENCES cohorts(id) ON DELETE CASCADE
        )
    """)

    # ---------------- LESSONS ----------------
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

    conn.commit()
    conn.close()