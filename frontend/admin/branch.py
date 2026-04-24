'''
Documentation: Branch Management Streamlit App
Purpose
This Streamlit application provides a simple frontend for managing branches in a college or organizational database. It interacts with a FastAPI backend (http://127.0.0.1:8000) to perform CRUD operations (Create, Read, Update, Delete).

Features
View Branches

Fetches all branches from GET /br/branches/.

Displays them in a table using st.table().

Handles empty results and error responses gracefully.

Create Branch

Inputs: Branch ID, Branch Name.

Fetches department list from GET /dp/departments/.

Provides a dropdown (st.selectbox) for selecting a department.

Sends a POST /br/branches/ request with branch details.

Displays success or error messages.

Update Branch

Fetches existing branches (GET /br/branches/) for selection.

Inputs: New Branch ID, New Branch Name.

Fetches departments (GET /dp/departments/) for new assignment.

Sends a PUT /br/branches/{branch_name} request with updated details.

Displays success or error messages.

Delete Branch

Fetches existing branches (GET /br/branches/) for selection.

Sends a DELETE /br/branches/{branch_name} request.

Displays success or error messages.

API Endpoints Used
GET /br/branches/ → Retrieve all branches.

POST /br/branches/ → Create a new branch.

PUT /br/branches/{branch_name} → Update an existing branch.

DELETE /br/branches/{branch_name} → Delete a branch.

GET /dp/departments/ → Retrieve department list for dropdowns.
'''

import streamlit as st
import requests

a = "http://127.0.0.1:8000/admin"
API_URL = "http://127.0.0.1:8000/admin/br"  # FastAPI backend

st.title("Branch Management")

tab1, tab2, tab3, tab4 = st.tabs(["View Branches", "Create Branch", "Update Branch", "Delete Branch"])

# View Branches
with tab1:
    st.header("All Branches")
    if st.button("Load Branches"):
        response = requests.get(f"{API_URL}/branches/")
        if response.status_code == 200:
            data = response.json()
            if data:
                st.table(data)
            else:
                st.write("No branches found.")
        else:
            st.error(response.json())

# Create Branch
with tab2:
    st.header("Create a New Branch")
    branch_id = st.text_input("Branch ID")
    branch_name = st.text_input("Branch Name")

    # Fetch departments for dropdown
    dept_response = requests.get(f"{a}/dp/departments/")
    dept_options = []
    if dept_response.status_code == 200:
        dept_data = dept_response.json()
        dept_options = [d["dept_name"] for d in dept_data]

    dept_name = st.selectbox("Select Department", dept_options)

    if st.button("Create Branch"):
        response = requests.post(
            f"{API_URL}/branches/",
            params={"branch_id": branch_id, "branch_name": branch_name, "dept_name": dept_name}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Update Branch
with tab3:
    st.header("Update Branch")

    # Fetch branches for dropdown
    branch_response = requests.get(f"{API_URL}/branches/")
    branch_options = []
    if branch_response.status_code == 200:
        branch_data = branch_response.json()
        branch_options = [b["branch_name"] for b in branch_data]

    branch_name = st.selectbox("Select Branch to Update", branch_options)

    new_branch_id = st.text_input("New Branch ID")
    new_branch_name = st.text_input("New Branch Name")

    # Fetch departments for dropdown
    dept_response = requests.get(f"{a}/dp/departments/")
    dept_options = []
    if dept_response.status_code == 200:
        dept_data = dept_response.json()
        dept_options = [d["dept_name"] for d in dept_data]

    new_dept_name = st.selectbox("Select New Department", dept_options)

    if st.button("Update Branch"):
        response = requests.put(
            f"{API_URL}/branches/{branch_name}",
            params={"new_branch_id": new_branch_id, "new_branch_name": new_branch_name, "new_dept_name": new_dept_name}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Delete Branch
with tab4:
    st.header("Delete Branch")

    # Fetch branches for dropdown
    branch_response = requests.get(f"{API_URL}/branches/")
    branch_options = []
    if branch_response.status_code == 200:
        branch_data = branch_response.json()
        branch_options = [b["branch_name"] for b in branch_data]

    branch_name = st.selectbox("Select Branch to Delete", branch_options)

    if st.button("Delete Branch"):
        response = requests.delete(f"{API_URL}/branches/{branch_name}")
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())
