from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import uvicorn
from connect import get_connection   # your DB connection helper

router = APIRouter()

# -------------------------------
# Models
class RequestCreate(BaseModel):
    email: str
    service_type: str   # 'mstmarks', 'assignment_marks', 'attendance'
    field_name: str
    old_value: str | None
    new_value: str
    rollno: str
    subject_code: str
    subject_name: str
    semester: int

class ReviewDecision(BaseModel):
    request_id: int
    hod_pk: int
    decision: str       # 'accept' or 'reject'
    reason: str | None

# -------------------------------
# Helpers

allowed_fields = {
    "attendance": {"lectures_attended", "total_lectures"},
    "mstmarks": {"marks"},
    "assignment_marks": {"marks"}
}

def resolve_target_pk(conn, req: RequestCreate):
    cursor = conn.cursor()
    if req.service_type == "attendance":
        cursor.execute("""
            SELECT aa.agg_pk
            FROM AttendanceAggregate aa
            JOIN Student s ON aa.student_pk = s.student_pk
            JOIN Subject subj ON aa.subject_pk = subj.subject_pk
            WHERE s.roll_no = ? AND subj.subject_code = ? AND subj.subject_name = ? AND aa.semester = ?
        """, (req.rollno, req.subject_code, req.subject_name, req.semester))
    elif req.service_type == "mstmarks":
        cursor.execute("""
            SELECT m.exam_marks_pk
            FROM MSTExamMarks m
            JOIN Student s ON m.student_pk = s.student_pk
            JOIN MSTExam e ON m.exam_pk = e.exam_pk
            JOIN Subject subj ON e.subject_pk = subj.subject_pk
            WHERE s.roll_no = ? AND subj.subject_code = ? AND subj.subject_name = ? AND e.semester = ?
        """, (req.rollno, req.subject_code, req.subject_name, req.semester))
    elif req.service_type == "assignment_marks":
        cursor.execute("""
            SELECT am.assignment_marks_pk
            FROM AssignmentMarks am
            JOIN Student s ON am.student_pk = s.student_pk
            JOIN Assignment a ON am.assignment_pk = a.assignment_pk
            JOIN Subject subj ON a.subject_pk = subj.subject_pk
            WHERE s.roll_no = ? AND subj.subject_code = ? AND subj.subject_name = ? AND a.semester = ?
        """, (req.rollno, req.subject_code, req.subject_name, req.semester))
    else:
        raise HTTPException(status_code=400, detail="Invalid service type")

    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Target record not found")
    return row[0]

# -------------------------------
# Endpoints

@router.post("/request")
def create_request(req: RequestCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Resolve user_pk from email
        cursor.execute("SELECT user_pk FROM Users WHERE email = ?", (req.email,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        user_pk = row[0]

        # Validate field_name
        if req.field_name not in allowed_fields[req.service_type]:
            raise HTTPException(status_code=400, detail="Invalid field for this service type")

        # Resolve target_pk
        target_pk = resolve_target_pk(conn, req)

        # Insert into Request
        cursor.execute("""
            INSERT INTO Request (user_pk, service_type, target_pk, field_name, old_value, new_value, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """, (user_pk, req.service_type, target_pk, req.field_name, req.old_value, req.new_value))
        conn.commit()
        return {"message": "Request submitted successfully"}
    finally:
        cursor.close()
        conn.close()

@router.get("/requests/pending")
def list_pending_requests():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Request WHERE status = 'pending'")
        rows = cursor.fetchall()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
    finally:
        cursor.close()
        conn.close()

@router.post("/review")
def review_request(decision: ReviewDecision):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Request WHERE request_id = ?", (decision.request_id,))
        req = cursor.fetchone()
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")

        request_id, user_pk, service_type, field_name, old_value, new_value, status, submitted_at, target_pk = req
        new_value1 = int(new_value) if isinstance(new_value, str) else str(new_value)

        if decision.decision == "accept":
            
            cursor.execute("INSERT INTO Accepted (request_id, hod_pk, reason) VALUES (?, ?, ?)",
                           (decision.request_id, decision.hod_pk, decision.reason))
            cursor.execute("UPDATE Request SET status = 'accepted' WHERE request_id = ?", (decision.request_id,))

            # Apply change
            if service_type == "attendance":
                cursor.execute(f"UPDATE AttendanceAggregate SET {field_name} = ? WHERE agg_pk = ?", (new_value1, target_pk))
            elif service_type == "mstmarks":
                cursor.execute(f"UPDATE MSTExamMarks SET {field_name} = ? WHERE exam_marks_pk = ?", (new_value1, target_pk))
            elif service_type == "assignment_marks":
                cursor.execute(f"UPDATE AssignmentMarks SET {field_name} = ? WHERE assignment_marks_pk = ?", (new_value1, target_pk))

            conn.commit()
            return {"message": "Request accepted and changes applied"}

        elif decision.decision == "reject":
            cursor.execute("INSERT INTO Rejected (request_id, hod_pk, reason) VALUES (?, ?, ?)",
                           (decision.request_id, decision.hod_pk, decision.reason))
            cursor.execute("UPDATE Request SET status = 'rejected' WHERE request_id = ?", (decision.request_id,))
            conn.commit()
            return {"message": "Request rejected"}

        else:
            raise HTTPException(status_code=400, detail="Invalid decision")
    finally:
        cursor.close()
        conn.close()

# -------------------------------
# Dropdown Endpoints for Frontend

@router.get("/service-types")
def get_service_types():
    return list(allowed_fields.keys())

@router.get("/fields/{service_type}")
def get_fields(service_type: str):
    if service_type not in allowed_fields:
        raise HTTPException(status_code=400, detail="Invalid service type")
    return list(allowed_fields[service_type])

@router.get("/rollnos")
def get_rollnos():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT roll_no FROM Student")
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

@router.get("/subjects")
def get_subjects(rollno: str, semester: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT subj.subject_code, subj.subject_name
            FROM Subject subj
            JOIN AttendanceAggregate aa ON subj.subject_pk = aa.subject_pk
            JOIN Student s ON aa.student_pk = s.student_pk
            WHERE s.roll_no = ? AND aa.semester = ?
        """, (rollno, semester))
        return [{"subject_code": row[0], "subject_name": row[1]} for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()
@router.get("/target_pk")
def get_target_pk(rollno: str, semester: int, subject_code: str, service_type: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if service_type == "attendance":
            cursor.execute("""
                SELECT aa.agg_pk
                FROM AttendanceAggregate aa
                JOIN Student s ON aa.student_pk = s.student_pk
                JOIN Subject subj ON aa.subject_pk = subj.subject_pk
                WHERE s.roll_no = ? AND subj.subject_code = ? AND aa.semester = ?
            """, (rollno, subject_code, semester))
        elif service_type == "mstmarks":
            cursor.execute("""
                SELECT m.exam_marks_pk
                FROM MSTExamMarks m
                JOIN Student s ON m.student_pk = s.student_pk
                JOIN MSTExam e ON m.exam_pk = e.exam_pk
                JOIN Subject subj ON e.subject_pk = subj.subject_pk
                WHERE s.roll_no = ? AND subj.subject_code = ? AND e.semester = ?
            """, (rollno, subject_code, semester))
        elif service_type == "assignment_marks":
            cursor.execute("""
                SELECT am.assignment_marks_pk
                FROM AssignmentMarks am
                JOIN Student s ON am.student_pk = s.student_pk
                JOIN Assignment a ON am.assignment_pk = a.assignment_pk
                JOIN Subject subj ON a.subject_pk = subj.subject_pk
                WHERE s.roll_no = ? AND subj.subject_code = ? AND a.semester = ?
            """, (rollno, subject_code, semester))
        else:
            raise HTTPException(status_code=400, detail="Invalid service type")

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Target record not found")
        return {"target_pk": row[0]}
    finally:
        cursor.close()
        conn.close()


@router.get("/old_value")
def get_old_value(target_pk: int, service_type: str, field_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if service_type == "attendance":
            cursor.execute(f"SELECT {field_name} FROM AttendanceAggregate WHERE agg_pk = ?", (target_pk,))
        elif service_type == "mstmarks":
            cursor.execute(f"SELECT {field_name} FROM MSTExamMarks WHERE exam_marks_pk = ?", (target_pk,))
        elif service_type == "assignment_marks":
            cursor.execute(f"SELECT {field_name} FROM AssignmentMarks WHERE assignment_marks_pk = ?", (target_pk,))
        else:
            raise HTTPException(status_code=400, detail="Invalid service type")

        row = cursor.fetchone()
        if not row or row[0] is None:
            return {"old_value": ""}
        return {"old_value": row[0]}
    finally:
        cursor.close()
        conn.close()

@router.get("/email")
def get_email():
    # This is a placeholder. In a real app, you'd get the email from the session or auth token.
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email FROM Users")
        rows = cursor.fetchall()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
    finally:
        cursor.close()
        conn.close()

# -------------------------------
# Main app
app = FastAPI(title="Campus ERP Correction Workflow", version="1.0.0")
app.include_router(router, prefix="/correction", tags=["Correction Requests"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
