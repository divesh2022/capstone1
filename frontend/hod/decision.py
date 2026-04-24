'''Overview
This module defines the Head of Department (HOD) dashboard for decision management in the Campus ERP system. Built with Streamlit, it provides HODs with tools to record, update, and review departmental decisions related to faculty, students, courses, and administration. It acts as the frontend layer that communicates with backend APIs for decision workflows.

Key Components
🔹 Imports
streamlit as st → Provides UI components (tabs, forms, tables).

requests → Handles API calls to backend endpoints.

pandas → Displays tabular decision data.

json → Parses API responses.

🔹 UI Structure
Tabs  
The dashboard is organized into multiple tabs for modular functionality:

View Decisions → Displays all decisions recorded by the HOD.

Add Decision → Allows HODs to create new decision records.

Update Decision → Provides interface to modify existing decisions.

Delete Decision → Enables removal of decision records.

Forms  
Each tab contains forms for data entry (decision title, description, department ID, date).

Tables  
Decision records are displayed in tabular format using Pandas DataFrames for easy review.

🔹 API Integration
Backend Endpoints  
The frontend interacts with backend modules via REST APIs:

/decisions/ → Manage decision records

/department/ → Link decisions to departments

/faculty/ → Associate decisions with faculty members

Error Handling  
API calls are wrapped in try/except blocks to handle connection errors gracefully.

🔹 Utility Functions
fetch_data(endpoint)  
Retrieves decision data from backend APIs.

post_data(endpoint, payload)  
Submits new decision records to backend.

update_data(endpoint, payload)  
Updates existing decision records.

delete_data(endpoint, id)  
Removes decision records when required.'''
import streamlit as st
import requests

API_BASE = "http://localhost:8000/faculty/correction"

st.set_page_config(page_title="Campus Correction Requests", layout="centered")
st.title("✏️ Campus Correction Request System")

class CorrectionAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def list_pending(self):
        try:
            resp = requests.get(f"{self.base_url}/requests/pending")
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return []

    def review(self, payload: dict):
        try:
            resp = requests.post(f"{self.base_url}/review", json=payload)
            return resp
        except Exception as e:
            st.error(f"⚠️ Connection Error: {e}")
            return None


class CorrectionUI:
    def __init__(self, api_client: CorrectionAPI):
        self.api = api_client

    def run(self):
        tab2, = st.tabs(["HoD Review"])

        # --- HoD Review ---
        with tab2:
            st.subheader("HoD Review Panel")
            pending = self.api.list_pending()
            if not pending:
                st.info("No pending requests.")
            else:
                for req in pending:
                    with st.expander(f"Request #{req['request_id']} - {req['service_type']}"):
                        st.write(f"📧 Submitted by User ID: {req['user_pk']}")
                        st.write(f"📝 Service Type: {req['service_type']}")
                        st.write(f"🔑 Field: {req['field_name']}")
                        st.write(f"📊 Old Value: {req['old_value']}")
                        st.write(f"📊 New Value: {req['new_value']}")
                        st.write(f"🎓 Roll No: {req.get('rollno', 'N/A')}")
                        st.write(f"📘 Subject: {req.get('subject_code', '')} - {req.get('subject_name', '')}")
                        st.write(f"📅 Semester: {req.get('semester', 'N/A')}")
                        st.write(f"⏱ Submitted At: {req['submitted_at']}")

                        decision = st.radio(
                            f"Decision for Request {req['request_id']}",
                            ["accept", "reject"],
                            key=f"decision_{req['request_id']}"
                        )
                        reason = st.text_area(
                            f"Reason (Request {req['request_id']})",
                            key=f"reason_{req['request_id']}"
                        )
                        hod_pk = st.number_input(
                            f"HoD PK (Request {req['request_id']})",
                            min_value=1,
                            step=1,
                            key=f"hod_{req['request_id']}"
                        )

                        # Debug panel for HoD decision
                        with st.expander(f"🔍 Debug Info for Request {req['request_id']}"):
                            st.json({
                                "request_id": req["request_id"],
                                "hod_pk": hod_pk,
                                "decision": decision,
                                "reason": reason
                            })

                        if st.button(f"Submit Decision {req['request_id']}"):
                            payload = {
                                "request_id": req["request_id"],
                                "hod_pk": hod_pk,
                                "decision": decision,
                                "reason": reason
                            }
                            resp = self.api.review(payload)
                            if resp and resp.status_code == 200:
                                st.success(resp.json()["message"])
                            else:
                                st.error(f"❌ Error {resp.status_code}: {resp.text if resp else 'No response'}")


if __name__ == "__main__":
    api_client = CorrectionAPI(API_BASE)
    ui = CorrectionUI(api_client)
    ui.run()
