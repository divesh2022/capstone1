'''Overview
This module defines the Head of Department (HOD) dashboard for timetable management in the Campus ERP system. Built with Streamlit, it provides HODs with tools to create, update, and manage timetables for courses, branches, and subjects. It acts as the frontend layer that communicates with backend APIs for scheduling workflows.

Key Components
🔹 Imports
streamlit as st → Provides UI components (tabs, forms, tables).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular timetable data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

View Timetable → Displays timetable records for courses and branches.

Add Timetable Entry → Allows HODs to create new timetable entries (day, time, subject, faculty).

Update Timetable Entry → Provides interface to modify existing timetable records.

Delete Timetable Entry → Enables removal of timetable records.

Forms  
Each tab contains forms for data entry (course ID, branch ID, subject ID, faculty ID, day, time slot).

Tables  
Timetable records are displayed in tabular format using Pandas DataFrames for easy review.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/timetable/ → Manage timetable records

/courses/ → Link timetables to courses

/branches/ → Link timetables to branches

/subjects/ → Link timetables to subjects

/faculty/ → Assign faculty to timetable slots

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves timetable data from backend APIs.

post_data(endpoint, payload)  
Submits new timetable records to backend.

update_data(endpoint, payload)  
Updates existing timetable records.

delete_data(endpoint, id)  
Removes timetable records when required'''
import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://localhost:8000/hod"  # Adjust if FastAPI runs elsewhere

st.title("Total Internal Marks Dashboard")

tab1, tab2, tab3 = st.tabs(["View Marks", "Export Data", "Filter, Sort & Export"])

with tab1:
    st.header("All Internal Marks")
    resp = requests.get(f"{BASE_URL}/Tm/total-internal-marks")
    if resp.ok:
        data = resp.json()
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.session_state["marks_data"] = df
    else:
        st.error(resp.text)

with tab2:
    st.header("Export Raw Marks")
    if "marks_data" in st.session_state and not st.session_state["marks_data"].empty:
        df = st.session_state["marks_data"]

        # CSV export
        csv_file = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV File",
            data=csv_file,
            file_name="marks_export.csv",
            mime="text/csv"
        )

        # Excel export (requires openpyxl)
        try:
            excel_file = "marks_export.xlsx"
            df.to_excel(excel_file, index=False, engine="openpyxl")
            with open(excel_file, "rb") as f:
                st.download_button(
                    label="Download Excel File",
                    data=f,
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except ImportError:
            st.warning("Excel export requires 'openpyxl'. Install it with: pip install openpyxl")
    else:
        st.info("No marks data available yet. Please fetch marks first in the 'View Marks' tab.")

with tab3:
    st.header("Filter, Sort & Export Subset")
    if "marks_data" in st.session_state and not st.session_state["marks_data"].empty:
        df = st.session_state["marks_data"]

        # Filter by subject code
        subject_codes = df["subject_code"].unique().tolist()
        selected_subject = st.selectbox("Filter by Subject Code", ["All"] + subject_codes)
        if selected_subject != "All":
            df = df[df["subject_code"] == selected_subject]

        # Select columns to display
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect("Select columns to display", all_columns, default=all_columns)
        df = df[selected_columns]

        # Multi-column sorting
        sort_columns = st.multiselect("Select columns to sort by", all_columns)
        if sort_columns:
            ascending = st.radio("Sort order", ["Ascending", "Descending"]) == "Ascending"
            df = df.sort_values(by=sort_columns, ascending=ascending)

        st.dataframe(df)

        # Export the filtered/sorted subset
        csv_file = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered CSV",
            data=csv_file,
            file_name="marks_filtered.csv",
            mime="text/csv"
        )

        try:
            excel_file = "marks_filtered.xlsx"
            df.to_excel(excel_file, index=False, engine="openpyxl")
            with open(excel_file, "rb") as f:
                st.download_button(
                    label="Download Filtered Excel",
                    data=f,
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except ImportError:
            st.warning("Excel export requires 'openpyxl'. Install it with: pip install openpyxl")
    else:
        st.info("No marks data available yet. Please fetch marks first in the 'View Marks' tab.")
