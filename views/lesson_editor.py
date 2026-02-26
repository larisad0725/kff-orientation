import streamlit as st
from database import get_connection

def render_lesson_editor():

    st.title("Lesson Editor")

    conn = get_connection()
    cursor = conn.cursor()

    # Get modules
    cursor.execute("""
        SELECT week_number, title, video_url, content,
               reflection_required, reading_required
        FROM modules
        ORDER BY week_number
    """)
    modules = cursor.fetchall()

    week_options = [f"Week {m[0]}" for m in modules]
    selected_week_label = st.selectbox("Select Week", week_options)

    selected_week = int(selected_week_label.split()[1])

    module = next(m for m in modules if m[0] == selected_week)

    week_number, title, video_url, content, reflection_required, reading_required = module

    st.markdown(f"## Editing Week {week_number}")

    new_title = st.text_input("Lesson Title", value=title or "")
    new_video = st.text_input("YouTube Video URL", value=video_url or "")
    new_content = st.text_area("Reading Content (Markdown Supported)", value=content or "", height=300)

    new_reflection_required = st.checkbox("Require Reflection", value=bool(reflection_required))
    new_reading_required = st.checkbox("Require Reading Confirmation", value=bool(reading_required))

    if st.button("Save Lesson"):

        cursor.execute("""
            UPDATE modules
            SET title = ?, video_url = ?, content = ?,
                reflection_required = ?, reading_required = ?
            WHERE week_number = ?
        """, (
            new_title,
            new_video,
            new_content,
            int(new_reflection_required),
            int(new_reading_required),
            week_number
        ))

        conn.commit()
        st.success("Lesson updated successfully.")

    conn.close()