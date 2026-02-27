import streamlit as st
from datetime import datetime
from database import get_connection, DATABASE_URL


def _ph():
    return "%s" if DATABASE_URL else "?"


def render_track_manager():
    st.title("Track Manager")
    st.subheader("Create and Manage Orientation Tracks")

    conn = get_connection()
    cursor = conn.cursor()
    ph = _ph()

    # ================= CREATE TRACK =================
    st.markdown("### Create New Track")

    with st.form("create_track_form"):
        name = st.text_input("Track Name")
        description = st.text_area("Description")
        submitted = st.form_submit_button("Create Track")

        if submitted:
            if not name:
                st.error("Track name is required.")
            else:
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

    # ================= LIST TRACKS =================
    st.markdown("### Existing Tracks")

    cursor.execute("SELECT id, name, description, is_active FROM tracks ORDER BY id")
    tracks = cursor.fetchall()

    if not tracks:
        st.info("No tracks created yet.")
        conn.close()
        return

    for track in tracks:
        if isinstance(track, dict):
            track_id = track["id"]
            name = track["name"]
            description = track["description"]
            active = track["is_active"]
        else:
            track_id, name, description, active = track

        status = "Active" if active else "Inactive"

        with st.expander(f"{name} ({status})"):

            st.write(description or "No description provided.")

            col1, col2 = st.columns(2)

            # -------- TOGGLE ACTIVE --------
            with col1:
                if st.button("Toggle Active Status", key=f"toggle_{track_id}"):
                    cursor.execute(
                        f"UPDATE tracks SET is_active = {ph} WHERE id = {ph}",
                        (not active, track_id)
                    )
                    conn.commit()
                    st.rerun()

            # -------- SAFE DELETE --------
            with col2:
                if st.button("Delete Track", key=f"delete_{track_id}"):

                    # Check for linked cohorts
                    cursor.execute(
                        f"SELECT COUNT(*) FROM cohorts WHERE track_id = {ph}",
                        (track_id,)
                    )
                    cohort_result = cursor.fetchone()

                    if isinstance(cohort_result, dict):
                        cohort_count = list(cohort_result.values())[0]
                    else:
                        cohort_count = cohort_result[0]

                    # Check for linked lessons
                    cursor.execute(
                        f"SELECT COUNT(*) FROM lessons WHERE track_id = {ph}",
                        (track_id,)
                    )
                    lesson_result = cursor.fetchone()

                    if isinstance(lesson_result, dict):
                        lesson_count = list(lesson_result.values())[0]
                    else:
                        lesson_count = lesson_result[0]

                    if cohort_count > 0 or lesson_count > 0:
                        st.error(
                            "Cannot delete this track because it has "
                            f"{cohort_count} cohort(s) and "
                            f"{lesson_count} lesson(s) attached."
                        )
                    else:
                        cursor.execute(
                            f"DELETE FROM tracks WHERE id = {ph}",
                            (track_id,)
                        )
                        conn.commit()
                        st.success("Track deleted successfully.")
                        st.rerun()

    conn.close()