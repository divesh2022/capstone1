'''Overview
This module defines the main entry point for the Student Dashboard in the Campus ERP system. Built with Streamlit, it integrates multiple student-specific modules (attendance, MST exams, assignments, corrections, etc.) into a unified interface. It acts as the frontend hub that allows students to manage their academic records and communicates with backend APIs.

Key Components
🔹 Imports
streamlit as st → Provides UI components and layout management.

requests → Handles API calls to backend services.

pandas → Displays tabular data for attendance, exams, and marks.

json → Parses API responses.

Local Modules → Imports student-specific modules (e.g., aa.py, am.py, ci.py) for modular functionality.

🔹 UI Structure
Page Configuration

Sets page title, layout, and sidebar navigation.

Provides a consistent look across student modules.

Sidebar Navigation  
Students can switch between different modules:

Attendance → View attendance records (aa.py).

MST Exams → View MST exam schedules and marks (am.py).

Corrections → Submit and track correction requests (ci.py).

Dynamic Rendering  
Based on sidebar selection, the corresponding module is loaded and displayed in the main content area.

🔹 API Integration
Backend Endpoints  
The dashboard communicates with backend APIs for CRUD operations:

/attendance/ → Attendance records

/mst-exams/ → MST exam schedules

/mst-exam-marks/ → MST exam marks

/corrections/ → Correction requests

Error Handling  
API calls are wrapped in try/except blocks to handle connection issues gracefully.

🔹 Utility Functions
load_module(module_name)  
Dynamically loads and executes the selected student module.

fetch_data(endpoint)  
Retrieves data from backend APIs.'''
import streamlit as st
import importlib

# 1. Page Config
st.set_page_config(page_title="Student Portal", page_icon="🎓", layout="wide")

# 2. Sidebar Navigation
choice = st.sidebar.selectbox(
    "Go to Module:",
    ["attendance", "assignment marks", "mst exam marks", "profile", "total marks"]
)

# 3. Module Mapping
modules = {
    "attendance": "frontend.student.aa",
    "assignment marks": "frontend.student.am",
    "mst exam marks": "frontend.student.mm",
    "profile": "frontend.student.profile",
    "total marks": "frontend.student.tm"
}

# 4. Function Wrapper
def run_selected_module(choice: str):
    """Import and run the selected student module safely."""
    if choice in modules:
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
