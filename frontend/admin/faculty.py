'''
Faculty Management App Documentation
Overview
This Streamlit application provides a frontend interface for managing Faculty Members in a college system. It interacts with a FastAPI backend (http://127.0.0.1:8000/fc) to perform CRUD (Create, Read, Update, Delete) operations on faculty records. Colleges and departments are fetched dynamically from related endpoints.

🔗 Backend API Endpoints
Colleges

GET /cg/colleges/ → Fetch all colleges (returns college_name, college_pk)

Departments

GET /dp/departments/{college_pk} → Fetch all departments under a specific college

Faculty

GET /fc/faculties/ → Fetch all faculty members

POST /fc/faculties/ → Create a new faculty member

PUT /fc/faculties/{email} → Update an existing faculty member (identified by email)

DELETE /fc/faculties/{email} → Delete a faculty member (identified by email)

🖥️ Tabs Functionality
1. View Faculty
Displays all faculty members in a table.

On Load Faculty:

Sends GET /faculties/.

Shows results in a table or a message if none found.

2. Create Faculty
Dropdown (create_college_select) to select a college.

Inputs:

Faculty Name (create_name_input)

Faculty Email (create_email_input)

Designation (create_designation_input)

Dropdown to select department (fetched via GET /dp/departments/{college_pk}).

On Create Faculty:

Sends POST /faculties/ with parameters:

name, email, designation, dept_name.

Displays success or error message.

3. Update Faculty
Dropdown (update_college_select) to select a college.

Dropdown (update_faculty_select) to select faculty by email.

Inputs:

New Name (update_name_input)

New Designation (update_designation_input)

Dropdown (update_dept_select) to select new department.

On Update Faculty:

Sends PUT /faculties/{email} with updated values.

Displays success or error message.

4. Delete Faculty
Dropdown to select faculty by email.

On Delete Faculty:

Sends DELETE /faculties/{email}.

Displays success or error message.
'''
import streamlit as st
import requests
a = "http://127.0.0.1:8000/admin"
API_URL = "http://127.0.0.1:8000/admin/fc"  # FastAPI backend

st.title("Faculty Management")

tab1, tab2, tab3, tab4 = st.tabs(["View Faculty", "Create Faculty", "Update Faculty", "Delete Faculty"])

# View Faculty
with tab1:
    st.header("All Faculty Members")
    if st.button("Load Faculty"):
        response = requests.get(f"{API_URL}/faculties/")
        if response.status_code == 200:
            data = response.json()
            if data:
                st.table(data)
            else:
                st.write("No faculty found.")
        else:
            st.error(response.json())

# Create Faculty
with tab2:
       # Fetch colleges for dropdown
    college_response = requests.get(f"{a}/cg/colleges/")
    college_options = []
    if college_response.status_code == 200:
        college_data = college_response.json()
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    new_college = st.selectbox(
    "Select College",
    list(college_options.keys()),
    key="create_college_select"
    )
 
    st.header("Create a New Faculty")
    name = st.text_input("Faculty Name",key="create_name_input")
    email = st.text_input("Faculty Email",key="create_email_input")
    designation = st.text_input("Designation",key="create_designation_input")

    # Fetch departments for dropdown
    dept_response = requests.get(f"{a}/dp/departments/{college_options[new_college]}")
    dept_options = []
    if dept_response.status_code == 200:
        dept_data = dept_response.json()
        dept_options = [d["dept_name"] for d in dept_data]

    dept_name = st.selectbox("Select Department", dept_options)

    if st.button("Create Faculty"):
        response = requests.post(
            f"{API_URL}/faculties/",
            params={"name": name, "email": email, "designation": designation, "dept_name": dept_name}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())
    

# Update Faculty
# Update Faculty
with tab3:
    st.header("Update Faculty")

    # Fetch colleges for dropdown
    college_response = requests.get(f"{a}/cg/colleges/")
    college_options = {}
    if college_response.status_code == 200:
        college_data = college_response.json()
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    new_college = st.selectbox(
        "Select College",
        list(college_options.keys()),
        key="update_college_select"
    )

    # Faculty dropdown
    faculty_response = requests.get(f"{API_URL}/faculties/")
    faculty_options = []
    if faculty_response.status_code == 200:
        faculty_data = faculty_response.json()
        faculty_options = [f["email"] for f in faculty_data]

    email = st.selectbox(
        "Select Faculty (by Email)",
        faculty_options,
        key="update_faculty_select"
    )

    # Update fields
    new_name = st.text_input("New Name", key="update_name_input")
    new_designation = st.text_input("New Designation", key="update_designation_input")

    # Department dropdown
    dept_response = requests.get(f"{a}/dp/departments/{college_options[new_college]}")
    dept_options = []
    if dept_response.status_code == 200:
        dept_data = dept_response.json()
        dept_options = [d["dept_name"] for d in dept_data]

    new_dept_name = st.selectbox(
        "Select New Department",
        dept_options,
        key="update_dept_select"
    )

    if st.button("Update Faculty", key="update_faculty_button"):
        response = requests.put(
            f"{API_URL}/faculties/{email}",
            params={
                "new_name": new_name,
                "new_designation": new_designation,
                "new_dept_name": new_dept_name
            }
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())


# Delete Faculty
with tab4:
    st.header("Delete Faculty")

    # Fetch faculty for dropdown
    faculty_response = requests.get(f"{API_URL}/faculties/")
    faculty_options = []
    if faculty_response.status_code == 200:
        faculty_data = faculty_response.json()
        faculty_options = [f["email"] for f in faculty_data]

    email = st.selectbox("Select Faculty to Delete (by Email)", faculty_options)

    if st.button("Delete Faculty"):
        response = requests.delete(f"{API_URL}/faculties/{email}")
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())
