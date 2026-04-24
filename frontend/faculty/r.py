import streamlit as st
import requests

API_BASE = "http://localhost:8000/faculty/correction"

st.set_page_config(page_title="Campus Correction Requests", layout="centered")
st.title("✏️ Campus Correction Request System")

class CorrectionAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def submit_request(self, payload: dict):
        try:
            resp = requests.post(f"{self.base_url}/request", json=payload)
            return resp
        except Exception as e:
            st.error(f"⚠️ Connection Error: {e}")
            return None

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

    def get_service_types(self):
        return requests.get(f"{self.base_url}/service-types").json()

    def get_fields(self, service_type: str):
        return requests.get(f"{self.base_url}/fields/{service_type}").json()

    def get_rollnos(self):
        return requests.get(f"{self.base_url}/rollnos").json()

    def get_subjects(self, rollno: str, semester: int):
        return requests.get(
            f"{self.base_url}/subjects",
            params={"rollno": rollno, "semester": semester}
        ).json()

    def get_old_value(self, target_pk: int, service_type: str, field_name: str):
        return requests.get(
            f"{self.base_url}/old_value",
            params={"target_pk": target_pk, "service_type": service_type, "field_name": field_name}
        ).json().get("old_value", "")

    def get_target_pk(self, rollno: str, semester: int, subject_code: str, service_type: str):
        return requests.get(
            f"{self.base_url}/target_pk",
            params={"rollno": rollno, "semester": semester, "subject_code": subject_code, "service_type": service_type}
        ).json().get("target_pk", None)
    def get_email(self):
        try:
            resp = requests.get(f"{self.base_url}/email")
            resp.raise_for_status()
            return resp.json()  # returns a list of dicts
        except Exception as e:
            st.error(f"⚠️ Connection Error: {e}")
            return []

class CorrectionUI:
    def __init__(self, api_client: CorrectionAPI):
        self.api = api_client

    def run(self):
        tab1 ,= st.tabs(["Submit Request"])

        # --- Submit Request ---
        with tab1:
            st.subheader("Submit Correction Request")
            emails = self.api.get_email()
            email_options = [e["email"] for e in emails]
            email = st.selectbox("Your Email", email_options)

            # Step 1: Service Type
            service_types = self.api.get_service_types()
            service_type = st.selectbox("Service Type", service_types)

            # Step 2: Field Name (depends on service type)
            fields = self.api.get_fields(service_type) if service_type else []
            field_name = st.selectbox("Field to Correct", fields)

            # Step 3: Roll Number
            rollnos = self.api.get_rollnos()
            rollno = st.selectbox("Roll Number", rollnos)

            # Step 4: Semester
            semester = st.number_input("Semester", min_value=1, max_value=8, step=1)

            # Step 5: Subject (depends on rollno + semester)
            subjects = self.api.get_subjects(rollno, semester) if rollno and semester else []
            subject_choice = st.selectbox(
                "Subject",
                [f"{s['subject_code']} - {s['subject_name']}" for s in subjects]
            )
            subject_code, subject_name = subject_choice.split(" - ") if subject_choice else ("", "")

            # Resolve target_pk
            target_pk = self.api.get_target_pk(
                rollno, semester, subject_code, service_type
            ) if rollno and semester and subject_code and service_type else None

            # Fetch old value
            old_value = self.api.get_old_value(
                target_pk, service_type, field_name
            ) if target_pk and service_type and field_name else ""
            # Show old value in disabled text input
            st.text_input("old_value", value=str(old_value), disabled=True)

            # New value input adapts to field type
            if field_name in ["lectures_attended", "total_lectures", "marks"]:
                new_value = st.number_input("New Value", step=1)
            else:
                new_value = st.text_input("New Value")

            # Debug panel
            with st.expander("🔍 Debug Info"):
                st.json({
                    "email": email,
                    "service_type": service_type,
                    "field_name": field_name,
                    "rollno": rollno,
                    "semester": semester,
                    "subject_code": subject_code,
                    "subject_name": subject_name,
                    "old_value": old_value,
                    "new_value": new_value
                })

            if st.button("Submit Request"):
                payload = {
                    "email": email,
                    "service_type": service_type,
                    "field_name": field_name,
                    "old_value": str(old_value) if old_value else None,
                    "new_value": str(new_value) if new_value else None,
                    "rollno": rollno,
                    "subject_code": subject_code,
                    "subject_name": subject_name,
                    "semester": int(semester)
                }
                resp = self.api.submit_request(payload)
                if resp and resp.status_code == 200:
                    st.success("✅ Request submitted successfully")
                else:
                    st.error(f"❌ Error {resp.status_code}: {resp.text if resp else 'No response'}")
if __name__ == "__main__":
    api_client = CorrectionAPI(API_BASE)
    ui = CorrectionUI(api_client)
    ui.run()