'''
Student Management App Documentation
Overview
This Streamlit application provides a frontend interface for managing Students in a college system. It interacts with a FastAPI backend (http://127.0.0.1:8000/st) to perform CRUD (Create, Read, Update, Delete) operations on student records. Colleges and departments are fetched dynamically from related endpoints to ensure data consistency.

🔗 Backend API Endpoints
Colleges

GET /cg/colleges/ → Fetch all colleges (returns college_name, college_pk)

Departments

GET /dp/departments/{college_pk} → Fetch all departments under a specific college

Students

GET /st/students/ → Fetch all students

POST /st/students/ → Create a new student

PUT /st/students/{roll_no} → Update an existing student (identified by roll number)

DELETE /st/students/{roll_no} → Delete a student (identified by roll number)

🖥️ Tabs Functionality
1. View Students
Displays all students in a table.

On Load Students:

Sends GET /students/.

Shows results in a table or a message if none found.

Displays error if backend returns non-200 status.

2. Create Student
Inputs:

Roll Number

Batch

Phone Number

Dropdown (create_college_select) to select a college.

Dropdown to select department (fetched via GET /dp/departments/{college_pk}).

On Create Student:

Sends POST /students/ with parameters:

roll_no, batch, phone_number, dept_name.

Displays success or error message.

3. Update Student
Dropdown (update_college_select) to select a college.

Dropdown to select student by roll number (fetched via GET /students/).

Inputs:

New Batch

New Phone Number

Dropdown to select new department.

On Update Student:

Sends PUT /students/{roll_no} with parameters:

new_batch, new_phone_number, new_dept_name.

Displays success or error message.

4. Delete Student
Dropdown to select student by roll number.

On Delete Student:

Sends DELETE /students/{roll_no}.


'''
import streamlit as st
import requests
a = "http://127.0.0.1:8000/admin"
API_URL = "http://127.0.0.1:8000/admin/st"  # FastAPI backend

st.title("Student Management")

tab1, tab2, tab3, tab4 = st.tabs(["View Students", "Create Student", "Update Student", "Delete Student"])

# View Students
with tab1:
    st.header("All Students")
    if st.button("Load Students"):
        response = requests.get(f"{API_URL}/students/")
        if response.status_code == 200:
            data = response.json()
            if data:
                st.table(data)
            else:
                st.write("No students found.")
        else:
            st.error(response.json())

# Create Student
with tab2:
    st.header("Create a New Student")
    roll_no = st.text_input("Roll Number")
    batch = st.text_input("Batch")
    phone_number = st.text_input("Phone Number")
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

    if st.button("Create Student"):
        response = requests.post(
            f"{API_URL}/students/",
            params={"roll_no": roll_no, "batch": batch, "phone_number": phone_number, "dept_name": dept_name}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Update Student
with tab3:
    st.header("Update Student")
    # Fetch colleges for dropdown
    college_response = requests.get(f"{a}/cg/colleges/")
    college_options = []
    if college_response.status_code == 200:
        college_data = college_response.json()
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    new_college = st.selectbox("Select New College", list(college_options.keys()),key="update_college_select")
    # Fetch students for dropdown
    student_response = requests.get(f"{API_URL}/students/")
    student_options = []
    if student_response.status_code == 200:
        student_data = student_response.json()
        student_options = [s["roll_no"] for s in student_data]

    roll_no = st.selectbox("Select Student (by Roll Number)", student_options)

    new_batch = st.text_input("New Batch")
    new_phone_number = st.text_input("New Phone Number")

    # Fetch departments for dropdown
    dept_response = requests.get(f"{a}/dp/departments/{college_options[new_college]}")
    dept_options = []
    if dept_response.status_code == 200:
        dept_data = dept_response.json()
        dept_options = [d["dept_name"] for d in dept_data]

    new_dept_name = st.selectbox("Select New Department", dept_options)

    if st.button("Update Student"):
        response = requests.put(
            f"{API_URL}/students/{roll_no}",
            params={"new_batch": new_batch, "new_phone_number": new_phone_number, "new_dept_name": new_dept_name}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Delete Student
with tab4:
    st.header("Delete Student")

    # Fetch students for dropdown
    student_response = requests.get(f"{API_URL}/students/")
    student_options = []
    if student_response.status_code == 200:
        student_data = student_response.json()
        student_options = [s["roll_no"] for s in student_data]

    roll_no = st.selectbox("Select Student to Delete (by Roll Number)", student_options)

    if st.button("Delete Student"):
        response = requests.delete(f"{API_URL}/students/{roll_no}")
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())
