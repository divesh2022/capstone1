'''Overview
This module defines the student dashboard for attendance management in the Campus ERP system. Built with Streamlit, it provides students with a simple interface to view their attendance records, track subject-wise percentages, and ensure compliance with academic requirements. It acts as the frontend layer that communicates with backend APIs for attendance workflows.

Key Components
🔹 Imports
streamlit as st → Provides UI components (forms, tables, charts).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular attendance data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

View Attendance → Displays attendance records for each subject.

Attendance Summary → Shows overall attendance percentage and subject-wise breakdown.

Download Report → Allows students to export attendance records.

Forms  
Students can input their roll number or ID to fetch attendance data.

Tables & Charts  
Attendance records are displayed in tabular format using Pandas DataFrames, with optional charts for visualization.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/attendance/ → Fetch subject-wise attendance records

/attendance-summary/ → Retrieve overall attendance percentage

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves attendance data from backend APIs.

post_data(endpoint, payload)  
Submits attendance queries or requests.

download_report()  
Exports attendance records into a downloadable format (CSV/PDF).'''
import streamlit as st
import requests
import pandas as pd

URL = "http://127.0.0.1:8000/student"

st.set_page_config(page_title="Attendance Dashboard", layout="centered")
st.title("📊 Student Attendance Aggregate")

# Input field for roll number
rollno = st.text_input("Enter Roll Number:")

if st.button("Get Attendance Summary"):
    if not rollno:
        st.error("Please enter a roll number")
    else:
        try:
            response = requests.get(
                f"{URL}/attendance_aggregate",
                headers={"rollno": rollno}
            )

            if response.status_code == 200:
                data = response.json()
                summary = data.get("attendance_summary", [])

                if not summary:
                    st.warning("No attendance records found")
                else:
                    # Convert to DataFrame for nice table display
                    df = pd.DataFrame(summary)
                    df["percentage"] = (df["lectures_attended"] / df["total_lectures"] * 100).round(2)

                    st.success(f"Attendance records for Roll No: {data['roll_no']}")
                    st.dataframe(df)

                    # Optional: show average attendance
                    avg = df["percentage"].mean()
                    st.write(f"**Average Attendance:** {avg:.2f}%")
                    st.progress(int(avg))
            else:
                st.error(response.json().get("detail", "Error fetching attendance"))
        except Exception as e:
            st.error(f"Connection error: {e}")
