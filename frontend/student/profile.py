import streamlit as st
import requests

st.title("🎓 Student Profile")

rollno = st.text_input("Enter Roll Number:")

if st.button("Get Profile"):
    try:
        response = requests.get("http://127.0.0.1:8000/student/profile", headers={"rollno": rollno})
        if response.status_code == 200:
            data = response.json()
            st.write("**Roll No:**", data.get("roll_no"))
            st.write("**Batch:**", data.get("batch"))
            st.write("**Phone Number:**", data.get("phone_number"))
            st.write("**Department:**", data.get("department"))
            st.write("**College:**", data.get("college"))
        else:
            st.error(response.json().get("detail", "Error fetching profile"))
    except Exception as e:
        st.error(f"Connection error: {e}")
