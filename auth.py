import bcrypt
from datetime import datetime
from database import get_connection, user_exists, DATABASE_URL
import streamlit as st


def _ph() -> str:
    """
    Returns the correct placeholder for the active DB driver.
    SQLite uses '?', psycopg2/Postgres uses '%s'.
    """
    return "%s" if DATABASE_URL else "?"


def create_user(name: str, email: str, password: str, role: str = "member") -> None:
    if user_exists(email):
        raise ValueError("User already exists")

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = get_connection()
    cursor = conn.cursor()

    ph = _ph()
    cursor.execute(
        f"""
        INSERT INTO users (name, email, password_hash, role, created_at)
        VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
        """,
        (name, email, password_hash, role, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()


def login(email: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    ph = _ph()
    cursor.execute(
        f"SELECT id, name, email, password_hash, role FROM users WHERE email={ph}",
        (email,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    # Row shape differs:
    # - Postgres RealDictCursor => dict-like
    # - SQLite Row => dict-like
    password_hash = row["password_hash"] if isinstance(row, dict) or hasattr(row, "__getitem__") else row[3]

    if bcrypt.checkpw(password.encode(), password_hash.encode()):
        # Normalize user dict into session_state
        user = {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "role": row["role"],
        }
        st.session_state.user = user
        return True

    return False