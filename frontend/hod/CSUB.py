'''Overview
This module defines the Head of Department (HOD) dashboard for course–branch management in the Campus ERP system. Built with Streamlit, it provides HODs with tools to manage courses and their associated branches. It acts as the frontend layer that communicates with backend APIs for curriculum and specialization workflows.

Key Components
🔹 Imports
streamlit as st → Provides UI components (tabs, forms, tables).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular course and branch data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

View Courses & Branches → Displays all courses and their branches linked to the department.

Add Branch → Allows HODs to create new branches under a course.

Update Branch → Provides interface to modify existing branch details.

Delete Branch → Enables removal of branches.

Forms  
Each tab contains forms for data entry (course name, branch name, department ID).

Tables  
Course and branch records are displayed in tabular format using Pandas DataFrames.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/courses/ → Manage course records

/branches/ → Manage branch records

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves course or branch data from backend APIs.

post_data(endpoint, payload)  
Submits new branch records to backend.

update_data(endpoint, payload)  
Updates existing branch records.

delete_data(endpoint, id)'''
import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000/hod"  # adjust to your backend server

st.title("Class–Subject Allocation System")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Classes", "Subjects", "Allocations"])

# --- Tab 1: Classes ---
with tab1:
    st.header("Available Classes")
    try:
        classes = requests.get(f"{BASE_URL}/classes").json()
        if isinstance(classes, dict):  # normalize single dict
            classes = [classes]
        for c in classes:
            st.write(f"Class PK: {c.get('class_pk')} | Batch: {c.get('batch')} | Department: {c.get('dept_name')}")
    except Exception as e:
        st.error(f"Error fetching classes: {e}")

# --- Tab 2: Subjects ---
with tab2:
    st.header("Available Subjects")
    try:
        subjects = requests.get(f"{BASE_URL}/subjects/").json()
        if isinstance(subjects, dict):  # normalize single dict
            subjects = [subjects]
        for s in subjects:
            st.write(f"Subject PK: {s.get('subject_pk')} | Code: {s.get('subject_code')} | Name: {s.get('subject_name')}")
    except Exception as e:
        st.error(f"Error fetching subjects: {e}")

# --- Tab 3: Allocations ---
with tab3:
    st.header("Allocate Subject to Class")

    try:
        # Dropdowns for class and subject
        classes = requests.get(f"{BASE_URL}/classes").json()
        if isinstance(classes, dict):
            classes = [classes]
        class_options = {f"{c.get('batch')} - {c.get('dept_name')}": c for c in classes}
        selected_class = st.selectbox("Choose a class", list(class_options.keys()))

        subjects = requests.get(f"{BASE_URL}/subjects").json()
        if isinstance(subjects, dict):
            subjects = [subjects]
        subject_options = {f"{s.get('subject_code')} - {s.get('subject_name')}": s for s in subjects}
        selected_subject = st.selectbox("Choose a subject", list(subject_options.keys()))

        semester = st.number_input("Semester", min_value=1, max_value=8, step=1)

        if st.button("Allocate"):
            class_info = class_options[selected_class]
            subject_info = subject_options[selected_subject]

            payload = {
                "batch": class_info.get("batch"),
                "dept_name": class_info.get("dept_name"),
                "subject_code": subject_info.get("subject_code"),
                "semester": semester,
            }
            response = requests.post(f"{BASE_URL}/class-subjects/allocate", json=payload)
            st.success(response.json().get("status", "Allocation complete"))

    except Exception as e:
        st.error(f"Error during allocation: {e}")

    st.subheader("Current Allocations")
    try:
        allocations = requests.get(f"{BASE_URL}/class-subjects").json()
        if isinstance(allocations, dict):
            allocations = [allocations]
        for alloc in allocations:
            st.markdown(f"**{alloc.get('batch')} - {alloc.get('dept_name')}**")
            for subj in alloc.get("subjects", []):
                st.write(f"Semester {subj.get('semester')}: {subj.get('subject_code')} - {subj.get('subject_name')}")
    except Exception as e:
        st.error(f"Error fetching allocations: {e}")
