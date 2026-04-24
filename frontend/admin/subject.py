'''
Subject Management App Documentation
Overview
This Streamlit application provides a frontend interface for managing Subjects in a college system. It interacts with a FastAPI backend (http://127.0.0.1:8000/Sub) to perform CRUD (Create, Read, Update, Delete) operations on subject records. Courses are fetched dynamically from related endpoints to ensure data consistency.

🔗 Backend API Endpoints
Courses

GET /Cr/courses/ → Fetch all courses (returns course_name)

Subjects

GET /Sub/subjects/ → Fetch all subjects

POST /Sub/subjects/ → Create a new subject

PUT /Sub/subjects/{subject_code} → Update an existing subject (identified by subject code)

DELETE /Sub/subjects/{subject_code} → Delete a subject (identified by subject code)

🖥️ Tabs Functionality
1. View Subjects
Displays all subjects in a table.

On Load Subjects:

Sends GET /subjects/.

Shows results in a table or a message if none found.

Displays error if backend returns non-200 status.

2. Create Subject
Inputs:

Subject Code

Subject Name

Syllabus PDF (URL or path)

Dropdown to select course (fetched via GET /Cr/courses/).

On Create Subject:

Sends POST /subjects/ with parameters:

subject_code, subject_name, course_name, syllabus_pdf.

Displays success or error message.

3. Update Subject
Dropdown to select subject by code (fetched via GET /subjects/).

Inputs:

New Subject Name

New Syllabus PDF (URL or path)

Dropdown to select new course (fetched via GET /Cr/courses/).

On Update Subject:

Sends PUT /subjects/{subject_code} with parameters:

new_subject_name, new_course_name, new_syllabus_pdf.

Displays success or error message.

4. Delete Subject
Dropdown to select subject by code (fetched via GET /subjects/).

On Delete Subject:

Sends DELETE /subjects/{subject_code}.

Displays success or error message.
'''
import streamlit as st
import requests

a = "http://127.0.0.1:8000/admin"
API_URL = "http://127.0.0.1:8000/admin/Sub"  # FastAPI backend

st.title("Subject Management")

tab1, tab2, tab3, tab4 = st.tabs(["View Subjects", "Create Subject", "Update Subject", "Delete Subject"])

# View Subjects
with tab1:
    st.header("All Subjects")
    if st.button("Load Subjects"):
        response = requests.get(f"{API_URL}/subjects/")
        if response.status_code == 200:
            data = response.json()
            if data:
                st.table(data)
            else:
                st.write("No subjects found.")
        else:
            st.error(response.json())

# Create Subject
with tab2:
    st.header("Create a New Subject")
    subject_code = st.text_input("Subject Code")
    subject_name = st.text_input("Subject Name")
    syllabus_pdf = st.text_input("Syllabus PDF (URL or path)")

    # Fetch courses for dropdown
    course_response = requests.get(f"{a}/Cr/courses/")
    course_options = []
    if course_response.status_code == 200:
        course_data = course_response.json()
        course_options = [c["course_name"] for c in course_data]

    course_name = st.selectbox("Select Course", course_options)

    if st.button("Create Subject"):
        response = requests.post(
            f"{API_URL}/subjects/",
            params={"subject_code": subject_code, "subject_name": subject_name, "course_name": course_name, "syllabus_pdf": syllabus_pdf}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Update Subject
with tab3:
    st.header("Update Subject")

    # Fetch subjects for dropdown
    subject_response = requests.get(f"{API_URL}/subjects/")
    subject_options = []
    if subject_response.status_code == 200:
        subject_data = subject_response.json()
        subject_options = [s["subject_code"] for s in subject_data]

    subject_code = st.selectbox("Select Subject to Update", subject_options)

    new_subject_name = st.text_input("New Subject Name")
    new_syllabus_pdf = st.text_input("New Syllabus PDF (URL or path)")

    # Fetch courses for dropdown
    course_response = requests.get(f"{a}/Cr/courses/")
    course_options = []
    if course_response.status_code == 200:
        course_data = course_response.json()
        course_options = [c["course_name"] for c in course_data]

    new_course_name = st.selectbox("Select New Course", course_options)

    if st.button("Update Subject"):
        response = requests.put(
            f"{API_URL}/subjects/{subject_code}",
            params={"new_subject_name": new_subject_name, "new_course_name": new_course_name, "new_syllabus_pdf": new_syllabus_pdf}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Delete Subject
with tab4:
    st.header("Delete Subject")

    # Fetch subjects for dropdown
    subject_response = requests.get(f"{API_URL}/subjects/")
    subject_options = []
    if subject_response.status_code == 200:
        subject_data = subject_response.json()
        subject_options = [s["subject_code"] for s in subject_data]

    subject_code = st.selectbox("Select Subject to Delete", subject_options)

    if st.button("Delete Subject"):
        response = requests.delete(f"{API_URL}/subjects/{subject_code}")
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())
