'''Overview
This module defines the faculty interface for MST (Mid-Semester Test) exam management in the Campus ERP system. Built with Streamlit, it allows faculty members to schedule MST exams, record marks, and view exam-related data. It acts as the frontend layer that communicates with backend APIs for exam workflows.

Key Components
🔹 Imports
streamlit as st → Provides UI components (tabs, forms, tables).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular exam and marks data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs:

Schedule MST Exam → Faculty can create new MST exam records.

Enter Marks → Allows entry of student marks for MST exams.

View Exams → Displays scheduled MST exams with subject and faculty details.

View Marks → Shows marks awarded to students in MST exams.

Forms  
Each tab contains forms for data entry (exam type, subject, date, student roll number, marks).

Tables  
Exam schedules and marks are displayed in tabular format using Pandas DataFrames.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/mst-exams/ → Create and view MST exam records

/mst-exam-marks/ → Record and view MST exam marks

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves exam or marks data from backend APIs.

post_data(endpoint, payload)  
Submits new exam schedules or marks to backend.

update_data(endpoint, payload)  
Updates existing exam or marks records.

delete_data(endpoint, id)  
Removes exam or marks records when required.'''
import streamlit as st
import requests
import datetime

API_BASE = "http://127.0.0.1:8000/faculty/mst_exam"

st.set_page_config(page_title="MST Exam Creator", page_icon="📝", layout="centered")
st.title("📝 Create MST Exam Record")
st.markdown("Use this form to register a new **MST-1** or **MST-2** in the system.")


# ---------------------------
# API Client Class
# ---------------------------
class MSTExamAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @st.cache_data(ttl=60)
    def fetch_data(_self, endpoint: str):
        try:
            r = requests.get(f"{_self.base_url}/{endpoint}")
            if r.status_code == 200:
                return r.json().get("data", [])
            return []
        except Exception as e:
            st.error(f"Error connecting to {endpoint}: {e}")
            return []

    def create_exam(self, payload: dict):
        try:
            return requests.post(f"{self.base_url}/", json=payload)
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
            return None


# ---------------------------
# UI Class
# ---------------------------
class MSTExamUI:
    def __init__(self, api_client: MSTExamAPI):
        self.api = api_client

    def run(self):
        with st.spinner("Loading configuration..."):
            departments = self.api.fetch_data("departments")
            subjects = self.api.fetch_data("subjects")
            faculties = self.api.fetch_data("faculty")

        if not departments or not subjects or not faculties:
            st.error("Missing required data (Departments/Subjects/Faculty). Ensure FastAPI is running and database is populated.")
            return

        dept_map = {d["dept_pk"]: f"{d['dept_id']} - {d['dept_name']}" for d in departments}
        sub_map = {s["subject_pk"]: f"{s['subject_code']} - {s['subject_name']}" for s in subjects}
        fac_map = {f["faculty_pk"]: f["name"] for f in faculties}

        with st.form("mst_exam_form", clear_on_submit=True):
            st.subheader("General Details")

            col1, col2 = st.columns(2)
            with col1:
                exam_name = st.selectbox("Exam Type", options=["MST-1", "MST-2"])
                selected_dept_pk = st.selectbox("Department", options=list(dept_map.keys()), format_func=lambda x: dept_map[x])
                semester = st.number_input("Semester", min_value=1, max_value=8, value=6)

            with col2:
                selected_subject_pk = st.selectbox("Subject", options=list(sub_map.keys()), format_func=lambda x: sub_map[x])
                exam_date = st.date_input("Exam Date", min_value=datetime.date.today())
                total_marks = st.number_input("Total Marks", min_value=1, max_value=100, value=50)

            st.divider()
            st.subheader("Authority & Files")

            col3, col4 = st.columns(2)
            with col3:
                selected_faculty_pk = st.selectbox("Faculty in Charge", options=list(fac_map.keys()), format_func=lambda x: fac_map[x])
            with col4:
                pdf_path = st.text_input("Exam PDF Filename/Link", value="mst_paper.pdf", help="Enter the storage path or filename for the exam paper.")

            submitted = st.form_submit_button("🚀 Create MST Exam")

            if submitted:
                payload = {
                    "dept_pk": selected_dept_pk,
                    "subject_pk": selected_subject_pk,
                    "semester": int(semester),
                    "exam_date": str(exam_date),
                    "exam_pdf": pdf_path,
                    "total_marks": int(total_marks),
                    "exam_name": exam_name,
                    "faculty_pk": selected_faculty_pk
                }

                resp = self.api.create_exam(payload)
                if resp:
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"Successfully registered {exam_name} for {sub_map[selected_subject_pk]}!")
                        st.balloons()
                    else:
                        st.error(f"Server Error: {resp.json().get('detail', 'Unknown error')}")


# ---------------------------
# Sidebar Utilities
# ---------------------------
def sidebar_utilities():
    with st.sidebar:
        st.header("Settings")
        if st.button("🔄 Refresh Dropdowns"):
            st.cache_data.clear()
            st.rerun()
        st.info("""
        **Developer Note:** Ensure the `exam_date` is sent as a string (YYYY-MM-DD) to match the FastAPI validation.
        """)


# ---------------------------
# Main Entry Point
# ---------------------------
if __name__ == "__main__":
    api_client = MSTExamAPI(API_BASE)
    ui = MSTExamUI(api_client)
    ui.run()
    sidebar_utilities()
