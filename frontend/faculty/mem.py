'''Overview
This module defines the faculty interface for managing exam marks in the Campus ERP system. Built with Streamlit, it provides a user-friendly dashboard for faculty members to record, update, and view marks for MST (Mid-Semester Tests) and assignments. It acts as the frontend layer that communicates with backend APIs for marks management.

Key Components
🔹 Imports
streamlit as st → Provides UI components (forms, tables, tabs).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular marks data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

Enter MST Marks → Faculty can input marks for MST exams.

Enter Assignment Marks → Faculty can record assignment marks.

View MST Marks → Displays MST marks linked to students and subjects.

View Assignment Marks → Shows assignment marks with student details.

Forms  
Each tab contains forms for data entry (student roll number, subject, marks, faculty ID).

Tables  
Marks records are displayed in tabular format using Pandas DataFrames for easy review.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/mst-exam-marks/ → Record and view MST exam marks

/assignment-marks/ → Record and view assignment marks

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves marks data from backend APIs.

post_data(endpoint, payload)  
Submits new marks records to backend.

update_data(endpoint, payload)  
Updates existing marks records.

delete_data(endpoint, id)  
Removes marks records when required.'''
import streamlit as st
import requests
import pandas as pd

API_BASE = "http://127.0.0.1:8000/faculty/mst_exam_marks"

st.set_page_config(page_title="MST Exam Marks", layout="wide")
st.title("📊 MST Exam Marks Entry")


# ---------------------------
# API Client
# ---------------------------
class MSTExamAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @st.cache_data(ttl=60)
    def fetch_exams(_self):
        try:
            r = requests.get(f"{_self.base_url}/exams")
            return r.json().get("data", []) if r.status_code == 200 else []
        except Exception:
            return []

    @st.cache_data(ttl=60)
    def fetch_students(_self, dept_pk, batch):
        try:
            r = requests.get(f"{_self.base_url}/students", params={"dept_pk": dept_pk, "batch": batch})
            return r.json().get("data", []) if r.status_code == 200 else []
        except Exception:
            return []

    @st.cache_data(ttl=60)
    def fetch_marks(_self, exam_pk):
        try:
            r = requests.get(f"{_self.base_url}/marks", params={"exam_pk": exam_pk})
            return r.json().get("data", []) if r.status_code == 200 else []
        except Exception:
            return []

    @st.cache_data(ttl=60)
    def fetch_faculty(_self):
        try:
            r = requests.get(f"{_self.base_url}/faculty/")
            return r.json() if r.status_code == 200 else []
        except Exception:
            return []

    def save_marks(self, records: list):
        try:
            return requests.post(f"{self.base_url}/bulk_insert", json=records)
        except Exception as e:
            st.error(f"Error saving marks: {e}")
            return None


# ---------------------------
# UI Class
# ---------------------------
class MSTExamUI:
    def __init__(self, api_client: MSTExamAPI):
        self.api = api_client

    def semester_to_batch(self, semester: int) -> str:
        # Adjust mapping logic if needed
        return "2025"

    def run(self):
        exams = self.api.fetch_exams()
        faculty_list = self.api.fetch_faculty()

        if not exams or not faculty_list:
            st.warning("Please ensure Exams and Faculty records exist in the database.")
            return

        # Selection
        col_a, col_b = st.columns(2)
        with col_a:
            exam_map = {e["exam_pk"]: f"{e['exam_name']} - {e['subject_code']} ({e['dept_name']})" for e in exams}
            selected_exam_pk = st.selectbox("Select Exam", options=list(exam_map.keys()), format_func=lambda x: exam_map[x])
        with col_b:
            faculty_map = {f["faculty_pk"]: f["name"] for f in faculty_list}
            selected_faculty_pk = st.selectbox("Select Faculty (Entry By)", options=list(faculty_map.keys()), format_func=lambda x: faculty_map[x])

        selected_exam = next((e for e in exams if e["exam_pk"] == selected_exam_pk), None)
        if not selected_exam:
            return

        dept_pk = selected_exam.get("dept_pk")
        semester = selected_exam.get("semester")
        batch = self.semester_to_batch(semester)

        st.info(f"**Exam:** {selected_exam['exam_name']} | **Max Marks:** {selected_exam['total_marks']}")

        tab1, tab2 = st.tabs(["📝 Enter Marks", "📋 View Existing"])

        with tab2:
            marks_data = self.api.fetch_marks(selected_exam_pk)
            if marks_data:
                df_marks = pd.DataFrame(marks_data)
                st.dataframe(df_marks[["roll_no", "marks", "faculty_name"]], width='stretch')
            else:
                st.info("No marks recorded yet.")

        with tab1:
            students = self.api.fetch_students(dept_pk, batch)
            if not students:
                st.warning(f"No students found for Dept {dept_pk}, Batch {batch}.")
                return

            df = pd.DataFrame(students)
            if "marks" not in df.columns:
                df["marks"] = 0

            edited_df = st.data_editor(
                df[["roll_no", "marks"]],
                num_rows="fixed",
                width='stretch',
                hide_index=True,
                column_config={
                    "marks": st.column_config.NumberColumn(max_value=int(selected_exam['total_marks']))
                }
            )

            if st.button("🚀 Save All MST Marks"):
                records = [
                    {
                        "exam_pk": selected_exam_pk,
                        "student_pk": students[i]["student_pk"],
                        "marks": row["marks"],
                        "faculty_pk": selected_faculty_pk
                    }
                    for i, row in enumerate(edited_df.to_dict(orient="records"))
                ]
                with st.spinner("Saving..."):
                    resp = self.api.save_marks(records)
                if resp and resp.status_code == 200:
                    st.success(f"Successfully saved records under {faculty_map[selected_faculty_pk]}!")
                    st.balloons()
                elif resp:
                    st.error(f"Error {resp.status_code}: {resp.text}")


# ---------------------------
# Main Entry Point
# ---------------------------
if __name__ == "__main__":
    api_client = MSTExamAPI(API_BASE)
    ui = MSTExamUI(api_client)
    ui.run()
