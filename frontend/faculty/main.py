'''Overview
This module defines the main entry point for the faculty dashboard in the Campus ERP system. Built with Streamlit, it provides a unified interface for faculty members to manage academic workflows such as student records, attendance, assignments, and MST exams. It integrates multiple submodules (a.py, aa.py, am.py, ass.py) into a single navigable application.

Key Components
🔹 Imports
streamlit as st → Provides UI components and layout management.

requests → Handles API calls to backend services.

pandas → Displays tabular data.

json → Parses API responses.

Local Modules → Imports faculty-specific modules (a, aa, am, ass) for modular functionality.

🔹 UI Structure
Page Configuration

Sets page title, layout, and sidebar navigation.

Provides a consistent look across faculty modules.

Sidebar Navigation  
Faculty can switch between different modules:

Students → Student management interface (a.py).

Attendance → Attendance management (aa.py).

MST Exams → Exam scheduling and marks entry (am.py).

Assignments → Assignment creation and marks entry (ass.py).

Dynamic Rendering  
Based on sidebar selection, the corresponding module is loaded and displayed in the main content area.

🔹 API Integration
Backend Endpoints  
The dashboard communicates with backend APIs for CRUD operations:

/students/ → Student records

/attendance/ → Attendance records

/mst-exams/ → MST exam details

/mst-exam-marks/ → Exam marks

/assignments/ → Assignment details and marks

Error Handling  
API calls are wrapped in try/except blocks to handle connection issues gracefully.

🔹 Utility Functions
load_module(module_name)  
Dynamically loads and executes the selected faculty module.

fetch_data(endpoint)  
Retrieves data from backend APIs.

post_data(endpoint, payload)  
Submits new records to backend.'''
import streamlit as st

# 1. Page Config
st.set_page_config(page_title="Campus Portal", page_icon="🎓", layout="wide")

# 2. Sidebar Navigation
with st.sidebar:
    st.title("🏫 Campus Portal")
    st.markdown("---")
    choice = st.radio(
        "Go to Module:",
        [
            "Assignments",
            "Assignment Marks",
            "Attendance",
            "MST Exam Creator",
            "MST Exam Marks",
            "Correction Requests"
        ]
    )
    st.info("Logged in as: Faculty Admin")

# 3. Function to run selected module
def run_module(choice: str):
    """Import and run the selected module UI."""
    if choice == "Assignments":
        import frontend.faculty.ass as ass
        ass.main()   # <-- call the module’s entry point

    elif choice == "Assignment Marks":
        import frontend.faculty.am as am
        am.main()

    elif choice == "Attendance":
        import frontend.faculty.aa as aa
        aa.main()

    elif choice == "MST Exam Creator":
        import frontend.faculty.me as me
        me.main()

    elif choice == "MST Exam Marks":
        import frontend.faculty.mem as mem
        mem.main()

    elif choice == "Correction Requests":
        import frontend.faculty.r as r
        r.main()

# 4. Main Content Area
main_container = st.container()
with main_container:
    run_module(choice)
