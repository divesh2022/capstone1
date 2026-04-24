'''Overview
This module defines the Head of Department (HOD) dashboard for faculty–student management in the Campus ERP system. Built with Streamlit, it provides HODs with tools to oversee student records, link them with faculty, and manage departmental academic workflows. It acts as the frontend layer that communicates with backend APIs for student–faculty operations.

Key Components
🔹 Imports
streamlit as st → Provides UI components (tabs, forms, tables).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular student and faculty data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

View Students → Displays student records linked to the department.

Assign Faculty to Students → Allows HODs to assign faculty members to specific students or subjects.

Update Student Records → Provides interface to modify student details.

Delete Student Records → Enables removal of student records when necessary.

Forms  
Each tab contains forms for data entry (student ID, faculty ID, subject ID, department ID).

Tables  
Student and faculty records are displayed in tabular format using Pandas DataFrames.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/students/ → Manage student records

/faculty/ → Manage faculty records

/hod/ → Link faculty and students under HOD supervision

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves student or faculty data from backend APIs.

post_data(endpoint, payload)  
Submits new student–faculty assignments to backend.

update_data(endpoint, payload)  
Updates existing student records.

delete_data(endpoint, id)  
Removes student records when required.'''
import streamlit as st
import requests
import pandas as pd
import io

# Configuration - Ensure your FastAPI server is running here
API_BASE_URL = "http://127.0.0.1:8000/hod"

st.set_page_config(page_title="Faculty Management System", layout="wide")

st.title("🏫 Academic Management Portal")
st.markdown("---")

# Create the Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👥 Faculty Directory", 
    "✍️ Single Allocation", 
    "📤 Bulk CSV Import", 
    "🗑️ Manage Allocations",
    "subjects"
])

# --- Tab 1: Faculty Directory ---
with tab1:
    st.header("Faculty List")
    if st.button("Fetch Latest Faculty Data"):
        try:
            response = requests.get(f"{API_BASE_URL}/faculties/")
            if response.status_code == 200:
                df = pd.DataFrame(response.json())
                st.dataframe(df, width = 'stretch', hide_index=True)
            else:
                st.error("Backend returned an error.")
        except Exception as e:
            st.error(f"Could not connect to FastAPI: {e}")

# --- Tab 2: Single Allocation ---
with tab2:
    st.header("New Subject Allocation")
    with st.form("single_entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Faculty Email", placeholder="teacher@university.edu")
            sub_code = st.text_input("Subject Code", placeholder="CS101")
        with col2:
            semester = st.number_input("Semester", min_value=1, max_value=10, value=1)
        
        submitted = st.form_submit_button("Assign Subject", width = 'stretch')
        
        if submitted:
            payload = {"email": email, "subject_code": sub_code, "semester": semester}
            res = requests.post(f"{API_BASE_URL}/faculty-subjects/allocate", json=payload)
            if res.status_code == 200:
                st.success(f"Successfully assigned {sub_code} to {email}")
            else:
                st.error(f"Error: {res.json().get('detail')}")

# --- Tab 3: Bulk CSV Import ---
with tab3:
    st.header("CSV Batch Upload")
    st.write("Upload a CSV file with headers: `email`, `subject_code`, `semester`")
    
    uploaded_file = st.file_uploader("Choose CSV file", type="csv")
    
    if uploaded_file:
        df_preview = pd.read_csv(uploaded_file)
        st.subheader("Data Preview")
        st.table(df_preview.head(5))
        
        if st.button("Execute Bulk Import"):
            uploaded_file.seek(0)
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            res = requests.post(f"{API_BASE_URL}/faculty-subjects/upload-csv", files=files)
            
            if res.status_code == 200:
                st.success("Batch processing complete!")
            else:
                st.error(f"Upload failed: {res.json().get('detail')}")

# --- Tab 4: Manage/Delete Allocations ---
with tab4:
    st.header("Remove Allocation")
    st.info("Enter the exact details to remove a faculty member from a subject.")
    
    with st.expander("Delete Form"):
        d_email = st.text_input("Registered Email")
        d_sub = st.text_input("Subject Code")
        d_sem = st.number_input("Semester", min_value=1, key="del_sem")
        
        if st.button("Permanent Delete", type="primary"):
            params = {"email": d_email, "subject_code": d_sub, "semester": d_sem}
            res = requests.delete(f"{API_BASE_URL}/faculty-subjects/delete", params=params)
            if res.status_code == 200:
                st.toast("Record deleted successfully!")
            else:
                st.error("Could not find or delete record.")
with tab5:
    st.header("Subject List")
    if st.button("Fetch Subjects"):
        try:
            response = requests.get(f"{API_BASE_URL}/FS/subjects/")
            if response.status_code == 200:
                df = pd.DataFrame(response.json())
                st.dataframe(df, width = 'stretch', hide_index=True)
            else:
                st.error("Backend returned an error.")
        except Exception as e:
            st.error(f"Could not connect to FastAPI: {e}")
