'''Overview
This module defines the student profile dashboard in the Campus ERP system. Built with Streamlit, it provides students with a centralized interface to view and update their personal information, academic details, and linked records. It acts as the frontend layer that communicates with backend APIs for profile management.

Key Components
🔹 Imports
streamlit as st → Provides UI components (forms, tables, tabs).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular student data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

View Profile → Displays student details (name, roll number, department, contact info).

Update Profile → Allows students to update personal or academic information.

Linked Records → Shows related records such as attendance, marks, and corrections.

Forms  
Each tab contains forms for data entry (student ID, name, department, contact details).

Tables  
Student records are displayed in tabular format using Pandas DataFrames.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/students/ → Manage student records

/profile/ → Fetch and update student profile details

/attendance/, /marks/, /corrections/ → Link profile with academic records

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves student profile data from backend APIs.

post_data(endpoint, payload)  
Submits updated profile information to backend.

update_data(endpoint, payload)  
Updates existing student records.'''
import streamlit as st
import requests

st.title("🎓 Student Profile")

rollno = st.text_input("Enter Roll Number:")

if st.button("Get Profile"):
    try:
        response = requests.get("http://127.0.0.1:8000/student/profile", headers={"rollno": rollno})
        if response.status_code == 200:
            data = response.json()
            st.write("**Roll No:**", data.get("roll_no"))
            st.write("**Batch:**", data.get("batch"))
            st.write("**Phone Number:**", data.get("phone_number"))
            st.write("**Department:**", data.get("department"))
            st.write("**College:**", data.get("college"))
        else:
            st.error(response.json().get("detail", "Error fetching profile"))
    except Exception as e:
        st.error(f"Connection error: {e}")
