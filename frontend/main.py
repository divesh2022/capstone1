'''Overview
This module defines the main entry point for the Campus ERP system frontend. Built with Streamlit, it integrates dashboards for different user roles (Admin, HOD, Faculty, Student) into a unified interface. It acts as the central hub that provides role-based navigation and connects to backend APIs.

Key Components
🔹 Imports
streamlit as st → Provides UI components and layout management.

requests → Handles API calls to backend services.

pandas → Displays tabular data.

json → Parses API responses.

Local Modules → Imports role-specific dashboards (e.g., frontend/admin/main.py, frontend/hod/main.py, frontend/faculty/main.py, frontend/student/main.py).

🔹 UI Structure
Page Configuration

Sets page title, layout, and sidebar navigation.

Provides a consistent look across all role dashboards.

Sidebar Navigation  
Users can switch between dashboards based on their role:

Admin Dashboard → Manage institution-wide records.

HOD Dashboard → Manage departmental workflows.

Faculty Dashboard → Manage faculty-specific tasks.

Student Dashboard → Manage student-specific tasks.

Dynamic Rendering  
Based on sidebar selection, the corresponding role module is loaded and displayed in the main content area.

🔹 API Integration
Backend Endpoints  
The frontend communicates with backend APIs for CRUD operations across modules:

/faculty/ → Faculty records

/students/ → Student records

/courses/ → Course records

/branches/ → Branch records

/semesters/ → Semester records

/timetable/ → Timetable records

/decisions/ → Departmental decisions

/corrections/ → Correction requests

Error Handling  
API calls are wrapped in try/except blocks to handle connection issues gracefully.

🔹 Utility Functions
load_module(module_name)  
Dynamically loads and executes the selected role-specific module.

fetch_data(endpoint)  
Retrieves data from backend APIs.'''
import streamlit as st
import importlib

# 1. Page Config
st.set_page_config(page_title="Campus Connect Dashboard", page_icon="🎓", layout="wide")

# 2. Sidebar Navigation
st.sidebar.title("📂 Campus Connect Dashboard")
main_choice = st.sidebar.radio("Select Portal:", ["ADMIN", "HOD", "STUDENT", "FACULTY"])

# 3. Comprehensive Module Mapping
# This maps the UI display name to the actual python module path
module_map = {
    "ADMIN": {
        "Faculty Management": "frontend.admin.faculty",
        "HOD Management": "frontend.admin.hod",
        "Roles Management": "frontend.admin.role",
        "Student Management": "frontend.admin.student",
        "Subject Management": "frontend.admin.subject",
        "UserRoles Management": "frontend.admin.user_roles",
        "Users Management": "frontend.admin.user",
        "Admin Query Editor": "frontend.admin.query",
        "Branch Management": "frontend.admin.branch",
        "College Management": "frontend.admin.college",
        "Course Management": "frontend.admin.course",
        "Department Management": "frontend.admin.department",
        "Semester Management": "frontend.admin.semester"
    },
    "HOD": {
        "class-faculty": "frontend.hod.CF",
        "class-student": "frontend.hod.CS",
        "class-subjects": "frontend.hod.CSUB",
        "class-incharge": "frontend.hod.CI",
        "class-semesters": "frontend.hod.CSem",
        "faculty-subject": "frontend.hod.FS",
        "total-internal-marks": "frontend.hod.Tm",
        # "correction-requests" is handled as a special case in the dispatcher
    },
    "STUDENT": {
        "attendance": "frontend.student.aa",
        "assignment marks": "frontend.student.am",
        "mst exam marks": "frontend.student.mm",
        "total marks": "frontend.student.tm",
        "profile": "frontend.student.profile"
    },
    "FACULTY": {
        "Assignments": "frontend.faculty.ass",
        "Assignment Marks": "frontend.faculty.am",
        "Attendance": "frontend.faculty.aa",
        "MST Exam Creator": "frontend.faculty.me",
        "MST Exam Marks": "frontend.faculty.mem",
        "Correction Requests": "frontend.faculty.r"
    }
}

# Hierarchy for Sidebar UI
services = {
    "ADMIN": {
        "Management": ["Faculty Management", "HOD Management", "Roles Management", "Student Management", "Subject Management", "UserRoles Management", "Users Management"],
        "Setup": ["Branch Management", "College Management", "Course Management", "Department Management", "Semester Management"],
        "Tools": ["Admin Query Editor"]
    },
    "HOD": {
        "Class": ["class-faculty", "class-student", "class-subjects", "class-incharge", "class-semesters"],
        "Evaluation": ["correction-requests", "faculty-subject", "total-internal-marks"]
    },
    "STUDENT": {
        "Academics": ["attendance", "assignment marks", "mst exam marks", "total marks"],
        "Profile": ["profile"]
    },
    "FACULTY": {
        "Academics": ["Assignments", "Assignment Marks", "Attendance", "MST Exam Creator", "MST Exam Marks"],
        "Requests": ["Correction Requests", "detain"]
    }
}

# 4. Sidebar second-level selection
sub_choice = None
if main_choice in services:
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"{main_choice} Services")
    categories = services[main_choice]
    category_choice = st.sidebar.selectbox("Select Category:", list(categories.keys()))
    sub_choice = st.sidebar.selectbox("Select Service:", categories[category_choice])

# 5. Dispatcher function
# 5. Dispatcher function
def run_selected_module(main_portal: str, service_name: str):
    """Executes modules safely without double-loading or requiring main()."""
    
    # 1. Special Case: HOD Correction (OOP)
    if main_portal == "HOD" and service_name == "correction-requests":
        from frontend.hod import decision
        api = decision.CorrectionAPI("http://localhost:8000/faculty/correction")
        ui = decision.CorrectionUI(api)
        ui.run()
        return

    # 2. General Module Execution
    module_path = module_map.get(main_portal, {}).get(service_name)
    
    if module_path:
        try:
            # We check if this is a fresh selection to avoid redundant reloads
            # and ID collisions.
            state_key = f"last_loaded_{main_portal}_{service_name}"
            
            # Import the module (this runs it the first time)
            mod = importlib.import_module(module_path)
            
            # If it was already in memory from a previous selection, 
            # we reload it to ensure the UI actually renders.
            if state_key in st.session_state:
                importlib.reload(mod)
            
            # Mark this module as "active" in session state
            st.session_state[state_key] = True
            
        except Exception as e:
            st.error(f"⚠️ Error executing {service_name}: {e}")

# 3. Function to run selected module
def run_module(choice: str):
    """Import and run the selected module UI."""
    if choice == "Assignments":
        import frontend.faculty.ass as ass
        api = ass.AssignmentAPI("http://localhost:8000/faculty/assignment")
        ui = ass.AssignmentUI(api)  # <-- call the module’s entry point
        ui.run()
    elif choice == "Assignment Marks":
        import frontend.faculty.am as am
        api = am.APIClient("http://127.0.0.1:8000/faculty/assignment_marks")
        ui = am.MarksEntryUI(api)
        ui.run()

    elif choice == "Attendance":
        import frontend.faculty.aa as aa
        api = aa.AttendanceAPI("http://localhost:8000/faculty/attendance_aggregate")
        ui = aa.AttendanceUI(api)
        ui.run()

    elif choice == "MST Exam Creator":
        import frontend.faculty.me as me
        api = me.MSTExamAPI("http://127.0.0.1:8000/faculty/mst_exam")
        ui = me.MSTExamUI(api)
        ui.run()

    elif choice == "MST Exam Marks":
        import frontend.faculty.mem as mem
        api = mem.MSTExamMarksAPI("http://127.0.0.1:8000/faculty/mst_exam_marks")
        ui = mem.MSTExamMarksUI(api)
        ui.run()

    elif choice == "Correction Requests":
        import frontend.faculty.r as r
        api = r.CorrectionAPI("http://localhost:8000/faculty/correction")
        ui = r.CorrectionUI(api)
        ui.run()
    elif choice == "detain":
        import frontend.faculty.det as det
        det.show_attendance_ui()


# 6. Main Content Area Execution
if sub_choice:
    st.title(f"{sub_choice}")
    st.caption(f"Portal: {main_choice} | Category: {category_choice}")
    st.divider()
    if(main_choice == "FACULTY"):
        run_module(sub_choice)
    run_selected_module(main_choice, sub_choice)
    
else:
    st.write("Please select a service from the sidebar to begin.")
