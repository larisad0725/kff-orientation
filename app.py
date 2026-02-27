import streamlit as st

from database import init_db
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