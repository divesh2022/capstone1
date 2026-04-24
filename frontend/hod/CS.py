import streamlit as st
import requests
import pandas as pd
import io

# backend configuration
API_BASE_URL = "http://127.0.0.1:8000/hod"

st.set_page_config(page_title="Student Allocation Manager", layout="wide")

st.title("🎓 Student Class Allocation Portal")
st.markdown("Manage student-to-class mappings for each semester.")

# create separate tabs for each operation
tab1, tab2, tab3 = st.tabs([
    "📍 Single Allocation", 
    "📁 Bulk CSV Upload", 
    "⚙️ Manage & Delete"
])

# --- Tab 1: Single Allocation ---
with tab1:
    st.header("Assign Student to Class")
    with st.form("student_single_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            roll_no = st.text_input("Roll Number", placeholder="e.g., 2021CS101")
            dept_name = st.text_input("Department Name", placeholder="e.g., Computer Science")
        
        with col2:
            batch = st.text_input("Batch", placeholder="e.g., 2021-25")
            semester = st.number_input("Semester", min_value=1, max_value=8, step=1)
            
        submitted = st.form_submit_button("Allocate Student", use_container_width=True)
        
        if submitted:
            payload = {
                "roll_no": roll_no,
                "batch": batch,
                "dept_name": dept_name,
                "semester": semester
            }
            try:
                res = requests.post(f"{API_BASE_URL}/class-students/allocate", json=payload)
                if res.status_code == 200:
                    st.success(f"Success: Roll No {roll_no} allocated to {batch} class.")
                else:
                    st.error(f"Error: {res.json().get('detail', 'Failed to allocate')}")
            except Exception as e:
                st.error(f"Connection failed: {e}")

# --- Tab 2: Bulk CSV Upload ---
with tab2:
    st.header("Batch Student Import")
    st.markdown("""
    **Instructions:** Upload a CSV file with the following exact headers:
    `roll_no`, `batch`, `dept_name`, `semester`
    """)
    
    uploaded_file = st.file_uploader("Choose Student CSV", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("🚀 Process Bulk Allocation", use_container_width=True):
            # reset pointer to start of file
            uploaded_file.seek(0)
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            
            try:
                res = requests.post(f"{API_BASE_URL}/class-students/upload-csv", files=files)
                if res.status_code == 200:
                    st.success("✅ Bulk allocation processed successfully!")
                else:
                    st.error(f"Error: {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Connection failed: {e}")

# --- Tab 3: Manage & Delete ---
with tab3:
    st.header("Remove Student Allocation")
    st.warning("Warning: This action will permanently remove the student from the specified class for that semester.")
    
    with st.expander("Show Deletion Form"):
        del_roll = st.text_input("Roll Number to Remove")
        del_batch = st.text_input("Batch Associated")
        del_dept = st.text_input("Department Associated")
        del_sem = st.number_input("Semester to Remove", min_value=1, key="del_sem_input")
        
        if st.button("Confirm Deletion", type="primary"):
            params = {
                "roll_no": del_roll,
                "batch": del_batch,
                "dept_name": del_dept,
                "semester": del_sem
            }
            try:
                # requests.delete uses params for query strings
                res = requests.delete(f"{API_BASE_URL}/class-students/delete", params=params)
                if res.status_code == 200:
                    st.toast(f"Allocation for {del_roll} removed!", icon="🗑️")
                    st.success("Record deleted successfully.")
                else:
                    st.error("Could not find or delete the record. Please check details.")
            except Exception as e:
                st.error(f"Connection failed: {e}")