'''
Overview
This module defines API endpoints for managing student attendance records in the college management system. It provides CRUD operations, supports bulk uploads, and ensures faculty can track and update attendance efficiently.

Key Components
🔹 Data Models
AttendanceRecord (Pydantic Model)  
Represents a student’s attendance entry.
Attributes:

student_pk: Primary key of the student

subject_pk: Primary key of the subject

faculty_pk: Faculty member recording attendance

date: Date of the lecture

status: Attendance status (e.g., Present/Absent)

AttendanceUpdate (Pydantic Model)  
Used for updating attendance records.
Attributes:

roll_no: Student roll number

date: Date of lecture

status: Updated attendance status

🔹 Endpoints
GET /students/ → get_students  
Fetches students by department primary key.

Parameters: dept_pk

Returns: List of students with student_pk and roll_no.

GET /subjects/ → get_subjects  
Retrieves subjects by department primary key.

POST /attendance/ → create_attendance  
Records attendance for a student in a subject.

PUT /attendance/ → update_attendance  
Updates an existing attendance record.

DELETE /attendance/ → delete_attendance  
Removes an attendance record.

POST /attendance/bulk-upload → bulk_upload_attendance  
Allows uploading multiple attendance records at once (e.g., via CSV/Excel).

🔹 Utility Functions
Database Connection  
Uses get_connection() from the connect module to establish and close database connections.

Error Handling  
Wraps queries in try/except blocks to ensure exceptions are caught and returned as HTTP errors.
'''
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
