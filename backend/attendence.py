import uvicorn
from fastapi import FastAPI, HTTPException,APIRouter
from pydantic import BaseModel
import pyodbc
from connect import get_connection   # <-- import your connection helper

router = APIRouter()

# ---------------------------
# Models
# ---------------------------
class AttendanceRecord(BaseModel):
    class_pk: int
    subject_pk: int
    faculty_pk: int
    student_pk: int
    date: str   # YYYY-MM-DD
    status: bool

# ---------------------------
# Helpers
# ---------------------------
def fetch_query(sql: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

# ---------------------------
# Endpoints
# ---------------------------
@router.get("/classes")
def get_classes():
    return {"data": fetch_query("SELECT class_pk, batch, dept_pk FROM Class")}

@router.get("/subjects")
def get_subjects():
    return {"data": fetch_query("SELECT subject_pk, subject_code, subject_name FROM Subject")}

@router.get("/faculty")
def get_faculty():
    return {"data": fetch_query("SELECT faculty_pk, name, designation FROM Faculty")}

@router.get("/students")
def get_students():
    return {"data": fetch_query("SELECT student_pk, roll_no, batch FROM Student")}

@router.post("/attendance/")
def insert_attendance(record: AttendanceRecord):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Attendance (class_pk, subject_pk, faculty_pk, student_pk, date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, record.class_pk, record.subject_pk, record.faculty_pk, record.student_pk, record.date, record.status)
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Attendance record inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insert failed: {e}")

# --------------------------- 
# Entry point
# ---------------------------
if __name__ == "__main__":
    uvicorn.run("attendence: router", host="127.0.0.1", port=8000, reload=True)
