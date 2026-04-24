'''Overview
This module defines the student dashboard for timetable management in the Campus ERP system. Built with Streamlit, it provides students with a simple interface to view their class schedules, subject allocations, and faculty assignments. It acts as the frontend layer that communicates with backend APIs for timetable workflows.

Key Components
🔹 Imports
streamlit as st → Provides UI components (tabs, tables, forms).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular timetable data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

View Timetable → Displays the student’s timetable for all subjects.

Daily Schedule → Shows timetable filtered by day.

Faculty Allocation → Displays which faculty is assigned to each subject slot.

Forms  
Students can input their roll number or course ID to fetch timetable data.

Tables  
Timetable records are displayed in tabular format using Pandas DataFrames for easy review.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/timetable/ → Fetch timetable records

/courses/ → Link timetable to courses

/subjects/ → Link timetable to subjects

/faculty/ → Link timetable slots to faculty

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves timetable data from backend APIs.

filter_by_day(day)  
Filters timetable records for a specific day.

download_report()'''
import streamlit as st
import requests
import pandas as pd

URL = "http://127.0.0.1:8000/student"

st.set_page_config(page_title="Total Internal Marks Dashboard", layout="centered")
st.title("📊 Student Total Internal Marks")

# Input field for roll number
rollno = st.text_input("Enter Roll Number:")

if st.button("Get Internal Marks"):
    if not rollno:
        st.error("Please enter a roll number")
    else:
        try:
            response = requests.get(
                f"{URL}/total_internal_marks",
                headers={"rollno": rollno}
            )

            if response.status_code == 200:
                data = response.json()
                summary = data.get("total_internal_marks", [])

                if not summary:
                    st.warning("No internal marks found")
                else:
                    # Convert to DataFrame
                    df = pd.DataFrame(summary)

                    # Add percentage columns if needed
                    df["MST1 %"] = (df["mst1_marks"] / df["total_internal_marks"] * 100).round(2)
                    df["MST2 %"] = (df["mst2_marks"] / df["total_internal_marks"] * 100).round(2)

                    st.success(f"Internal marks for Roll No: {data['roll_no']}")

                    # Beautify table
                    st.dataframe(
                        df.style
                        .set_properties(**{
                            "background-color": "#f9f9f9",
                            "color": "black",
                            "border": "1px solid #ddd",
                            "font-weight": "bold"
                        })
                        .highlight_max(color="lightgreen", axis=0)
                    )

                    # Optional: overall average
                    avg = df["total_internal_marks"].mean()
                    st.write(f"**Average Internal Marks:** {avg:.2f}")
                    st.progress(int(avg))  # assuming marks are out of 100
            else:
                st.error(response.json().get("detail", "Error fetching marks"))
        except Exception as e:
            st.error(f"Connection error: {e}")
