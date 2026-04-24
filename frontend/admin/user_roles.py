'''
UserRoles Management App Documentation
Overview
This Streamlit application provides a frontend interface for managing User-Role mappings in a system. It interacts with a FastAPI backend (http://127.0.0.1:8000/UR) to perform CRUD (Create, Read, Update, Delete) operations on user-role assignments. Users and roles are fetched dynamically from related endpoints to ensure consistency.

🔗 Backend API Endpoints
Users

GET /users/list → Fetch all users (returns user_pk, email)

Roles

GET /roles/list → Fetch all roles (returns role_pk, role_name)

UserRoles

GET /userroles/view → View all user-role mappings

POST /userroles/ → Insert a new user-role mapping

PUT /userroles/{user_pk}/{role_pk} → Update user-role assignment (e.g., password hash)

DELETE /userroles/{user_pk}/{role_pk} → Delete a user-role mapping

🖥️ Tabs Functionality
1. View UserRoles
Displays all user-role mappings in a table.

On Load UserRoles:

Sends GET /userroles/view.

Shows results in a table or a message if none found.

Displays error if backend returns non-200 status.

2. Insert UserRole
Dropdown to select user by email (mapped to user_pk).

Dropdown to select role by name (mapped to role_pk).

On Insert UserRole:

Sends POST /userroles/ with parameters:

user_pk, role_pk.

Displays success or error message.

3. Update UserRole
Dropdown to select user by email (mapped to user_pk).

Dropdown to select role by name (mapped to role_pk).

Input: New Password Hash.

On Update UserRole:

Sends PUT /userroles/{user_pk}/{role_pk} with parameter:

password_hash.

Displays success or error message.

4. Delete UserRole
Dropdown to select user by email (mapped to user_pk).

Dropdown to select role by name (mapped to role_pk).

On Delete UserRole:

Sends DELETE /userroles/{user_pk}/{role_pk}.


'''
import streamlit as st
import requests
a = "http://127.0.0.1:8000/admin"
API_URL = "http://127.0.0.1:8000/admin/UR"  # FastAPI backend

st.title("UserRoles Management Frontend")

# Tabs for each service
tab1, tab2, tab3, tab4 = st.tabs([
    "View UserRoles", "Insert UserRole", "Update UserRole", "Delete UserRole"
])

# View UserRoles
with tab1:
    st.header("All UserRoles (User, Role)")
    if st.button("Load UserRoles"):
        response = requests.get(f"{API_URL}/userroles/view")
        if response.status_code == 200:
            data = response.json().get("user_roles", [])
            if data:
                st.table(data)
            else:
                st.write("No user-role mappings found.")
        else:
            st.error(response.json())

with tab2:
    st.header("Insert a New UserRole")

    # Fetch users and roles
    users_resp = requests.get(f"{API_URL}/users/list")
    roles_resp = requests.get(f"{API_URL}/roles/list")

    if users_resp.status_code == 200 and roles_resp.status_code == 200:
        users = users_resp.json()
        roles = roles_resp.json()

        # Map user_pk → email
        user_options = {u["email"]: u["user_pk"] for u in users}
        selected_email = st.selectbox("Select User (by email)", list(user_options.keys()))
        user_pk = user_options[selected_email]

        # Map role_pk → role_name
        role_options = {r["role_name"]: r["role_pk"] for r in roles}
        selected_role = st.selectbox("Select Role", list(role_options.keys()))
        role_pk = role_options[selected_role]

        if st.button("Insert UserRole"):
            response = requests.post(
                f"{API_URL}/userroles/",
                params={"user_pk": user_pk, "role_pk": role_pk}
            )
            try:
                st.success(response.json())
            except Exception:
                st.error(response.text)
    else:
        st.error("Failed to load users or roles")

# Update UserRole (Tab 3)
with tab3:
    st.header("Update UserRole Password")

    users_resp = requests.get(f"{API_URL}/users/list")
    roles_resp = requests.get(f"{API_URL}/roles/list")

    if users_resp.status_code == 200 and roles_resp.status_code == 200:
        users = users_resp.json()
        roles = roles_resp.json()

        user_options = {u["email"]: u["user_pk"] for u in users}
        selected_email = st.selectbox(
            "Select User (by email)", list(user_options.keys()), key="update_user_email"
        )
        user_pk = user_options[selected_email]

        role_options = {r["role_name"]: r["role_pk"] for r in roles}
        selected_role = st.selectbox(
            "Select Role", list(role_options.keys()), key="update_user_role"
        )
        role_pk = role_options[selected_role]

        new_password = st.text_input("New Password Hash", key="update_password")

        if st.button("Update UserRole", key="update_button"):
            response = requests.put(
                f"{API_URL}/userroles/{user_pk}/{role_pk}",
                params={"password_hash": new_password}
            )
            try:
                st.success(response.json())
            except Exception:
                st.error(response.text)
    else:
        st.error("Failed to load users or roles")


# Delete UserRole (Tab 4)
with tab4:
    st.header("Delete UserRole")

    users_resp = requests.get(f"{API_URL}/users/list")
    roles_resp = requests.get(f"{API_URL}/roles/list")

    if users_resp.status_code == 200 and roles_resp.status_code == 200:
        users = users_resp.json()
        roles = roles_resp.json()

        user_options = {u["email"]: u["user_pk"] for u in users}
        selected_email = st.selectbox(
            "Select User (by email)", list(user_options.keys()), key="delete_user_email"
        )
        user_pk = user_options[selected_email]

        role_options = {r["role_name"]: r["role_pk"] for r in roles}
        selected_role = st.selectbox(
            "Select Role", list(role_options.keys()), key="delete_user_role"
        )
        role_pk = role_options[selected_role]

        if st.button("Delete UserRole", key="delete_button"):
            response = requests.delete(f"{API_URL}/userroles/{user_pk}/{role_pk}")
            try:
                st.success(response.json())
            except Exception:
                st.error(response.text)
    else:
        st.error("Failed to load users or roles")


