'''
Overview
This module defines the backend API endpoints for managing assignments within the college management system. It provides CRUD operations (Create, Read, Update, Delete) and supports bulk uploads, ensuring assignments can be efficiently handled by faculty and administrators.

Key Components
🔹 Assignment Management
list_assignments  
Retrieves all assignments stored in the system. Useful for faculty or students to view available assignments.

create_assignment  
Adds a new assignment record. Typically requires details such as title, description, course/subject linkage, and due date.

update_assignment  
Modifies an existing assignment’s details (e.g., updating deadlines or instructions).

delete_assignment  
Removes an assignment from the system.

bulk_upload_assignments  
Allows uploading multiple assignments at once, often via CSV/Excel files.

Data Models
Assignment  
Represents an assignment entity with attributes like:

assignment_id (primary key)

title

description

course_id / subject_id

due_date

AssignmentUpdate  
Used for partial updates to assignment details.

Utility Functions
health_check  
Confirms the assignment service is running properly.

run_query / fetch_query  
Internal helpers for executing and retrieving database queries.
'''
from fastapi import FastAPI, HTTPException,APIRouter
from pydantic import BaseModel
import uvicorn
# Ensure connect.py is in the same directory
from connect import get_connection 

router = APIRouter()

# Pydantic model for request validation
class AssignmentCreate(BaseModel):
    dept_pk: int
    subject_pk: int
    semester: int
    assignment_pdf: str
    total_marks: int
    faculty_pk: int  # Added faculty_pk to the model

@router.get("/departments/")
def list_departments():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # FIX: Added dept_pk to the SELECT statement (Index 2)
        cursor.execute("SELECT dept_id, dept_name, dept_pk FROM Department")
        rows = cursor.fetchall()
        return [{"dept_id": r[0], "dept_name": r[1], "dept_pk": r[2]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/subjects/")
def list_subjects():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # FIX: Added subject_pk to the SELECT statement (Index 2)
        cursor.execute("SELECT subject_code, subject_name, subject_pk FROM Subject")
        rows = cursor.fetchall()
        return [{"subject_code": r[0], "subject_name": r[1], "subject_pk": r[2]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/faculty/")
def list_faculties():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # FIX: Added faculty_pk to the SELECT statement (Index 2)
        cursor.execute("SELECT  name, faculty_pk FROM Faculty")
        rows = cursor.fetchall()
        return [{"name": r[0], "faculty_pk": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/assignments/")
def create_assignment(assignment: AssignmentCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        insert_query = """
        INSERT INTO Assignment (dept_pk, subject_pk, semester, assignment_pdf, total_marks, faculty_pk)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            insert_query,
            assignment.dept_pk,
            assignment.subject_pk,
            assignment.semester,
            assignment.assignment_pdf,
            assignment.total_marks,
            assignment.faculty_pk  # Include faculty_pk in the insert
        )
        conn.commit()

        # Get the ID of the row just inserted
        cursor.execute("SELECT @@IDENTITY")
        new_id = cursor.fetchone()[0]

        return {"assignment_pk": int(new_id), "message": "Assignment inserted successfully"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    uvicorn.run("assignment: router", host="0.0.0.0", port=8000, reload=True)
