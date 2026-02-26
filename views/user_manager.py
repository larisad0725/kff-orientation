import streamlit as st
from auth import create_user
from database import get_connection
import bcrypt

def render_user_manager(current_user_role):

    st.title("User Manager")

    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- CREATE USER ----------------
    st.markdown("## Create New User")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Temporary Password", type="password")

    if current_user_role == "super_admin":
        role_options = ["member", "pastor"]
    else:
        role_options = ["member"]

    role = st.selectbox("Role", role_options)

    if st.button("Create User"):
        try:
            create_user(name, email, password, role)
            st.success("User created successfully.")
        except Exception as e:
            st.error(str(e))

    st.divider()

    # ---------------- EXISTING USERS ----------------
    st.markdown("## Existing Users")

    cursor.execute("SELECT id, name, email, role FROM users")
    users = cursor.fetchall()

    for user in users:
        user_id, name, email, role = user

        # Pastor cannot see or edit super_admin accounts
        if current_user_role == "pastor" and role == "super_admin":
            continue

        with st.expander(f"{name} ({role})"):
            st.write(f"Email: {email}")

            new_password = st.text_input(
                f"Reset password for {name}",
                type="password",
                key=f"reset_{user_id}"
            )

            if st.button("Reset Password", key=f"btn_{user_id}"):

                if new_password:
                    hashed = bcrypt.hashpw(
                        new_password.encode(),
                        bcrypt.gensalt()
                    ).decode()

                    cursor.execute(
                        "UPDATE users SET password_hash=? WHERE id=?",
                        (hashed, user_id)
                    )
                    conn.commit()

                    st.success("Password updated.")
                else:
                    st.warning("Enter a password first.")

    conn.close()