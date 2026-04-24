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