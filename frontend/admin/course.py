'''
Documentation: Course Management Streamlit App
Purpose
This Streamlit application provides a user interface for managing courses in a college or organizational system. It interacts with a FastAPI backend (http://127.0.0.1:8000/Cr) to perform CRUD operations (Create, Read, Update, Delete).

Features
View Courses

Fetches all courses from GET /Cr/courses/.

Displays them in a table using st.table().

Handles empty results and error responses gracefully.

Create Course

Inputs: Course Code, Course Name.

Fetches branch list from GET /br/branches/.

Provides a dropdown (st.selectbox) for selecting a branch.

Sends a POST /Cr/courses/ request with course details.

Displays success or error messages.

Update Course

Fetches existing courses (GET /Cr/courses/) for selection.

Uses course_code for dropdown display and backend updates.

Inputs: New Course Name, New Branch Name.

Fetches branch list (GET /br/branches/) for reassignment.

Sends a PUT /Cr/courses/{course_code} request with updated details.

Displays success or error messages.

Delete Course

Fetches existing courses (GET /Cr/courses/) for selection.

Uses course_code for dropdown display and backend deletion.

Sends a DELETE /Cr/courses/{course_code} request.

Displays success or error messages.

API Endpoints Used
GET /Cr/courses/ → Retrieve all courses.

POST /Cr/courses/ → Create a new course.

PUT /Cr/courses/{course_code} → Update an existing course.

DELETE /Cr/courses/{course_code} → Delete a course.

GET /br/branches/ → Retrieve branch list for dropdowns.
'''

import streamlit as st
import requests

a = "http://127.0.0.1:8000/admin"
API_URL = "http://127.0.0.1:8000/admin/Cr"  # FastAPI backend

st.title("Course Management")

tab1, tab2, tab3, tab4 = st.tabs(["View Courses", "Create Course", "Update Course", "Delete Course"])

# View Courses
with tab1:
    st.header("All Courses")
    if st.button("Load Courses"):
        response = requests.get(f"{API_URL}/courses/")
        if response.status_code == 200:
            data = response.json()
            if data:
                st.table(data)
            else:
                st.write("No courses found.")
        else:
            st.error(response.json())

# Create Course
with tab2:
    st.header("Create a New Course")
    course_code = st.text_input("Course Code")
    course_name = st.text_input("Course Name")

    # Fetch branches for dropdown
    branch_response = requests.get(f"{a}/br/branches/")
    branch_options = []
    if branch_response.status_code == 200:
        branch_data = branch_response.json()
        branch_options = [b["branch_name"] for b in branch_data]

    branch_name = st.selectbox("Select Branch", branch_options)

    if st.button("Create Course"):
        response = requests.post(
            f"{API_URL}/courses/",
            params={"course_code": course_code, "course_name": course_name, "branch_name": branch_name}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Update Course
with tab3:
    st.header("Update Course")

    # Fetch courses for dropdown
    course_response = requests.get(f"{API_URL}/courses/")
    course_options = []
    if course_response.status_code == 200:
        course_data = course_response.json()
        course_options = [c["course_code"] for c in course_data]

    course_code = st.selectbox("Select Course to Update", course_options)

    new_course_name = st.text_input("New Course Name")

    # Fetch branches for dropdown
    branch_response = requests.get(f"{a}/br/branches/")
    branch_options = []
    if branch_response.status_code == 200:
        branch_data = branch_response.json()
        branch_options = [b["branch_name"] for b in branch_data]

    new_branch_name = st.selectbox("Select New Branch", branch_options)

    if st.button("Update Course"):
        response = requests.put(
            f"{API_URL}/courses/{course_code}",
            params={"new_course_name": new_course_name, "new_branch_name": new_branch_name}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Delete Course
with tab4:
    st.header("Delete Course")

    # Fetch courses for dropdown
    course_response = requests.get(f"{API_URL}/courses/")
    course_options = []
    if course_response.status_code == 200:
        course_data = course_response.json()
        course_options = [c["course_code"] for c in course_data]

    course_code = st.selectbox("Select Course to Delete", course_options)

    if st.button("Delete Course"):
        response = requests.delete(f"{API_URL}/courses/{course_code}")
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())
