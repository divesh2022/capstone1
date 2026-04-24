import streamlit as st
import requests

BASE_URL = "http://localhost:8000/hod/Ci"  # adjust if your FastAPI runs elsewhere

st.title("Class Incharge Management")

tab1, tab2, tab3 = st.tabs(["View Allocations", "Allocate Incharge", "Browse Faculties & Classes"])

with tab1:
    st.header("Class Incharge Allocations")
    resp = requests.get(f"{BASE_URL}/class-incharge/")
    if resp.ok:
        data = resp.json()
        st.table(data)

with tab2:
    st.header("Allocate Class Incharge")
    # Fetch dropdown data
    faculties = requests.get(f"{BASE_URL}/faculties/").json()
    classes = requests.get(f"{BASE_URL}/classes/").json()

    batch = st.selectbox("Select Batch", sorted({c["batch"] for c in classes}))
    dept_name = st.selectbox("Select Department", sorted({c["dept_name"] for c in classes}))
    faculty_email = st.selectbox("Select Faculty", [f["email"] for f in faculties])
    semester = st.number_input("Semester", min_value=1, max_value=8, step=1)

    if st.button("Allocate"):
        payload = {
            "batch": batch,
            "dept_name": dept_name,
            "faculty_email": faculty_email,
            "semester": semester
        }
        resp = requests.post(f"{BASE_URL}/class-incharge/", params=payload)
        if resp.ok:
            st.success(resp.json()["status"])
        else:
            st.error("Failed to allocate")

with tab3:
    st.header("Faculties")
    st.table(requests.get(f"{BASE_URL}/faculties/").json())

    st.header("Classes")
    st.table(requests.get(f"{BASE_URL}/classes/").json())
