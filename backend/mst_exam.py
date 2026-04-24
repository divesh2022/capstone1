'''
Overview
This module defines API endpoints for managing Mid-Semester Test (MST) exams in the college management system. It provides CRUD operations to create, update, delete, and list MST exams, ensuring proper linkage between courses, subjects, and faculty.

Key Components
🔹 Data Models
MSTExamCreate (Pydantic Model)  
Represents the structure for creating a new MST exam record.
Attributes:

course_pk: Primary key of the course

subject_pk: Primary key of the subject

faculty_pk: Faculty member conducting the exam

exam_date: Date of the exam

exam_type: Type of MST (e.g., MST-1, MST-2)

MSTExamUpdate (Pydantic Model)  
Used for updating existing MST exam records.
Attributes:

exam_id: Identifier of the MST exam record

exam_date: Updated exam date

exam_type: Updated exam type

🔹 Endpoints
GET /mst-exams/ → list_mst_exams  
Retrieves all MST exam records.

POST /mst-exams/ → create_mst_exam  
Adds a new MST exam record.

PUT /mst-exams/{id} → update_mst_exam  
Updates an existing MST exam record by ID.

DELETE /mst-exams/{id} → delete_mst_exam  
Removes an MST exam record.

🔹 Utility Functions
Database Connection  
Uses get_connection() from the connect module to establish and close database connections.

Error Handling  
Wraps queries in try/except blocks to ensure exceptions are caught and returned as HTTP errors.
'''
import uvicorn
from fastapi import FastAPI, HTTPException,APIRouter
from pydantic import BaseModel
from typing import Optional
from connect import get_connection 

router = APIRouter()

# ---------------------------
# Model
# ---------------------------
class MSTExamRecord(BaseModel):
    dept_pk: int
    subject_pk: int
    semester: int
    exam_date: str   # YYYY-MM-DD
    exam_pdf: Optional[str] = None
    total_marks: int
    exam_name: str   # 'MST-1' or 'MST-2'
    faculty_pk: int  

# ---------------------------
# Helpers
# ---------------------------
def fetch_query(sql: str, params: tuple = ()):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        # Handle cases where query returns rows
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            results = []
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

# ---------------------------
# Endpoints
# ---------------------------

@router.get("/hod/mst/departments")
def get_departments():
    # consistent format: {"data": [...]}
    return {"data": fetch_query("SELECT dept_pk, dept_id, dept_name FROM Department")}

@router.get("/hod/mst/subjects")
def get_subjects():
    # consistent format: {"data": [...]}
    return {"data": fetch_query("SELECT subject_pk, subject_code, subject_name FROM Subject")}

@router.get("/hod/mst/faculty/")
def list_faculties():
    # FIXED: Now uses fetch_query to return the list inside {"data": [...]}
    sql = "SELECT name, faculty_pk FROM Faculty"
    return {"data": fetch_query(sql)}

@router.post("/hod/mst/")
def insert_mst_exam(record: MSTExamRecord):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        insert_sql = """
            INSERT INTO MSTExam (dept_pk, subject_pk, semester, exam_date, exam_pdf, total_marks, exam_name, faculty_pk)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(
            insert_sql, 
            record.dept_pk, 
            record.subject_pk, 
            record.semester, 
            record.exam_date,
            record.exam_pdf, 
            record.total_marks, 
            record.exam_name, 
            record.faculty_pk
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "MST Exam record inserted successfully"}
    except Exception as e:
        # Better practice: print error to console for debugging
        print(f"Insert Error: {e}") 
        raise HTTPException(status_code=500, detail=f"Insert failed: {e}")

# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    uvicorn.run("mst_exam:app", host="127.0.0.1", port=8000, reload=True)
