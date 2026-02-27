import os
import streamlit as st
import bcrypt
from datetime import datetime

from database import init_db, get_connection, DATABASE_URL
from auth import login

from views.lesson_editor import render_lesson_editor
from views.member_dashboard import render_member_dashboard
from views.pastor_dashboard import render_pastor_dashboard
from views.user_manager import render_user_manager
from views.super_admin import render_super_admin_panel
from views.cohort_manager import render_cohort_manager


# Initialize database
init_db()

st.set_page_config(page_title="Kingdom Family Fellowship", layout="wide")


def _ph() -> str:
    """DB placeholder: SQLite '?' vs Postgres '%s'."""
    return "%s" if DATABASE_URL else "?"


# ----------------- SETUP MODE (FIRST ADMIN) -----------------
setup_key_env = os.getenv("SETUP_KEY", "").strip()
setup_key_url = (st.query_params.get("setup_key") or "").strip()

# Tiny debug (remove after it works)
st.caption(f"DEBUG setup_key_url={'set' if bool(setup_key_url) else 'missing'} | setup_key_env={'set' if bool(setup_key_env) else 'missing'}")

def upsert_super_admin(name: str, email: str, password: str) -> None:
    ph = _ph()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT id FROM users WHERE email = {ph}", (email,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            f"UPDATE users SET name={ph}, password_hash={ph}, role={ph} WHERE email={ph}",
            (name, hashed, "super_admin", email),
        )
    else:
        cursor.execute(
            f"""
            INSERT INTO users (name, email, password_hash, role, created_at)
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            """,
            (name, email, hashed, "super_admin", datetime.now().isoformat()),
        )

    conn.commit()
    conn.close()


if setup_key_env and setup_key_url and setup_key_env == setup_key_url:
    st.title("🔧 KFF Setup Mode — Create Super Admin")
    st.warning("Create/reset the super admin. After this works, REMOVE SETUP_KEY from Render.")

    with st.form("create_super_admin_form"):
        name = st.text_input("Super Admin Name", value="Larisa")
        email = st.text_input("Super Admin Email (use a real email address)")
        password = st.text_input("Set Password", type="password")
        password2 = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Create / Reset Super Admin")

    if submitted:
        if not email or not password:
            st.error("Email and password are required.")
            st.stop()
        if password != password2:
            st.error("Passwords do not match.")
            st.stop()

        upsert_super_admin(name=name, email=email, password=password)
        st.success("✅ Super admin created/reset successfully.")
        st.info("Now go to the normal app URL (no setup_key) and log in.")
        st.stop()

    st.stop()

# ----------------- NORMAL APP -----------------

st.title("Kingdom Family Fellowship")
st.subheader("8-Week New Member Orientation")

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- LOGIN ----------------
if not st.session_state.user:
    st.markdown("### Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(email, password):
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------- APP ----------------
else:
    user = st.session_state.user
    role = user["role"]

    st.sidebar.write(f"Logged in as: {user['name']}")

    if role == "member":
        page = st.sidebar.radio("Navigation", ["Dashboard"])
        if page == "Dashboard":
            render_member_dashboard()

    elif role == "pastor":
        page = st.sidebar.radio("Navigation", [
            "Dashboard",
            "User Manager",
            "Cohort Manager",
            "Lesson Editor",
            "Reporting"
        ])

        if page == "Dashboard":
            render_pastor_dashboard()
        elif page == "User Manager":
            render_user_manager(role)
        elif page == "Cohort Manager":
            render_cohort_manager()
        elif page == "Lesson Editor":
            render_lesson_editor()
        elif page == "Reporting":
            from views.reporting_dashboard import render_reporting_dashboard
            render_reporting_dashboard()

    elif role == "super_admin":
        page = st.sidebar.radio("Navigation", [
            "System Panel",
            "Pastor Dashboard",
            "User Manager",
            "Cohort Manager",
            "Lesson Editor",
            "Reporting"
        ])

        if page == "System Panel":
            render_super_admin_panel()
        elif page == "Pastor Dashboard":
            render_pastor_dashboard()
        elif page == "User Manager":
            render_user_manager(role)
        elif page == "Cohort Manager":
            render_cohort_manager()
        elif page == "Lesson Editor":
            render_lesson_editor()
        elif page == "Reporting":
            from views.reporting_dashboard import render_reporting_dashboard
            render_reporting_dashboard()

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
