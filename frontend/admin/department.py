'''
Department Management App Documentation
Overview
This Streamlit application provides a frontend interface for managing Departments in a college system. It interacts with a FastAPI backend (http://127.0.0.1:8000/dp) to perform CRUD (Create, Read, Update, Delete) operations on departments, with college associations handled via dropdowns.

🔗 Backend API Endpoints
Colleges

GET /colleges/ → Fetch all colleges (returns college_name, college_pk)

Departments

GET /departments/{college_pk} → Fetch all departments under a specific college

POST /departments/ → Create a new department

PUT /departments/{dept_pk} → Update an existing department

DELETE /departments/{dept_pk} → Delete a department

🖥️ Tabs Functionality
1. View Departments
Fetches all colleges and displays them in a dropdown (view_college_select).

When a college is selected and Load Departments is clicked:

Sends GET /departments/{college_pk}.

Displays the department list in a table.

2. Create Department
Inputs: Department ID, Department Name.

Dropdown (create_college_select) to select a college.

On Create Department:

Sends POST /departments/ with parameters:

dept_id, dept_name, college_pk.

Displays success or error message.

3. Update Department
Dropdown to select a college (update_college_select).

Fetches departments for that college (GET /departments/{college_pk}).

Dropdown (update_dept_select) to select department.

Inputs: New Department ID, New Department Name.

On Update Department:

Sends PUT /departments/{dept_pk} with updated values.

Displays success or error message.

4. Delete Department
Dropdown (delete_college_select) to select a college.

Fetches departments for that college (GET /departments/{college_pk}).

Dropdown (delete_dept_select) to select department.

On Delete Department:

Sends DELETE /departments/{dept_pk}.


'''

import streamlit as st
import requests

a = "http://127.0.0.1:8000/admin"

API_URL = "http://127.0.0.1:8000/admin/dp"  # FastAPI backend

st.title("Department Management")

tab1, tab2, tab3, tab4 = st.tabs(["View Departments", "Create Department", "Update Department", "Delete Department"])

# View Departments
with tab1:
    # Fetch colleges for dropdown
    college_response = requests.get(f"{API_URL}/colleges/")
    college_options = []
    if college_response.status_code == 200:
        college_data = college_response.json()
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    new_college = st.selectbox("Select New College", list(college_options.keys()),key="view_college_select")    
    st.header("All Departments")
    if st.button("Load Departments"):
        response = requests.get(f"{API_URL}/departments/{college_options[new_college]}")
        if response.status_code == 200:
            data = response.json()
            if data:
                st.table(data)
            else:
                st.write("No departments found.")
        else:
            st.error(response.json())

# Create Department
with tab2:
    st.header("Create a New Department")
    dept_id = st.text_input("Department ID")
    dept_name = st.text_input("Department Name")

    # Fetch colleges for dropdown
    college_response = requests.get(f"{API_URL}/colleges/")
    college_options = []
    if college_response.status_code == 200:
        college_data = college_response.json()
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    selected_college = st.selectbox("Select College", list(college_options.keys()),key="create_college_select")

    if st.button("Create Department"):
        college_pk = college_options[selected_college]
        response = requests.post(
            f"{API_URL}/departments/",
            params={"dept_id": dept_id, "dept_name": dept_name, "college_pk": college_pk}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Update Department
with tab3:
    st.header("Update Department")
    # Fetch colleges for dropdown
    college_response = requests.get(f"{API_URL}/colleges/")
    college_options = []
    if college_response.status_code == 200:
        college_data = college_response.json()
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    new_college = st.selectbox("Select New College", list(college_options.keys()))
    # Fetch departments for dropdown
    dept_response = requests.get(f"{API_URL}/departments/{college_options[new_college]}")
    dept_options = []
    if dept_response.status_code == 200:
        dept_data = dept_response.json()
        dept_options = {d["dept_name"]: d["dept_pk"] for d in dept_data}

    selected_dept = st.selectbox("Select Department to Update", list(dept_options.keys()),key="update_dept_select")

    new_dept_id = st.text_input("New Department ID")
    new_dept_name = st.text_input("New Department Name")


    if st.button("Update Department"):
        dept_pk = dept_options[selected_dept]
        college_pk = college_options[new_college]
        response = requests.put(
            f"{API_URL}/departments/{dept_pk}",
            params={"dept_id": new_dept_id, "dept_name": new_dept_name, "college_pk": college_pk}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Tab 4: Delete Department
with tab4:
    st.header("Delete Department")

    # Fetch colleges for dropdown
    college_response = requests.get(f"{API_URL}/colleges/")
    college_options = {}
    if college_response.status_code == 200:
        college_data = college_response.json()
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    # College dropdown with unique key
    new_college = st.selectbox(
        "Select College",
        list(college_options.keys()),
        key="delete_college_select"
    )

    # Fetch departments for dropdown
    dept_response = requests.get(f"{API_URL}/departments/{college_options[new_college]}")
    dept_options = {}
    if dept_response.status_code == 200:
        dept_data = dept_response.json()
        dept_options = {d["dept_name"]: d["dept_pk"] for d in dept_data}

    # Department dropdown with unique key
    selected_dept = st.selectbox(
        "Select Department to Delete",
        list(dept_options.keys()),
        key="delete_dept_select"
    )

    # Delete button
    if st.button("Delete Department", key="delete_dept_button"):
        dept_pk = dept_options[selected_dept]
        response = requests.delete(f"{API_URL}/departments/{dept_pk}")
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())
