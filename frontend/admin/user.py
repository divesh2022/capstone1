'''
Users Management App Documentation
Overview
This Streamlit application provides a frontend interface for managing Users in a system. It interacts with a FastAPI backend (http://127.0.0.1:8000/user) to perform CRUD (Create, Read, Update, Delete) operations and supports bulk upload of users via CSV. Tabs are used to separate each functionality for clarity.

🔗 Backend API Endpoints
Users

GET /users/ → List all users

POST /users/ → Create a new user

PUT /users/{user_id} → Update an existing user (identified by user ID)

DELETE /users/{user_id} → Delete a user (identified by user ID)

POST /users/bulk → Bulk upload users from a CSV file

🖥️ Tabs Functionality
1. List Users
Displays all users in a table.

On Load Users:

Sends GET /users/.

Shows results in a table or a message if none found.

Displays error if backend returns non-200 status.

2. Create User
Inputs:

Username

Email

Phone Number

On Create:

Sends POST /users/ with parameters:

username, email, phone_number.

Displays backend response.

3. Update User
Inputs:

User ID (numeric field)

New Username

New Email

New Phone Number

On Update:

Sends PUT /users/{user_id} with parameters:

username, email, phone_number.

Displays backend response.

4. Delete User
Input: User ID to Delete (numeric field).

On Delete:

Sends DELETE /users/{user_id}.

Displays backend response.

5. Bulk Upload
File uploader (st.file_uploader) accepts CSV files.

On upload:

Sends POST /users/bulk with the file payload.

Displays backend response.

⚙️ Key Implementation Details
Tabs Separation: Each CRUD operation and bulk upload is placed in its own tab for clarity.

Dynamic Feedback: Uses st.table, st.write, st.success, and st.error to display backend responses.

Error Handling: Each API call checks status_code and displays appropriate messages.

Bulk Upload: Uses st.file_uploader and sends file contents via requests.post with files.
'''
import streamlit as st
import requests
a = "http://127.0.0.1:8000/admin"

API_URL = "http://127.0.0.1:8000/admin/user"  # FastAPI backend

st.title("Users Management Frontend")

# Tabs for each service
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "List Users", "Create User", "Update User", "Delete User", "Bulk Upload"
])

# List Users
with tab1:
    st.header("All Users")
    if st.button("Load Users"):
        response = requests.get(f"{API_URL}/users/")
        if response.status_code == 200:
            data = response.json()
            if data:
                st.table(data)
            else:
                st.write("No users found.")
        else:
            st.error(response.json())

# Create User
with tab2:
    st.header("Create a New User")
    username = st.text_input("Username")
    email = st.text_input("Email")
    phone_number = st.text_input("Phone Number")
    if st.button("Create"):
        response = requests.post(
            f"{API_URL}/users/",
            params={"username": username, "email": email, "phone_number": phone_number}
        )
        st.write(response.json())

# Update User
with tab3:
    st.header("Update Existing User")
    user_id = st.number_input("User ID", min_value=1, step=1)
    new_username = st.text_input("New Username")
    new_email = st.text_input("New Email")
    new_phone = st.text_input("New Phone Number")
    if st.button("Update"):
        response = requests.put(
            f"{API_URL}/users/{user_id}",
            params={"username": new_username, "email": new_email, "phone_number": new_phone}
        )
        st.write(response.json())

# Delete User
with tab4:
    st.header("Delete User")
    user_id = st.number_input("User ID to Delete", min_value=1, step=1)
    if st.button("Delete"):
        response = requests.delete(f"{API_URL}/users/{user_id}")
        st.write(response.json())

# Bulk Upload
with tab5:
    st.header("Bulk Upload Users (CSV)")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(f"{API_URL}/users/bulk", files=files)
        st.write(response.json())
