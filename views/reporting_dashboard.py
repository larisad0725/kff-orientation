import streamlit as st
from database import get_connection


def render_reporting_dashboard():
    st.title("Reporting Dashboard")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM users")
    result = cursor.fetchone()

    if isinstance(result, dict):
        total_users = result["count"]
    else:
        total_users = result[0]

    st.metric("Total Users", total_users)

    conn.close()
