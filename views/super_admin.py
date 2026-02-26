import streamlit as st
from database import get_connection

def render_super_admin_panel():
    st.title("Super Admin System Panel")

    st.markdown("### System Controls")

    st.info("This panel is reserved for system-level operations.")

    st.divider()

    st.markdown("### Database Overview")

    conn = get_connection()
    cursor = conn.cursor()

    # Count users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    st.write(f"Total Users: {user_count}")

    conn.close()

    st.divider()

    st.warning("⚠ Future system controls will appear here.")