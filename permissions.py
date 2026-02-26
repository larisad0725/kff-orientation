import streamlit as st

def require_login():
    if "user" not in st.session_state or st.session_state.user is None:
        st.warning("Please log in.")
        st.stop()

def require_role(allowed_roles):
    require_login()

    if st.session_state.user["role"] not in allowed_roles:
        st.error("Access denied.")
        st.stop()