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
