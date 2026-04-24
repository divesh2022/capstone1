import streamlit as st
import importlib
import requests

# --- 1. Page Config ---
st.set_page_config(page_title="Campus Connect Dashboard", page_icon="🎓", layout="wide")

# Backend URL - Update this if your FastAPI server runs elsewhere
BASE_URL = "http://localhost:8000/auth"

# --- 2. Authentication Logic ---

def fetch_login_options():
    """Fetch roles and emails from FastAPI for the dropdowns."""
    roles, emails = [], []
    try:
        # Fetch Roles
        role_res = requests.get(f"{BASE_URL}/roles")
        if role_res.status_code == 200:
            roles = [r['role_name'] for r in role_res.json()]
        
        # Fetch Emails
        email_res = requests.get(f"{BASE_URL}/emails") 
        if email_res.status_code == 200:
            emails = email_res.json()
    except Exception as e:
        st.error(f"📡 API Connection Error: {e}")
    return roles, emails

def login_screen():
    """Renders the login UI as a gatekeeper."""
    st.container()
    with st.columns([1, 2, 1])[1]:
        st.title("🔐 Campus Login")
        st.write("Select your identity to access the portal")
        
        roles, emails = fetch_login_options()
        
        with st.form("login_form"):
            selected_email = st.selectbox("Select Email ID", options=emails if emails else ["No emails found"])
            selected_role = st.selectbox("Select Role", options=roles if roles else ["No roles found"])
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Sign In"):
                if not password:
                    st.warning("Please enter your password.")
                else:
                    payload = {"email": selected_email, "password": password, "role_name": selected_role}
                    try:
                        response = requests.post(f"{BASE_URL}/login", json=payload)
                        if response.status_code == 200:
                            user_data = response.json()
                            st.session_state["authenticated"] = True
                            st.session_state["user_role"] = user_data["role_name"]
                            st.session_state["username"] = user_data["username"]
                            st.session_state["user_pk"] = user_data["user_pk"]
                            st.rerun()
                        else:
                            st.error("Invalid credentials or unauthorized role.")
                    except Exception as e:
                        st.error(f"Auth Service Error: {e}")

# Check Authentication Status
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_screen()
    st.stop() # Stop execution here so the dashboard doesn't load

# --- 3. Dashboard Logic (Only runs if authenticated) ---

# Logout button in sidebar
if st.sidebar.button("🚪 Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.title("📂 Campus Connect")
st.sidebar.info(f"👤 User: {st.session_state['username']}\n\n🔑 Role: {st.session_state['user_role']}")

# Restrict the portal choice to the user's assigned role
main_choice = st.sidebar.radio("Active Portal:", [st.session_state["user_role"].upper()])

# --- 4. Comprehensive Module Mapping ---
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
        "Requests": ["Correction Requests"]
    }
}

# --- 5. Sidebar second-level selection ---
sub_choice = None
if main_choice in services:
    st.sidebar.markdown("---")
    categories = services[main_choice]
    category_choice = st.sidebar.selectbox("Select Category:", list(categories.keys()))
    sub_choice = st.sidebar.selectbox("Select Service:", categories[category_choice])

# --- 6. Dispatcher function ---
def run_selected_module(main_portal: str, service_name: str):
    # Special Case: HOD Correction (OOP)
    if main_portal == "HOD" and service_name == "correction-requests":
        try:
            from frontend.hod import decision
            api = decision.CorrectionAPI("http://localhost:8000/faculty/correction")
            ui = decision.CorrectionUI(api)
            ui.run()
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
        return

    module_path = module_map.get(main_portal, {}).get(service_name)
    if module_path:
        try:
            state_key = f"last_loaded_{main_portal}_{service_name}"
            mod = importlib.import_module(module_path)
            if state_key in st.session_state:
                importlib.reload(mod)
            st.session_state[state_key] = True
        except Exception as e:
            st.error(f"⚠️ Error executing {service_name}: {e}")

# --- 7. Main Content Area Execution ---
if sub_choice:
    st.title(f"{sub_choice}")
    st.caption(f"Portal: {main_choice} | Category: {category_choice}")
    st.divider()
    run_selected_module(main_choice, sub_choice)
else:
    st.write(f"Welcome, {st.session_state['username']}. Please select a module to start.")