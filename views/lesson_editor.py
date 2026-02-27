import streamlit as st
from database import get_connection, DATABASE_URL


def _ph():
    return "%s" if DATABASE_URL else "?"


def render_lesson_editor():
    st.title("Lesson Editor")

    conn = get_connection()
    cursor = conn.cursor()

    # ---- LOAD LESSONS ----
    cursor.execute("""
        SELECT id, week, title, content, is_published
        FROM lessons
        ORDER BY week
    """)
    rows = cursor.fetchall()

    if rows:
        st.subheader("Existing Lessons")

        for row in rows:
            if isinstance(row, dict):
                lesson_id = row["id"]
                week = row["week"]
                title = row["title"]
                content = row["content"]
                published = row["is_published"]
            else:
                lesson_id, week, title, content, published = row

            with st.expander(f"Week {week} - {title}"):
                st.write(content)
                st.write("Published:", published)

    # ---- CREATE / UPDATE LESSON ----
    st.subheader("Create / Update Lesson")

    week = st.number_input("Week Number", min_value=1, max_value=8, step=1)
    title = st.text_input("Lesson Title")
    content = st.text_area("Lesson Content")
    published = st.checkbox("Publish Lesson")

    if st.button("Save Lesson"):
        ph = _ph()

        cursor.execute(
            f"SELECT id FROM lessons WHERE week = {ph}",
            (week,)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                f"""
                UPDATE lessons
                SET title={ph}, content={ph}, is_published={ph}
                WHERE week={ph}
                """,
                (title, content, published, week)
            )
        else:
            cursor.execute(
                f"""
                INSERT INTO lessons (week, title, content, is_published)
                VALUES ({ph}, {ph}, {ph}, {ph})
                """,
                (week, title, content, published)
            )

        conn.commit()
        st.success("Lesson saved successfully.")
        st.rerun()

    conn.close()