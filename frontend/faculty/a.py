'''Overview
This module defines the faculty dashboard interface for the Campus ERP system. It provides a Streamlit-based frontend where faculty members can manage academic tasks such as viewing students, recording attendance, uploading assignments, and entering exam marks. It acts as the UI layer that interacts with backend APIs.

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
from datetime import date

BASE_URL = "http://127.0.0.1:8000/faculty/attendance"

st.set_page_config(page_title="Attendance Management", layout="centered")
st.title("📋 Attendance Management")


# ---------------------------
# API Client
# ---------------------------
class AttendanceAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @st.cache_data
    def fetch_classes(_self):
        try:
            r = requests.get(f"{_self.base_url}/classes")
            if r.status_code == 200:
                return r.json().get("data", [])
            return []
        except Exception as e:
            st.error(f"Error fetching classes: {e}")
            return []

    @st.cache_data
    def fetch_subjects(_self):
        try:
            r = requests.get(f"{_self.base_url}/subjects")
            if r.status_code == 200:
                return r.json().get("data", [])
            return []
        except Exception as e:
            st.error(f"Error fetching subjects: {e}")
            return []

    @st.cache_data
    def fetch_faculty(_self):
        try:
            r = requests.get(f"{_self.base_url}/faculty")
            if r.status_code == 200:
                return r.json().get("data", [])
            return []
        except Exception as e:
            st.error(f"Error fetching faculty: {e}")
            return []


# ---------------------------
# UI
# ---------------------------
class AttendanceUI:
    def __init__(self, api_client: AttendanceAPI):
        self.api = api_client

    def run(self):
        classes = self.api.fetch_classes()
        subjects = self.api.fetch_subjects()
        faculty = self.api.fetch_faculty()

        # Defensive key handling for classes
        class_options = {}
        for c in classes:
            # Try different possible keys
            class_id = c.get("class_id") or c.get("class_pk") or c.get("id")
            class_name = c.get("class_name", str(class_id))
            if class_id is not None:
                class_options[f"{class_name} (ID {class_id})"] = class_id

        subject_options = {
            f"{s.get('subject_code')} - {s.get('subject_name','')}": s.get("subject_code")
            for s in subjects if "subject_code" in s
        }

        faculty_options = {
            f.get("name", f.get("faculty_id")): f.get("faculty_id") or f.get("faculty_pk")
            for f in faculty
        }

        with st.form("attendance_form", clear_on_submit=True):
            class_label = st.selectbox("Select Class", options=list(class_options.keys()))
            subject_label = st.selectbox("Select Subject", options=list(subject_options.keys()))
            faculty_label = st.selectbox("Select Faculty", options=list(faculty_options.keys()))
            lecture_date = st.date_input("Lecture Date", value=date.today())

            submitted = st.form_submit_button("Submit Attendance")

            if submitted:
                if not class_label or not subject_label:
                    st.error("Please select both a Class and a Subject.")
                else:
                    payload = {
                        "class_id": class_options[class_label],
                        "subject_code": subject_options[subject_label],
                        "faculty_id": faculty_options[faculty_label],
                        "lecture_date": str(lecture_date)
                    }
                    try:
                        resp = requests.post(f"{BASE_URL}/mark", json=payload)
                        if resp.status_code == 200:
                            st.success(f"✅ Attendance marked successfully for {lecture_date}")
                        else:
                            st.error(f"❌ Error {resp.status_code}: {resp.text}")
                    except Exception as e:
                        st.error(f"⚠️ Connection Error: {e}")

        with st.expander("System Debug Info"):
            st.write("Loaded Classes:", classes)
            st.write("Loaded Subjects:", subjects)
            st.write("Loaded Faculty:", faculty)


# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    api_client = AttendanceAPI(BASE_URL)
    ui = AttendanceUI(api_client)
    ui.run()
