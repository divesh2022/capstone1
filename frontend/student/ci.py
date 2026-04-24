'''Overview
This module defines the student dashboard for correction requests in the Campus ERP system. Built with Streamlit, it provides students with a simple interface to raise correction requests (e.g., attendance, marks, or personal details), track their status, and view approvals or rejections. It acts as the frontend layer that communicates with backend APIs for correction workflows.

Key Components
🔹 Imports
streamlit as st → Provides UI components (forms, tables, tabs).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular correction data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

Raise Correction Request → Students can submit a new correction request.

View My Requests → Displays all correction requests submitted by the student.

Track Status → Shows whether a correction request is pending, approved, or rejected.

Delete Request → Allows students to withdraw a correction request.

Forms  
Each tab contains forms for data entry (student ID, correction type, description, date).

Tables  
Correction records are displayed in tabular format using Pandas DataFrames for easy review.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/corrections/ → Submit and manage correction requests

/students/ → Link corrections to student records

/hod/ → Track approval/rejection by HOD

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves correction records from backend APIs.

post_data(endpoint, payload)  
Submits new correction requests to backend.

update_data(endpoint, payload)  
Updates existing correction requests.

delete_data(endpoint, id)  
Removes correction requests when required.'''
import streamlit as st
import requests
import pandas as pd

URL = "http://127.0.0.1:8000/student"

st.set_page_config(page_title="Class Info Dashboard", layout="centered")
st.title("🏫 Student Class Information")

# Input field for roll number
rollno = st.text_input("Enter Roll Number:")

if st.button("Get Class Info"):
    if not rollno:
        st.error("Please enter a roll number")
    else:
        try:
            response = requests.get(
                f"{URL}/class_info",
                headers={"rollno": rollno}
            )

            if response.status_code == 200:
                data = response.json()
                summary = data.get("class_info", [])

                if not summary:
                    st.warning("No class information found")
                else:
                    # Convert to DataFrame for nice table display
                    df = pd.DataFrame(summary)

                    st.success(f"Class information for Roll No: {data['roll_no']}")
                    st.dataframe(df)
            else:
                st.error(response.json().get("detail", "Error fetching class info"))
        except Exception as e:
            st.error(f"Connection error: {e}")
