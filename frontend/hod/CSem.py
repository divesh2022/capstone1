import streamlit as st
import requests

# Backend URL
API_BASE_URL = "http://127.0.0.1:8000/hod"

st.set_page_config(page_title="Semester Management", layout="centered")

st.title("📅 Class Semester Management")
st.markdown("Use this portal to set or update the current academic semester for specific classes.")

# Create separate tabs
tab_set, tab_update = st.tabs(["🆕 Set Semester", "🔄 Promote Class"])

# --- Tab 1: Set Semester (POST) ---
with tab_set:
    st.header("Initialize Class Semester")
    st.info("Assign a starting semester to a specific batch and department.")
    
    with st.form("set_semester_form"):
        col1, col2 = st.columns(2)
        with col1:
            batch_name = st.text_input("Batch", placeholder="e.g., 2023-27")
            dept_name = st.text_input("Department", placeholder="e.g., Information Technology")
        with col2:
            sem_value = st.number_input("Current Semester", min_value=1, max_value=10, step=1)
        
        submitted = st.form_submit_button("Set Record", use_container_width=True)
        
        if submitted:
            # Matches ClassSemesterBase schema
            payload = {
                "batch": batch_name,
                "dept_name": dept_name,
                "semester": sem_value
            }
            try:
                res = requests.post(f"{API_BASE_URL}/class/semester", json=payload)
                if res.status_code == 200:
                    st.success(f"Confirmed: {batch_name} ({dept_name}) set to Semester {sem_value}")
                else:
                    st.error(f"Failed: {res.json().get('detail', 'Check if Batch/Dept exists')}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- Tab 2: Promote Class (PUT) ---
with tab_update:
    st.header("Update/Promote Semester")
    st.markdown("Find an existing class record and update its semester value.")

    with st.form("update_semester_form"):
        # Section to find the record
        st.subheader("1. Identify Existing Record")
        c1, c2, c3 = st.columns(3)
        with c1:
            u_batch = st.text_input("Batch", key="u_batch")
        with c2:
            u_dept = st.text_input("Department", key="u_dept")
        with c3:
            u_old_sem = st.number_input("Old Semester", min_value=1, key="u_old")

        st.divider()
        
        # Section for new data
        st.subheader("2. New Semester Value")
        u_new_sem = st.number_input("Update to Semester", min_value=1, key="u_new")
        
        update_submitted = st.form_submit_button("Promote Class", use_container_width=True)
        
        if update_submitted:
            # Query parameters for identification
            params = {
                "batch": u_batch,
                "dept_name": u_dept,
                "old_semester": u_old_sem
            }
            # JSON body for the change (ClassSemesterUpdate)
            payload = {"new_semester": u_new_sem}
            
            try:
                res = requests.put(
                    f"{API_BASE_URL}/class/semester/update", 
                    params=params, 
                    json=payload
                )
                if res.status_code == 200:
                    st.balloons()
                    st.success(f"Class {u_batch} successfully promoted to Semester {u_new_sem}!")
                else:
                    st.error(f"Update failed: {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Connection Error: {e}")