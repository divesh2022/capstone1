import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List
import pyodbc
from connect import get_connection   # reuse your working connection helper

router = APIRouter()

# ---------------------------
# Models
# ---------------------------
class AttendanceAggregateRecord(BaseModel):
    student_pk: int
    subject_pk: int
    semester: int
    faculty_pk: int
    lectures_attended: int
    total_lectures: int

class UpdateRecord(BaseModel):
    roll_no: str
    lectures_attended: int

# ---------------------------
# Helpers
# ---------------------------
def fetch_query(sql: str, params: tuple = ()):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

# ---------------------------
# Endpoints
# ---------------------------

@router.get("/departments")
def get_departments():
    return {"data": fetch_query("SELECT dept_id, dept_name FROM Department")}

@router.get("/subjects")
def get_subjects():
    return {"data": fetch_query("SELECT subject_pk, subject_code, subject_name FROM Subject")}

@router.get("/semesters")
def get_semesters():
    # simple static list for demo
    return {"data": [1, 2, 3, 4, 5, 6, 7, 8]}

@router.get("/records")
def get_records(subject_code: str = Query(...), semester: int = Query(...), dept_id: str = Query(...)):
    sql = """
        SELECT s.roll_no, agg.lectures_attended, agg.total_lectures
        FROM AttendanceAggregate agg
        JOIN Student s ON agg.student_pk = s.student_pk
        JOIN Subject subj ON agg.subject_pk = subj.subject_pk
        JOIN Department d ON s.dept_pk = d.dept_pk
        WHERE subj.subject_code = ? AND agg.semester = ? AND d.dept_id = ?
    """
    return {"data": fetch_query(sql, (subject_code, semester, dept_id))}

@router.post("/set_total_lectures")
def set_total_lectures(payload: dict):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE AttendanceAggregate
            SET total_lectures = ?
            WHERE subject_pk = (SELECT subject_pk FROM Subject WHERE subject_code = ?)
              AND semester = ?
              AND student_pk IN (SELECT student_pk FROM Student WHERE dept_pk = (SELECT dept_pk FROM Department WHERE dept_id = ?))
        """, payload["total_lectures"], payload["subject_code"], payload["semester"], payload["dept_id"])
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Total lectures updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {e}")

@router.post("/update_attendance")
def update_attendance(records: List[UpdateRecord]):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for rec in records:
            cursor.execute("""
                UPDATE AttendanceAggregate
                SET lectures_attended = ?
                WHERE student_pk = (SELECT student_pk FROM Student WHERE roll_no = ?)
            """, rec.lectures_attended, rec.roll_no)
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Attendance records updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk update failed: {e}")

# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    uvicorn.run("attendance_aggregate: router", host="127.0.0.1", port=8000, reload=True)
