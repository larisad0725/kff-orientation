import streamlit as st
from database import get_connection
from datetime import datetime

def render_cohort_manager():

    st.title("Cohort Manager")

    conn = get_connection()
    cursor = conn.cursor()

    # ===============================
    # CREATE COHORT
    # ===============================
    st.markdown("## Create New Cohort")

    cohort_name = st.text_input("Cohort Name")

    if st.button("Create Cohort"):
        if cohort_name:
            cursor.execute("""
                INSERT INTO cohorts (name, created_at)
                VALUES (?, ?)
            """, (cohort_name, datetime.now().isoformat()))

            cohort_id = cursor.lastrowid

            # Create 8-week schedule automatically
            for week in range(1, 9):
                cursor.execute("""
                    INSERT INTO cohort_schedule (cohort_id, week_number)
                    VALUES (?, ?)
                """, (cohort_id, week))

            conn.commit()
            st.success("Cohort created with 8-week schedule.")
        else:
            st.warning("Enter a cohort name.")

    st.divider()

    # ===============================
    # ASSIGN MEMBER TO COHORT
    # ===============================
    st.markdown("## Assign Member to Cohort")

    cursor.execute("SELECT id, name FROM cohorts")
    cohorts = cursor.fetchall()

    cursor.execute("SELECT id, name FROM users WHERE role='member'")
    members = cursor.fetchall()

    if cohorts and members:

        cohort_dict = {name: cid for cid, name in cohorts}
        member_dict = {name: uid for uid, name in members}

        selected_member = st.selectbox("Select Member", list(member_dict.keys()))
        selected_cohort = st.selectbox("Select Cohort", list(cohort_dict.keys()))

        if st.button("Assign to Cohort"):
            cursor.execute("""
                UPDATE users
                SET cohort_id = ?
                WHERE id = ?
            """, (
                cohort_dict[selected_cohort],
                member_dict[selected_member]
            ))

            conn.commit()
            st.success("Member assigned to cohort.")

    else:
        st.info("Create at least one cohort and one member first.")

    st.divider()

    # ===============================
    # EDIT COHORT SCHEDULE
    # ===============================
    st.markdown("## Edit Cohort Schedule")

    if cohorts:

        selected_cohort_name = st.selectbox(
            "Select Cohort to Edit",
            list(cohort_dict.keys()),
            key="edit_cohort"
        )

        selected_cohort_id = cohort_dict[selected_cohort_name]

        cursor.execute("""
            SELECT id, week_number, unlock_date, due_date
            FROM cohort_schedule
            WHERE cohort_id = ?
            ORDER BY week_number
        """, (selected_cohort_id,))

        schedule_rows = cursor.fetchall()

        for row in schedule_rows:
            schedule_id, week_number, unlock_date, due_date = row

            st.markdown(f"### Week {week_number}")

            unlock_value = (
                datetime.fromisoformat(unlock_date).date()
                if unlock_date else None
            )

            due_value = (
                datetime.fromisoformat(due_date).date()
                if due_date else None
            )

            new_unlock = st.date_input(
                f"Unlock Date - Week {week_number}",
                value=unlock_value,
                key=f"unlock_{schedule_id}"
            )

            new_due = st.date_input(
                f"Due Date - Week {week_number}",
                value=due_value,
                key=f"due_{schedule_id}"
            )

            if st.button(f"Save Week {week_number}", key=f"save_{schedule_id}"):

                cursor.execute("""
                    UPDATE cohort_schedule
                    SET unlock_date = ?, due_date = ?
                    WHERE id = ?
                """, (
                    new_unlock.isoformat() if new_unlock else None,
                    new_due.isoformat() if new_due else None,
                    schedule_id
                ))

                conn.commit()
                st.success(f"Week {week_number} updated.")

            st.divider()

    conn.close()