'''
📘 Documentation: College Management Streamlit App
Purpose
This Streamlit application provides a simple user interface for managing colleges in a database. It interacts with a FastAPI backend (http://127.0.0.1:8000/cg) to perform CRUD operations (Create, Read, Update, Delete).

Features
View Colleges

Fetches all colleges from GET /cg/colleges/.

Displays them in a table using st.table().

Handles empty results and error responses gracefully.

Create College

Inputs: College ID, College Name.

Sends a POST /cg/colleges/ request with the new college details.

Displays success or error messages depending on the response.

Update College

Fetches existing colleges (GET /cg/colleges/) for selection.

Uses college_name for dropdown display but keeps track of college_pk for backend updates.

Inputs: New College ID, New College Name.

Sends a PUT /cg/colleges/{college_pk} request with updated details.

Displays success or error messages.

Delete College

Fetches existing colleges (GET /cg/colleges/) for selection.

Uses college_name for dropdown display but keeps track of college_pk for backend deletion.

Sends a DELETE /cg/colleges/{college_pk} request.

Displays success or error messages.

API Endpoints Used
GET /cg/colleges/ → Retrieve all colleges.

POST /cg/colleges/ → Create a new college.

PUT /cg/colleges/{college_pk} → Update an existing college.

DELETE /cg/colleges/{college_pk} → Delete a college.
'''
import streamlit as st
import requests
a = "http://127.0.0.1:8000/admin"

API_URL = "http://127.0.0.1:8000/admin/cg"  # FastAPI backend

st.title("College Management")

tab1, tab2, tab3, tab4 = st.tabs(["View Colleges", "Create College", "Update College", "Delete College"])

# View Colleges
with tab1:
    st.header("All Colleges")
    if st.button("Load Colleges"):
        response = requests.get(f"{API_URL}/colleges/")
        if response.status_code == 200:
            data = response.json()
            if data:
                st.table(data)
            else:
                st.write("No colleges found.")
        else:
            st.error(response.json())

# Create College
with tab2:
    st.header("Create a New College")
    college_id = st.text_input("College ID")
    college_name = st.text_input("College Name")

    if st.button("Create College"):
        response = requests.post(
            f"{API_URL}/colleges/",
            params={"college_id": college_id, "college_name": college_name}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Update College
with tab3:
    st.header("Update College")

    # Fetch colleges for dropdown
    college_response = requests.get(f"{API_URL}/colleges/")
    college_options = []
    if college_response.status_code == 200:
        college_data = college_response.json()
        # Use college_name for selection, but keep PK for backend
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    selected_college = st.selectbox("Select College to Update", list(college_options.keys()))

    new_college_id = st.text_input("New College ID")
    new_college_name = st.text_input("New College Name")

    if st.button("Update College"):
        college_pk = college_options[selected_college]
        response = requests.put(
            f"{API_URL}/colleges/{college_pk}",
            params={"college_id": new_college_id, "college_name": new_college_name}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Delete College
with tab4:
    st.header("Delete College")

    # Fetch colleges for dropdown
    college_response = requests.get(f"{API_URL}/colleges/")
    college_options = []
    if college_response.status_code == 200:
        college_data = college_response.json()
        college_options = {c["college_name"]: c["college_pk"] for c in college_data}

    selected_college = st.selectbox("Select College to Delete", list(college_options.keys()))

    if st.button("Delete College"):
        college_pk = college_options[selected_college]
        response = requests.delete(f"{API_URL}/colleges/{college_pk}")
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())
