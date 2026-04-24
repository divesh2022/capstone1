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
