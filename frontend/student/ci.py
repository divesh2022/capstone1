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
