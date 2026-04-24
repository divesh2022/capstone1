import streamlit as st
import importlib

# 1. Page Config
st.set_page_config(page_title="College Management System", page_icon="🎓", layout="wide")

# 2. Sidebar Navigation
st.sidebar.title("📚 Admin Management System")
choice = st.sidebar.selectbox(
    "Choose a Module",
    [
        "Faculty Management",
        "HOD Management",
        "Roles Management",
        "Student Management",
        "Subject Management",
        "UserRoles Management",
        "Users Management",
        "Admin Query Editor",
        "Branch Management",
        "College Management",
        "Course Management",
        "Department Management",
        "Semester Management"
    ]
)

# 3. Module Mapping
modules = {
    "Faculty Management": "frontend.admin.faculty",
    "HOD Management": "frontend.admin.hod",
    "Roles Management": "frontend.admin.role",
    "Student Management": "frontend.admin.student",
    "Subject Management": "frontend.admin.subject",
    "UserRoles Management": "frontend.admin.user_roles",
    "Users Management": "frontend.admin.users",
    "Admin Query Editor": "frontend.admin.query",
    "Branch Management": "frontend.admin.branch",
    "College Management": "frontend.admin.college",
    "Course Management": "frontend.admin.course",
    "Department Management": "frontend.admin.department",
    "Semester Management": "frontend.admin.semester"
}

# 4. Function Wrapper
def run_selected_module(choice: str):
    """Import and run the selected module safely."""
    if choice in modules:
        try:
            mod = importlib.import_module(modules[choice])
            if hasattr(mod, "main"):
                mod.main()   # <-- call the entry point
            else:
                st.error(f"⚠️ Module '{modules[choice]}' has no main() function. Please add def main(): inside it.")
        except Exception as e:
            st.error(f"⚠️ Could not load module '{modules[choice]}': {e}")

# 5. Execute
def main():
    run_selected_module(choice)
