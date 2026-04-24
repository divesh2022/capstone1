'''
HOD Management App Documentation
Overview
This Streamlit application provides a frontend interface for managing Head of Department (HOD) assignments in a college system. It interacts with a FastAPI backend (http://127.0.0.1:8000/hd) to perform CRUD (Create, Read, Update, Delete) operations on HOD records. Colleges, departments, and faculty are fetched dynamically from related endpoints.

🔗 Backend API Endpoints
Colleges

GET /cg/colleges/ → Fetch all colleges (returns college_name, college_pk)

Departments

GET /dp/departments/{college_pk} → Fetch all departments under a specific college

Faculty

GET /fc/faculties/ → Fetch all faculty members (returns email)

HOD

GET /hd/hods/ → Fetch all HOD assignments

POST /hd/hods/ → Assign a faculty member as HOD

PUT /hd/hods/{dept_name} → Update HOD assignment for a department

DELETE /hd/hods/{dept_name} → Delete HOD assignment for a department

🖥️ Tabs Functionality
1. View HODs
Displays all HOD assignments in a table.

On Load HODs:

Sends GET /hods/.

Shows results in a table or a message if none found.

2. Assign HOD
Dropdown (create_college_select) to select a college.

Dropdown to select department (fetched via GET /dp/departments/{college_pk}).

Dropdown to select faculty by email (fetched via GET /fc/faculties/).

On Assign HOD:

Sends POST /hods/ with parameters:

dept_name, faculty_email.

Displays success or error message.

3. Update HOD
Dropdown to select a college.

Dropdown to select department (HOD to update).

Dropdown to select new faculty by email.

On Update HOD:

Sends PUT /hods/{dept_name} with parameter:

new_faculty_email.

Displays success or error message.

4. Delete HOD
Dropdown (delete_college_select) to select a college.

Dropdown to select department (HOD to delete).

On Delete HOD:

Sends DELETE /hods/{dept_name}.


'''
import streamlit as st
import requests
a = "http://127.0.0.1:8000/admin"
API_URL = "http://127.0.0.1:8000/admin/hd"  # FastAPI backend

st.title("HOD Management")

tab1, tab2, tab3, tab4 = st.tabs(["View HODs", "Assign HOD", "Update HOD", "Delete HOD"])

# View HODs
with tab1:
    st.header("All HODs")
    if st.button("Load HODs"):
        response = requests.get(f"{API_URL}/hods/")
        if response.status_code == 200:
            data = response.json()
            if data:
                st.table(data)
            else:
                st.write("No HODs found.")
        else:
            st.error(response.json())

# Assign HOD
with tab2:
    st.header("Assign a Faculty as HOD")
    # Fetch colleges for dropdown
    college_response = requests.get(f"{a}/cg/colleges/")
    college_options = []
    if college_response.status_code == 200:
        college_data = college_response.json()
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    new_college = st.selectbox("Select New College", list(college_options.keys()),key="create_college_select")
    # Fetch departments for dropdown
    dept_response = requests.get(f"{a}/dp/departments/{college_options[new_college]}")
    dept_options = []
    if dept_response.status_code == 200:
        dept_data = dept_response.json()
        dept_options = [d["dept_name"] for d in dept_data]

    dept_name = st.selectbox("Select Department", dept_options)

    # Fetch faculty for dropdown
    faculty_response = requests.get(f"{a}/fc/faculties/")
    faculty_options = []
    if faculty_response.status_code == 200:
        faculty_data = faculty_response.json()
        faculty_options = [f["email"] for f in faculty_data]

    faculty_email = st.selectbox("Select Faculty (by Email)", faculty_options)

    if st.button("Assign HOD"):
        response = requests.post(
            f"{API_URL}/hods/",
            params={"dept_name": dept_name, "faculty_email": faculty_email}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Update HOD
with tab3:
    st.header("Update HOD Assignment")
    # Fetch colleges for dropdown
    college_response = requests.get(f"{a}/cg/colleges/")
    college_options = []
    if college_response.status_code == 200:
        college_data = college_response.json()
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    new_college = st.selectbox("Select New College", list(college_options.keys()))
    # Fetch departments for dropdown
    dept_response = requests.get(f"{a}/dp/departments/{college_options[new_college]}")
    dept_options = []
    if dept_response.status_code == 200:
        dept_data = dept_response.json()
        dept_options = [d["dept_name"] for d in dept_data]

    dept_name = st.selectbox("Select Department (HOD to Update)", dept_options)

    # Fetch faculty for dropdown
    faculty_response = requests.get(f"{a}/fc/faculties/")
    faculty_options = []
    if faculty_response.status_code == 200:
        faculty_data = faculty_response.json()
        faculty_options = [f["email"] for f in faculty_data]

    new_faculty_email = st.selectbox("Select New Faculty (by Email)", faculty_options)

    if st.button("Update HOD"):
        response = requests.put(
            f"{API_URL}/hods/{dept_name}",
            params={"new_faculty_email": new_faculty_email}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Delete HOD
with tab4:
    st.header("Delete HOD Assignment")
    # Fetch colleges for dropdown
    college_response = requests.get(f"{a}/cg/colleges/")
    college_options = []
    if college_response.status_code == 200:
        college_data = college_response.json()
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    new_college = st.selectbox("Select New College", list(college_options.keys()),key="delete_college_select")
    # Fetch departments for dropdown
    dept_response = requests.get(f"{a}/dp/departments/{college_options[new_college]}")
    dept_options = []
    if dept_response.status_code == 200:
        dept_data = dept_response.json()
        dept_options = [d["dept_name"] for d in dept_data]

    dept_name = st.selectbox("Select Department (HOD to Delete)", dept_options)

    if st.button("Delete HOD"):
        response = requests.delete(f"{API_URL}/hods/{dept_name}")
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())
