'''Overview
This module defines the Head of Department (HOD) dashboard for correction management in the Campus ERP system. Built with Streamlit, it provides HODs with tools to review, approve, and manage correction requests submitted by faculty for student records. It acts as the frontend layer that communicates with backend APIs for correction workflows.

Key Components
🔹 Imports
streamlit as st → Provides UI components (tabs, forms, tables).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular correction data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

View Corrections → Displays all correction requests submitted by faculty.

Approve Correction → Allows HODs to approve or reject correction requests.

Update Correction → Provides interface to modify correction details.

Delete Correction → Enables removal of correction records.

Forms  
Each tab contains forms for data entry (student ID, faculty ID, description, date).

Tables  
Correction records are displayed in tabular format using Pandas DataFrames for easy review.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/corrections/ → Manage correction records

/faculty/ → Link corrections to faculty members

/students/ → Link corrections to student records

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves correction data from backend APIs.

post_data(endpoint, payload)  
Submits new correction requests to backend.

update_data(endpoint, payload)  
Updates existing correction records.

delete_data(endpoint, id)  
Removes correction records when required.'''
import streamlit as st
import requests

BASE_URL = "http://localhost:8000/hod/Ci"  # adjust if your FastAPI runs elsewhere

st.title("Class Incharge Management")

tab1, tab2, tab3 = st.tabs(["View Allocations", "Allocate Incharge", "Browse Faculties & Classes"])

with tab1:
    st.header("Class Incharge Allocations")
    resp = requests.get(f"{BASE_URL}/class-incharge/")
    if resp.ok:
        data = resp.json()
        st.table(data)

with tab2:
    st.header("Allocate Class Incharge")
    # Fetch dropdown data
    faculties = requests.get(f"{BASE_URL}/faculties/").json()
    classes = requests.get(f"{BASE_URL}/classes/").json()

    batch = st.selectbox("Select Batch", sorted({c["batch"] for c in classes}))
    dept_name = st.selectbox("Select Department", sorted({c["dept_name"] for c in classes}))
    faculty_email = st.selectbox("Select Faculty", [f["email"] for f in faculties])
    semester = st.number_input("Semester", min_value=1, max_value=8, step=1)

    if st.button("Allocate"):
        payload = {
            "batch": batch,
            "dept_name": dept_name,
            "faculty_email": faculty_email,
            "semester": semester
        }
        resp = requests.post(f"{BASE_URL}/class-incharge/", params=payload)
        if resp.ok:
            st.success(resp.json()["status"])
        else:
            st.error("Failed to allocate")

with tab3:
    st.header("Faculties")
    st.table(requests.get(f"{BASE_URL}/faculties/").json())

    st.header("Classes")
    st.table(requests.get(f"{BASE_URL}/classes/").json())
