import bcrypt
import streamlit as st
from database import get_connection, user_exists
from datetime import datetime

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def login(email: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and verify_password(password, user[3]):
        st.session_state.user = {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[4]
        }
        return True

    return False


def create_user(name: str, email: str, password: str, role: str):
    if user_exists(email):
        raise ValueError("User already exists")

    conn = get_connection()
    cursor = conn.cursor()

    hashed = hash_password(password)

    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        email,
        hashed,
        role,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()