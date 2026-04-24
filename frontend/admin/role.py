'''
Roles Management App Documentation
Overview
This Streamlit application provides a frontend interface for managing Roles in a system. It interacts with a FastAPI backend (http://127.0.0.1:8000/role) to perform CRUD (Create, Read, Update, Delete) operations on role records. The app uses tabs to separate each operation for clarity.

🔗 Backend API Endpoints
Roles

POST /roles/ → Insert a new role

PUT /roles/{role_id} → Update an existing role by ID

DELETE /roles/{role_id} → Delete a role by ID

GET /roles/ → View all roles

🖥️ Tabs Functionality
1. Insert Role
Input: Role Name (text field).

On Insert:

Sends POST /roles/ with parameter:

role_name.

Displays backend response.

2. Update Role
Input: Role ID (numeric field).

Input: New Role Name (text field).

On Update:

Sends PUT /roles/{role_id} with parameter:

role_name.

Displays backend response.

3. Delete Role
Input: Role ID to Delete (numeric field).

On Delete:

Sends DELETE /roles/{role_id}.

Displays backend response.

4. View Roles
On Load Roles:

Sends GET /roles/.

Displays results in a table (role_id, role_name).

Shows message if no roles found.

Displays error if backend returns non-200 status.
'''
import streamlit as st
import requests
a = "http://127.0.0.1:8000/admin"

API_URL = "http://127.0.0.1:8000/admin/role"  # Adjust if FastAPI runs elsewhere

st.title("Roles Management Frontend")

# Tabs for each service
tab1, tab2, tab3, tab4 = st.tabs(["Insert Role", "Update Role", "Delete Role", "View Roles"])

# Insert Role
with tab1:
    st.header("Insert a New Role")
    role_name = st.text_input("Role Name")
    if st.button("Insert"):
        response = requests.post(f"{API_URL}/roles/", params={"role_name": role_name})
        st.write(response.json())

# Update Role
with tab2:
    st.header("Update Existing Role")
    role_id = st.number_input("Role ID", min_value=1, step=1)
    new_name = st.text_input("New Role Name")
    if st.button("Update"):
        response = requests.put(f"{API_URL}/roles/{role_id}", params={"role_name": new_name})
        st.write(response.json())

# Delete Role
with tab3:
    st.header("Delete Role")
    role_id = st.number_input("Role ID to Delete", min_value=1, step=1)
    if st.button("Delete"):
        response = requests.delete(f"{API_URL}/roles/{role_id}")
        st.write(response.json())

# Tab 4: View Roles
with tab4:
    st.header("View All Roles")
    if st.button("Load Roles"):
        response = requests.get(f"{API_URL}/roles/")
        if response.status_code == 200:
            data = response.json().get("roles", [])
            if data:
                st.table(data)  # shows role_id and role_name in a table
            else:
                st.write("No roles found.")
        else:
            st.error(response.json())
