'''Overview
This module defines the student dashboard for assignment marks management in the Campus ERP system. Built with Streamlit, it provides students with a simple interface to view their assignment marks, track performance across subjects, and download reports. It acts as the frontend layer that communicates with backend APIs for assignment marks workflows.

Key Components
🔹 Imports
streamlit as st → Provides UI components (tabs, forms, tables).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular marks data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

View Assignment Marks → Displays marks awarded to students for assignments.

Performance Summary → Provides subject-wise and overall performance analysis.

Download Report → Allows students to export assignment marks.

Forms  
Students can input their roll number or ID to fetch marks data.

Tables & Charts  
Assignment marks are displayed in tabular format using Pandas DataFrames, with optional charts for performance visualization.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/assignment-marks/ → Retrieve assignment marks records

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves assignment marks data from backend APIs.

download_report()  
Exports assignment marks into a downloadable format (CSV/PDF).'''
import streamlit as st
import requests
import pandas as pd

URL = "http://127.0.0.1:8000/student"

st.set_page_config(page_title="MST Marks Dashboard", layout="centered")
st.title("📝 Student MST Marks")

# Input field for roll number
rollno = st.text_input("Enter Roll Number:")

if st.button("Get MST Marks"):
    if not rollno:
        st.error("Please enter a roll number")
    else:
        try:
            response = requests.get(
                f"{URL}/mst_marks",
                headers={"rollno": rollno}
            )

            if response.status_code == 200:
                data = response.json()
                summary = data.get("mst_marks_summary", [])

                if not summary:
                    st.warning("No MST marks found")
                else:
                    # Convert to DataFrame for nice table display
                    df = pd.DataFrame(summary)
                    df["percentage"] = (df["marks_obtained"] / df["total_marks"] * 100).round(2)

                    st.success(f"MST marks for Roll No: {data['roll_no']}")
                    st.dataframe(df)

                    # Optional: show average MST performance
                    avg = df["percentage"].mean()
                    st.write(f"**Average MST Score:** {avg:.2f}%")
                    st.progress(int(avg))
            else:
                st.error(response.json().get("detail", "Error fetching MST marks"))
        except Exception as e:
            st.error(f"Connection error: {e}")
