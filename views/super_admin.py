import streamlit as st
from database import get_connection, DATABASE_URL


def render_super_admin_panel():
    st.title("System Panel")
    st.subheader("Database Overview")

    conn = get_connection()
    cursor = conn.cursor()

    # Use correct SQL placeholder style (no placeholders needed here)
    cursor.execute("SELECT COUNT(*) AS count FROM users")
    result = cursor.fetchone()

    # Postgres (RealDictCursor) returns dict
    if isinstance(result, dict):
        user_count = result["count"]
    else:
        # SQLite returns tuple
        user_count = result[0]

    st.metric("Total Users", user_count)

    cursor.execute("SELECT COUNT(*) AS count FROM cohorts")
    result = cursor.fetchone()

    if isinstance(result, dict):
        cohort_count = result["count"]
    else:
        cohort_count = result[0]

    st.metric("Total Cohorts", cohort_count)

    conn.close()