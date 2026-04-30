import requests
import streamlit as st
import pandas as pd
url = "http://127.0.0.1:8000/faculty/low/low"

def get_low_attendance(semester, dept_name, subject_name, faculty_id):
    
    params = {
        "semester": semester,
        "dept_name": dept_name,
        "subject_name": subject_name,
        "faculty_id": faculty_id
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def show_attendance_ui():
    st.title("📊 Attendance Dashboard")
    st.write("Fetch students below 75% attendance for a subject.")

    with st.form("attendance_form"):
        semester = st.number_input("Semester", min_value=1, max_value=8, step=1)
        dept_name = st.text_input("Department Name", value="Computer Science")
        subject_name = st.text_input("Subject Name", value="Programming Basics")
        faculty_id = st.number_input("Faculty ID", min_value=1, step=1)
        submitted = st.form_submit_button("Fetch Records")

    if submitted:
        try:
            data = get_low_attendance(semester, dept_name, subject_name, faculty_id)
            if data:
                df = pd.DataFrame(data)
                st.subheader("Students Below 75% Attendance")
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name="low_attendance.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No students found below 75% attendance.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
