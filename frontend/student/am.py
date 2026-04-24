'''Overview
This module defines the student dashboard for MST (Mid-Semester Test) exam management in the Campus ERP system. Built with Streamlit, it provides students with a simple interface to view MST exam schedules, check marks, and track academic performance. It acts as the frontend layer that communicates with backend APIs for MST exam workflows.

Key Components
🔹 Imports
streamlit as st → Provides UI components (tabs, forms, tables).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular exam and marks data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

View MST Exams → Displays scheduled MST exams with subject and faculty details.

View MST Marks → Shows marks awarded to students in MST exams.

Performance Summary → Provides subject-wise and overall performance analysis.

Forms  
Students can input their roll number or ID to fetch exam and marks data.

Tables & Charts  
Exam schedules and marks are displayed in tabular format using Pandas DataFrames, with optional charts for performance visualization.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/mst-exams/ → Fetch MST exam schedules

/mst-exam-marks/ → Retrieve MST exam marks

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves exam or marks data from backend APIs.

download_report()  
Exports MST exam marks into a downloadable format (CSV/PDF).'''
import streamlit as st
import requests
import pandas as pd

URL = "http://127.0.0.1:8000/student"

st.set_page_config(page_title="Assignment Marks Dashboard", layout="centered")
st.title("📝 Student Assignment Marks")

# Input field for roll number
rollno = st.text_input("Enter Roll Number:")

if st.button("Get Assignment Marks"):
    if not rollno:
        st.error("Please enter a roll number")
    else:
        try:
            response = requests.get(
                f"{URL}/assignment_marks",
                headers={"rollno": rollno}
            )

            if response.status_code == 200:
                data = response.json()
                summary = data.get("assignment_marks_summary", [])

                if not summary:
                    st.warning("No assignment marks found")
                else:
                    # Convert to DataFrame for nice table display
                    df = pd.DataFrame(summary)
                    df["percentage"] = (df["marks_obtained"] / df["total_marks"] * 100).round(2)

                    st.success(f"Assignment marks for Roll No: {data['roll_no']}")
                    st.dataframe(df)

                    # Optional: show average assignment performance
                    avg = df["percentage"].mean()
                    st.write(f"**Average Assignment Score:** {avg:.2f}%")
                    st.progress(int(avg))
            else:
                st.error(response.json().get("detail", "Error fetching assignment marks"))
        except Exception as e:
            st.error(f"Connection error: {e}")
