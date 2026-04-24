'''Overview
This module defines a Streamlit-based faculty dashboard for the Campus ERP system. It provides an interactive interface for faculty members to manage academic workflows such as viewing students, recording attendance, uploading assignments, and entering MST exam marks. It acts as the frontend layer that communicates with backend APIs.

Key Components
🔹 Imports
streamlit as st → Provides UI components (tabs, forms, tables).

requests → Handles API calls to backend endpoints.

pandas → Used for tabular data display and manipulation.

json → For parsing API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

View Students → Displays student records fetched from backend.

Attendance → Allows faculty to mark and view attendance.

Assignments → Enables assignment creation and marks entry.

MST Exams → Provides exam scheduling and marks entry interface.

Forms  
Each tab contains forms for data entry (e.g., roll number, subject, marks).

Tables  
Student lists, attendance records, and marks are displayed in tabular format using Pandas DataFrames.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/students/ → Fetch student records

/attendance/ → Record and view attendance

/assignment/ → Create assignments

/mst-exams/ → Manage MST exams

/mst-exam-marks/ → Record MST exam marks

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Generic function to retrieve data from backend APIs.

post_data(endpoint, payload)  
Sends new records (attendance, assignments, marks) to backend.

update_data(endpoint, payload)  
Updates existing records.

delete_data(endpoint, id)  
Removes records when required.'''
import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8000/faculty/attendance_aggregate"

st.set_page_config(page_title="Attendance Aggregate Manager", layout="wide")
st.title("📊 Attendance Aggregate Manager")

# ---------------------------
# API Client Class
# ---------------------------
class AttendanceAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @st.cache_data
    def fetch_options(_self, endpoint: str):
        try:
            response = requests.get(f"{_self.base_url}/{endpoint}")
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                st.error(f"Error fetching {endpoint}: {response.text}")
                return []
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")
            return []

    def fetch_records(self, subject_code, semester, dept_id):
        params = {"subject_code": subject_code, "semester": semester, "dept_id": dept_id}
        response = requests.get(f"{self.base_url}/records", params=params)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            st.error(f"Error fetching records: {response.text}")
            return []

    def set_total_lectures(self, payload: dict):
        return requests.post(f"{self.base_url}/set_total_lectures", json=payload)

    def update_attendance(self, records: list):
        return requests.post(f"{self.base_url}/update_attendance", json=records)

# ---------------------------
# UI Class
# ---------------------------
class AttendanceUI:
    def __init__(self, api_client: AttendanceAPI):
        self.api = api_client

    def run(self):
        # Fetch dropdown data
        departments = self.api.fetch_options("departments")
        subjects = self.api.fetch_options("subjects")
        semesters = self.api.fetch_options("semesters")

        # Tabs
        tab1, tab2 = st.tabs(["📊 View & Update Attendance", "⚙️ Set Total Lectures"])

        # ---------------------------
        # Tab 1: View & Update Attendance
        # ---------------------------
        with tab1:
            st.header("View & Update Attendance Records")

            dept_ids = [d["dept_id"] for d in departments]
            dept_names = {d["dept_id"]: d.get("dept_name", d["dept_id"]) for d in departments}
            selected_dept = st.selectbox("Department", dept_ids, format_func=lambda x: dept_names[x])

            subject_codes = [s["subject_code"] for s in subjects]
            subject_names = {s["subject_code"]: s.get("subject_name", s["subject_code"]) for s in subjects}
            selected_subject = st.selectbox("Subject", subject_codes, format_func=lambda x: subject_names[x])

            selected_semester = st.selectbox("Semester", semesters)

            if selected_dept and selected_subject and selected_semester:
                records = self.api.fetch_records(selected_subject, selected_semester, selected_dept)

                if records:
                    st.subheader("Attendance Records")
                    df = pd.DataFrame(records)

                    # Editable table
                    edited_df = st.data_editor(df, num_rows="fixed")

                    if st.button("Save Changes"):
                        updated_records = edited_df[["roll_no", "lectures_attended"]].to_dict(orient="records")
                        resp = self.api.update_attendance(updated_records)
                        if resp.status_code == 200:
                            st.success(resp.json().get("message"))
                        else:
                            st.error(resp.text)
                else:
                    st.warning("No records found for the selected filters.")

        # ---------------------------
        # Tab 2: Set Total Lectures
        # ---------------------------
        with tab2:
            st.header("Set Total Lectures Delivered")

            dept_ids = [d["dept_id"] for d in departments]
            dept_names = {d["dept_id"]: d.get("dept_name", d["dept_id"]) for d in departments}
            selected_dept = st.selectbox("Department (for total lectures)", dept_ids, format_func=lambda x: dept_names[x])

            subject_codes = [s["subject_code"] for s in subjects]
            subject_names = {s["subject_code"]: s.get("subject_name", s["subject_code"]) for s in subjects}
            selected_subject = st.selectbox("Subject (for total lectures)", subject_codes, format_func=lambda x: subject_names[x])

            selected_semester = st.selectbox("Semester (for total lectures)", semesters)
            total_lectures = st.number_input("Total Lectures Delivered", min_value=1, step=1)

            if st.button("Set Total Lectures"):
                payload = {
                    "subject_code": selected_subject,
                    "semester": selected_semester,
                    "dept_id": selected_dept,
                    "total_lectures": total_lectures
                }
                resp = self.api.set_total_lectures(payload)
                if resp.status_code == 200:
                    st.success(resp.json().get("message"))
                else:
                    st.error(resp.text)

# ---------------------------
# Main Entry Point
# ---------------------------
if __name__ == "__main__":
    api_client = AttendanceAPI(API_BASE)
    ui = AttendanceUI(api_client)
    ui.run()
