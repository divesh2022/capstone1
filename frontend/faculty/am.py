import streamlit as st
import requests
import pandas as pd

# --- Configuration ---
API_BASE = "http://127.0.0.1:8000/faculty/assignment_marks"

st.set_page_config(
    page_title="Campus Management | Marks Entry",
    page_icon="🎓",
    layout="wide"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div.stButton > button:first-child {
        background-color: #28a745;
        color: white;
        border-radius: 4px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)


# -------------------------------
# OOP Design
# -------------------------------

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @st.cache_data(ttl=10)
    def fetch_assignments(_self):
        return _self._safe_get(f"{_self.base_url}/assignments-list/")

    @st.cache_data(ttl=10)
    def fetch_students(_self, dept_pk: int):
        return _self._safe_get(f"{_self.base_url}/students/", params={"dept_pk": dept_pk})

    @st.cache_data(ttl=10)
    def fetch_faculty(_self):
        return _self._safe_get(f"{_self.base_url}/faculty/")

    def save_marks(self, records: list):
        try:
            return requests.post(f"{self.base_url}/assignment-marks/bulk", json=records)
        except Exception as e:
            st.error(f"Connection failed: {e}")
            return None

    def _safe_get(self, url, params=None):
        try:
            r = requests.get(url, params=params)
            return r.json() if r.status_code == 200 else []
        except:
            return []

class MarksEntryUI:
    """Handles the Streamlit UI for marks entry."""

    def __init__(self, api_client: APIClient):
        self.api = api_client

    def run(self):
        st.title("📑 Assignment Marks Entry")

        faculty_list = self.api.fetch_faculty()
        assignments = self.api.fetch_assignments()

        if not assignments or not faculty_list:
            st.warning("Ensure both Assignments and Faculty records exist in the database.")
            return

        assign_map = {a["assignment_pk"]: f"{a['subject_name']} (Sem {a['semester']}) | ID: {a['assignment_pk']}" for a in assignments}
        faculty_map = {f["faculty_pk"]: f["name"] for f in faculty_list}

        # Selection Bar
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            selected_assign_pk = st.selectbox("1. Select Assignment", options=list(assign_map.keys()), format_func=lambda x: assign_map[x])
        with col2:
            selected_faculty_pk = st.selectbox("2. Select Faculty (You)", options=list(faculty_map.keys()), format_func=lambda x: faculty_map[x])
        curr_assign = next(a for a in assignments if a["assignment_pk"] == selected_assign_pk)
        with col3:
            st.metric("Max Marks", curr_assign['total_marks'])

        st.divider()

        # Student Roster
        students = self.api.fetch_students(curr_assign['dept_pk'])
        if not students:
            st.error("No students found for this department.")
            return

        st.subheader(f"Mark Entry Grid - {faculty_map[selected_faculty_pk]}")
        df_students = pd.DataFrame(students)
        if "marks" not in df_students.columns:
            df_students["marks"] = 0

        edited_df = st.data_editor(
            df_students[["roll_no", "marks"]],
            width='stretch',
            hide_index=True,
            column_config={
                "roll_no": st.column_config.Column("Roll Number", disabled=True),
                "marks": st.column_config.NumberColumn("Marks", min_value=0, max_value=int(curr_assign['total_marks']), step=1)
            }
        )

        # Save Logic
        if st.button("💾 Finalize & Save All Records"):
            records = [
                {
                    "assignment_pk": selected_assign_pk,
                    "faculty_pk": selected_faculty_pk,
                    "student_pk": students[i]["student_pk"],
                    "marks": row["marks"]
                }
                for i, row in enumerate(edited_df.to_dict(orient="records"))
            ]

            with st.spinner("Pushing marks to database..."):
                res = self.api.save_marks(records)

            if res and res.status_code == 200:
                st.success(f"Records successfully logged under {faculty_map[selected_faculty_pk]}.")
                st.toast("Database Updated", icon="✅")
            elif res:
                st.error(f"Error: {res.text}")


# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == "__main__":
    client = APIClient(API_BASE)
    ui = MarksEntryUI(client)
    ui.run()
