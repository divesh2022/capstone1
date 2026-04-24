import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/hod"  # FastAPI backend

st.title("Class–Faculty Allocation Handling")

tab1, tab2, tab3, tab4 = st.tabs(["View Allocations", "Create Allocation", "Update Allocation", "Delete Allocation"])

# View Allocations
with tab1:
    st.header("All Class–Faculty Allocations")
    if st.button("Load Allocations"):
        response = requests.get(f"{API_URL}/class_incharge/")
        if response.status_code == 200:
            data = response.json()
            if data:
                st.table(data)
            else:
                st.write("No allocations found.")
        else:
            st.error(response.json())

# Create Allocation
with tab2:
    st.header("Assign Faculty to Class")

    # Fetch classes for dropdown
    class_response = requests.get(f"{API_URL}/classes/")
    class_options = []
    if class_response.status_code == 200:
        class_data = class_response.json()
        # Show "Batch - Department" in dropdown
        class_options = [f"{c['batch']} - {c['dept_name']}" for c in class_data]

    selected_class = st.selectbox("Select Class (Batch - Department)", class_options)

    # Split back into batch and dept_name
    batch, dept_name = (selected_class.split(" - ") if selected_class else ("", ""))

    # Fetch faculty for dropdown
    faculty_response = requests.get(f"{API_URL}/faculties/")
    faculty_options = []
    if faculty_response.status_code == 200:
        faculty_data = faculty_response.json()
        # Show "Name (Email)" in dropdown
        faculty_options = [f"{f['name']} ({f['email']})" for f in faculty_data]

    selected_faculty = st.selectbox("Select Faculty", faculty_options)
    faculty_email = selected_faculty.split("(")[-1].strip(")") if selected_faculty else ""

    semester = st.number_input("Semester", min_value=1, max_value=10, step=1)

    if st.button("Create Allocation"):
        response = requests.post(
            f"{API_URL}/class_incharge/",
            params={"batch": batch, "dept_name": dept_name, "faculty_email": faculty_email, "semester": semester}
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# --- Tab 3: Update Allocation ---
with tab3:
    st.header("Update Allocation")

    # Fetch existing allocations for dropdown
    alloc_response = requests.get(f"{API_URL}/class_incharge/")
    alloc_options = {}
    if alloc_response.status_code == 200:
        alloc_data = alloc_response.json()
        alloc_options = {
            f"{a['batch']} - {a['dept_name']} ({a['faculty_email']})": a["class_incharge_pk"]
            for a in alloc_data
        }

    selected_alloc = st.selectbox(
        "Select Allocation to Update",
        list(alloc_options.keys()),
        key="update_alloc_select"
    )

    # Inputs for new values
    new_batch = st.text_input("New Batch", key="update_batch")
    department_response = requests.get(f"{API_URL}/departments/")
    dept_options = []
    if department_response.status_code == 200:
        dept_data = department_response.json()
        dept_options = [d["dept_name"] for d in dept_data]
    new_dept_name = st.selectbox("Select New Department", dept_options, key="update_dept_select")

    # Fetch faculty for dropdown
    faculty_response = requests.get(f"{API_URL}/faculties/")
    faculty_options = []
    if faculty_response.status_code == 200:
        faculty_data = faculty_response.json()
        # Handle case where backend returns both name and email OR only email
        faculty_options = [
            f"{f.get('name', '')} ({f['email']})" if "name" in f else f["email"]
            for f in faculty_data
        ]

    selected_faculty = st.selectbox(
        "Select Faculty",
        faculty_options,
        key="update_faculty_select"
    )

    # Extract email cleanly
    if selected_faculty:
        if "(" in selected_faculty:
            new_faculty_email = selected_faculty.split("(")[-1].strip(")")
        else:
            new_faculty_email = selected_faculty
    else:
        new_faculty_email = ""

    new_semester = st.number_input("New Semester", min_value=1, max_value=10, step=1, key="update_semester")

    if st.button("Update Allocation", key="update_button"):
        response = requests.put(
            f"{API_URL}/class_incharge/{alloc_options[selected_alloc]}",
            params={
                "new_batch": new_batch,
                "new_dept_name": new_dept_name,
                "new_faculty_email": new_faculty_email,
                "new_semester": new_semester,
            },
        )
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())

# Delete Allocation
with tab4:
    st.header("Delete Allocation")

    # Fetch allocations for dropdown
    alloc_response = requests.get(f"{API_URL}/class_incharge/")
    alloc_options = {}
    if alloc_response.status_code == 200:
        alloc_data = alloc_response.json()
        alloc_options = {f"{a['batch']} - {a['dept_name']} ({a['faculty_email']})": a["class_incharge_pk"] for a in alloc_data}

    selected_alloc = st.selectbox("Select Allocation to Delete", list(alloc_options.keys()))

    if st.button("Delete Allocation"):
        response = requests.delete(f"{API_URL}/class_incharge/{alloc_options[selected_alloc]}")
        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(response.json())
