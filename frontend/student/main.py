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
