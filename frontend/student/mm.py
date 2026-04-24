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
