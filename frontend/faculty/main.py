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
