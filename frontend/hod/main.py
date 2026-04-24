'''Overview
This module defines the main entry point for the Head of Department (HOD) dashboard in the Campus ERP system. Built with Streamlit, it integrates multiple HOD-specific modules (faculty, courses, branches, subjects, semesters, timetable, decisions, corrections, etc.) into a unified interface. It acts as the frontend hub that allows HODs to manage departmental workflows and communicates with backend APIs.

Key Components
🔹 Imports
streamlit as st → Provides UI components and layout management.

requests → Handles API calls to backend services.

pandas → Displays tabular data.

json → Parses API responses.

Local Modules → Imports HOD-specific modules (e.g., CF.py, CS.py, CSUB.py, CSem.py, Ci.py, FS.py, Tm.py, decision.py) for modular functionality.

🔹 UI Structure
Page Configuration

Sets page title, layout, and sidebar navigation.

Provides a consistent look across HOD modules.

Sidebar Navigation  
HODs can switch between different modules:

Faculty Management → Manage faculty records and assignments (CF.py).

Course Management → Manage courses (CS.py).

Branch Management → Manage branches (CSUB.py).

Semester Management → Manage semester records (CSem.py).

Corrections → Review and approve correction requests (Ci.py).

Faculty–Student Management → Link faculty with students (FS.py).

Timetable Management → Create and update timetables (Tm.py).

Decisions → Record and review departmental decisions (decision.py).

Dynamic Rendering  
Based on sidebar selection, the corresponding module is loaded and displayed in the main content area.

🔹 API Integration
Backend Endpoints  
The dashboard communicates with backend APIs for CRUD operations:

/faculty/ → Faculty records

/courses/ → Course records

/branches/ → Branch records

/semesters/ → Semester records

/subjects/ → Subject records

/timetable/ → Timetable records

/decisions/ → Departmental decisions

/corrections/ → Correction requests

Error Handling  
API calls are wrapped in try/except blocks to handle connection issues gracefully.

🔹 Utility Functions
load_module(module_name)  
Dynamically loads and executes the selected HOD module.

fetch_data(endpoint)  
Retrieves data from backend APIs.

post_data(endpoint, payload)  
Submits new records to backend.'''
import streamlit as st
import importlib
from frontend.hod import decision

# 1. Page Config
st.set_page_config(page_title="HOD Portal", page_icon="📘", layout="wide")

# 2. Sidebar Navigation
choice = st.sidebar.selectbox(
    "Go to Module:",
    [
        "class-faculty",
        "class-student",
        "class-subjects",
        "class-incharge",
        "class-semesters",
        "correction-requests",
        "faculty-subject",
        "total-internal-marks"
    ]
)

# 3. Module Mapping
modules = {
    "class-faculty": "frontend.hod.CF",
    "class-student": "frontend.hod.CS",
    "class-subjects": "frontend.hod.CSUB",
    "class-incharge": "frontend.hod.CI",
    "class-semesters": "frontend.hod.CSem",
    "faculty-subject": "frontend.hod.FS",
    "total-internal-marks": "frontend.hod.Tm",
}

# 4. Function Wrapper
def run_selected_module(choice: str):
    if choice == "correction-requests":
        # Correction Requests module has its own UI class
        api = decision.CorrectionAPI("http://localhost:8000/faculty/correction")
        ui = decision.CorrectionUI(api)
        ui.run()
    elif choice in modules:
        try:
            mod = importlib.import_module(modules[choice])
            if hasattr(mod, "main"):
                mod.main()   # <-- call the module’s entry point
            else:
                st.error(f"⚠️ Module '{modules[choice]}' has no main() function. Please add def main(): inside it.")
        except Exception as e:
            st.error(f"⚠️ Could not load {choice}: {e}")

# 5. Execute
run_selected_module(choice)
