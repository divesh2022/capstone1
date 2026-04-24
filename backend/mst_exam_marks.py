'''
Overview
This module defines API endpoints for managing marks obtained in Mid-Semester Tests (MSTs). It allows faculty to record, update, and retrieve exam marks for students, ensuring proper linkage between MST exams, subjects, and faculty.

Key Components
🔹 Data Models
MSTExamMarkCreate (Pydantic Model)  
Represents the structure for creating MST exam marks.
Attributes:

exam_pk: Primary key of the MST exam

student_pk: Primary key of the student

marks: Marks awarded

faculty_pk: Faculty member who entered the marks

MSTExamMarkUpdate (Pydantic Model)  
Used for updating existing MST exam marks.
Attributes:

exam_mark_id: Identifier of the MST exam mark record

marks: Updated marks

🔹 Endpoints
GET /students/ → get_students  
Fetches students by department primary key.

Parameters: dept_pk

Returns: List of students with student_pk and roll_no.

GET /mst-exams/ → get_mst_exams  
Retrieves a list of MST exams available in the system.

POST /mst-exam-marks/ → create_mst_exam_mark  
Records marks for a student in a specific MST exam.

PUT /mst-exam-marks/{id} → update_mst_exam_mark  
Updates an existing MST exam mark record by ID.

DELETE /mst-exam-marks/{id} → delete_mst_exam_mark  
Removes an MST exam mark record.

🔹 Utility Functions
Database Connection  
Uses get_connection() from the connect module to establish and close database connections.

Error Handling  
Wraps queries in try/except blocks to ensure exceptions are caught and returned as HTTP errors.
'''
import uvicorn
from fastapi import FastAPI, HTTPException, Query, APIRouter
from pydantic import BaseModel
from typing import List
from connect import get_connection

router = APIRouter()

# --- Pydantic Model ---
class ExamMarkRecord(BaseModel):
    exam_pk: int
    student_pk: int
    marks: int
    faculty_pk: int  # Track who entered the marks


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


# 1. Exams list (only unmarked exams)
@router.get("/exams")
def get_exams():
    sql = """
        SELECT e.exam_pk,
               e.dept_pk,
               e.subject_pk,
               d.dept_name,
               s.subject_code,
               s.subject_name,
               e.semester,
               e.exam_name,
               e.exam_date,
               e.total_marks
        FROM MSTExam e
        JOIN Department d ON e.dept_pk = d.dept_pk
        JOIN Subject s ON e.subject_pk = s.subject_pk
        WHERE e.status = 0
    """
    return {"data": fetch_query(sql)}


# 2. Students list (Filtered by Dept and Batch)
@router.get("/students")
def get_students(dept_pk: int = Query(...), batch: str = Query(...)):
    sql = """
        SELECT student_pk, roll_no, batch, dept_pk
        FROM Student
        WHERE dept_pk = ? AND batch = ?
    """
    return {"data": fetch_query(sql, (dept_pk, batch))}


# 3. Bulk insert marks (then mark exam as completed)
@router.post("/bulk_insert")
def bulk_insert_marks(records: List[ExamMarkRecord]):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        data_to_insert = [
            (rec.exam_pk, rec.student_pk, rec.marks, rec.faculty_pk)
            for rec in records
        ]

        sql = """
            INSERT INTO MSTExamMarks (exam_pk, student_pk, marks, faculty_pk)
            VALUES (?, ?, ?, ?)
        """
        cursor.executemany(sql, data_to_insert)
        conn.commit()

        # Update parent exam status to marked
        exam_ids = list({rec.exam_pk for rec in records})
        cursor.executemany("UPDATE MSTExam SET status = 1 WHERE exam_pk = ?", [(eid,) for eid in exam_ids])
        conn.commit()

        return {"message": f"{len(records)} MST marks inserted successfully and exams updated"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk insert failed: {e}")
    finally:
        cursor.close()
        conn.close()


# 4. Fetch existing marks
@router.get("/marks")
def get_marks(exam_pk: int = Query(...)):
    sql = """
        SELECT m.exam_pk,
               m.exam_name,
               subj.subject_name,
               s.roll_no,
               s.batch,
               mm.marks,
               f.name as faculty_name
        FROM MSTExam m
        JOIN MSTExamMarks mm ON mm.exam_pk = m.exam_pk
        JOIN Subject subj    ON m.subject_pk = subj.subject_pk
        JOIN Student s       ON mm.student_pk = s.student_pk
        LEFT JOIN Faculty f  ON mm.faculty_pk = f.faculty_pk
        WHERE m.exam_pk = ?
    """
    return {"data": fetch_query(sql, (exam_pk,))}


# 5. Faculties list
@router.get("/faculty/")
def list_faculties():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name, faculty_pk FROM Faculty")
        rows = cursor.fetchall()
        return [{"name": r[0], "faculty_pk": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# --- Uvicorn Entry Point ---
if __name__ == "__main__":
    uvicorn.run("mst_exam_marks:router", host="127.0.0.1", port=8000, reload=True)
