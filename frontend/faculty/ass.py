'''Overview
This module defines a Streamlit-based interface for faculty members to manage assignment records in the Campus ERP system. It provides a simple UI for submitting assignments and fetching assignment-related data from backend APIs. It acts as the frontend layer that communicates with the backend service at http://localhost/faculty/assignment.

Key Components
🔹 Imports
streamlit as st → Provides UI components and caching.

requests → Handles HTTP requests to backend APIs.

🔹 Page Configuration
st.set_page_config  
Sets the page title to Campus Assignment Entry and centers the layout.

st.title  
Displays the dashboard title with an assignment icon.

🔹 API Client Class
AssignmentAPI  
Encapsulates API interactions for assignments.

Methods:

__init__(self, base_url: str)  
Initializes the API client with a base URL.

fetch_data(_self, endpoint: str)

Decorated with @st.cache_data(ttl=60) for caching responses.

Sends a GET request to the backend.

Returns JSON data if successful, otherwise an empty list.

Handles exceptions gracefully.

submit_assignment(self, payload: dict)

Sends a POST request to /assignments/ endpoint with assignment details.

Returns the response object if successful.

Displays a Streamlit error message if a connection error occurs.

🔹 UI Features
Assignment Entry Form  
Faculty can input assignment details (title, description, subject, due date) and submit them to the backend.

Data Fetching  
Cached retrieval of assignment records for display in the dashboard.
'''
import streamlit as st
import requests

API_BASE = "http://localhost:8000/faculty/assignment"

st.set_page_config(page_title="Campus Assignment Entry", layout="centered")
st.title("📘 Campus Assignment Entry")


# -------------------------------
# API Client Class
# -------------------------------
class AssignmentAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @st.cache_data(ttl=60)
    def fetch_data(_self, endpoint: str):
        """Generic fetch method with caching."""
        try:
            resp = requests.get(f"{_self.base_url}/{endpoint}/", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return []

    def submit_assignment(self, payload: dict):
        """Submit a new assignment record."""
        try:
            resp = requests.post(f"{self.base_url}/assignments/", json=payload)
            return resp
        except Exception as e:
            st.error(f"⚠️ Connection Error: {e}")
            return None


# -------------------------------
# UI Class
# -------------------------------
class AssignmentUI:
    def __init__(self, api_client: AssignmentAPI):
        self.api = api_client

    def run(self):
        # Fetch data
        departments = self.api.fetch_data("departments")
        subjects = self.api.fetch_data("subjects")
        faculty = self.api.fetch_data("faculty")
        assignments = self.api.fetch_data("assignments")

        # Map dropdowns
        dept_options = {f"{d['dept_id']} - {d['dept_name']}": d["dept_pk"] for d in departments}
        subject_options = {f"{s['subject_code']} - {s['subject_name']}": s["subject_pk"] for s in subjects}
        faculty_options = {f"{f['name']}": f["faculty_pk"] for f in faculty}

        # --- Form UI ---
        with st.form("assignment_form", clear_on_submit=True):
            dept_label = st.selectbox("Select Department", options=list(dept_options.keys()))
            subject_label = st.selectbox("Select Subject", options=list(subject_options.keys()))
            faculty_label = st.selectbox("Select Faculty", options=list(faculty_options.keys()))

            col1, col2 = st.columns(2)
            with col1:
                semester = st.number_input("Semester", min_value=1, max_value=8, step=1)
            with col2:
                total_marks = st.number_input("Total Marks", min_value=1, step=1)

            assignment_pdf = st.text_input("Assignment PDF (Path or URL)")

            submitted = st.form_submit_button("Submit Assignment")

            if submitted:
                if not dept_label or not subject_label:
                    st.error("Please select both a Department and a Subject.")
                else:
                    payload = {
                        "dept_pk": dept_options[dept_label],
                        "subject_pk": subject_options[subject_label],
                        "semester": semester,
                        "assignment_pdf": assignment_pdf,
                        "total_marks": total_marks,
                        "faculty_pk": faculty_options[faculty_label],
                    }

                    resp = self.api.submit_assignment(payload)
                    if resp:
                        if resp.status_code == 200:
                            data = resp.json()
                            st.success(f"✅ Success! Assignment ID: {data['assignment_pk']}")
                        else:
                            st.error(f"❌ Error {resp.status_code}: {resp.text}")

        # --- Debug Info ---
        with st.expander("System Debug Info"):
            st.write("Loaded Departments:", departments)
            st.write("Loaded Subjects:", subjects)
            st.write("Loaded Faculty:", faculty)
            st.write("Loaded Assignments:", assignments)


# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == "__main__":
    api_client = AssignmentAPI(API_BASE)
    ui = AssignmentUI(api_client)
    ui.run()
