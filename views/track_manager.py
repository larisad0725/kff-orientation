import streamlit as st
from datetime import datetime
from database import get_connection, DATABASE_URL


def _ph():
    return "%s" if DATABASE_URL else "?"


def render_track_manager():
    st.title("Track Manager")

    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- CREATE TRACK ----------------
    st.subheader("Create New Track")

    name = st.text_input("Track Name")
    description = st.text_area("Description")

    if st.button("Create Track"):
        if not name:
            st.error("Track name is required.")
        else:
            ph = _ph()
            cursor.execute(
                f"""
                INSERT INTO tracks (name, description, created_at)
                VALUES ({ph}, {ph}, {ph})
                """,
                (name, description, datetime.now().isoformat())
            )
            conn.commit()
            st.success("Track created successfully.")
            st.rerun()

    # ---------------- LIST TRACKS ----------------
    st.subheader("Existing Tracks")

    cursor.execute("SELECT id, name, description, is_active FROM tracks ORDER BY id")
    tracks = cursor.fetchall()

    if not tracks:
        st.info("No tracks created yet.")

    for track in tracks:
        if isinstance(track, dict):
            track_id = track["id"]
            name = track["name"]
            description = track["description"]
            active = track["is_active"]
        else:
            track_id, name, description, active = track

        with st.expander(f"{name} {'(Active)' if active else '(Inactive)'}"):
            st.write(description)

            toggle_label = "Deactivate" if active else "Activate"

            if st.button(toggle_label, key=f"toggle_{track_id}"):
                ph = _ph()
                cursor.execute(
                    f"UPDATE tracks SET is_active = {ph} WHERE id = {ph}",
                    (not active, track_id)
                )
                conn.commit()
                st.rerun()

    conn.close()