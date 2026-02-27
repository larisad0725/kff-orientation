import streamlit as st
from database import get_connection


def render_super_admin_panel():
    st.title("System Panel")
    st.subheader("Database Overview")

    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- TOTAL USERS ----------------
    cursor.execute("SELECT COUNT(*) AS count FROM users")
    result = cursor.fetchone()

    if isinstance(result, dict):
        user_count = result["count"]
    else:
        user_count = result[0]

    st.metric("Total Users", user_count)

    # ---------------- TOTAL COHORTS ----------------
    cursor.execute("SELECT COUNT(*) AS count FROM cohorts")
    result = cursor.fetchone()

    if isinstance(result, dict):
        cohort_count = result["count"]
    else:
        cohort_count = result[0]

    st.metric("Total Cohorts", cohort_count)

    # ---------------- TOTAL TRACKS ----------------
    cursor.execute("SELECT COUNT(*) AS count FROM tracks")
    result = cursor.fetchone()

    if isinstance(result, dict):
        track_count = result["count"]
    else:
        track_count = result[0]

    st.metric("Total Tracks", track_count)

    conn.close()