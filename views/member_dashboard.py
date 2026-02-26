import streamlit as st
from database import get_connection
from datetime import datetime, date

def render_member_dashboard():

    st.title("Member Dashboard")

    conn = get_connection()
    cursor = conn.cursor()

    user_id = st.session_state.user["id"]

    # ---------------- GET USER COHORT ----------------
    cursor.execute("""
        SELECT cohort_id FROM users
        WHERE id = ?
    """, (user_id,))

    result = cursor.fetchone()

    if not result or not result[0]:
        st.warning("You have not been assigned to a cohort yet.")
        conn.close()
        return

    cohort_id = result[0]

    # Get cohort name
    cursor.execute("""
        SELECT name FROM cohorts
        WHERE id = ?
    """, (cohort_id,))

    cohort_name = cursor.fetchone()[0]

    st.subheader(f"Cohort: {cohort_name}")

    st.divider()

    # ---------------- GET SCHEDULE ----------------
    cursor.execute("""
        SELECT week_number, unlock_date, due_date
        FROM cohort_schedule
        WHERE cohort_id = ?
        ORDER BY week_number
    """, (cohort_id,))

    schedule = cursor.fetchall()

    today = date.today()

    for week_number, unlock_date, due_date in schedule:

        st.markdown(f"### Week {week_number}")

        if unlock_date:
            unlock_date_obj = datetime.fromisoformat(unlock_date).date()
        else:
            unlock_date_obj = None

        if due_date:
            due_date_obj = datetime.fromisoformat(due_date).date()
        else:
            due_date_obj = None

        # Determine status
        if not unlock_date_obj:
            st.info("🔒 Not yet scheduled.")
        elif today < unlock_date_obj:
            st.warning(f"🔒 Unlocks on {unlock_date_obj}")
        else:
            st.success("🔓 Available")

            if due_date_obj:
                if today > due_date_obj:
                    st.error(f"⚠ Past due (was due {due_date_obj})")
                else:
                    st.info(f"⏳ Due on {due_date_obj}")

        st.divider()

    conn.close()