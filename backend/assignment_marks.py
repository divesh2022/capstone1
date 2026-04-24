from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from connect import get_connection

router = APIRouter()

# --- Pydantic Models ---
class AssignmentMarkCreate(BaseModel):
    assignment_pk: int
    student_pk: int
    marks: int
    faculty_pk: int  # Track who entered the marks


# --- GET Endpoints ---

@router.get("/students/")
def get_students(dept_pk: int = Query(...)):
    """Fetch students by department primary key."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT student_pk, roll_no FROM Student WHERE dept_pk = ?"
        cursor.execute(query, (dept_pk,))
        rows = cursor.fetchall()
        return [{"student_pk": r[0], "roll_no": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/assignments-list/")
def get_assignments_list():
    """Fetch assignments joined with subject names for dropdowns (only unmarked)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
        SELECT a.assignment_pk, s.subject_name, a.dept_pk, a.semester, a.total_marks
        FROM Assignment a
        JOIN Subject s ON a.subject_pk = s.subject_pk
        WHERE a.status = 0
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [
            {
                "assignment_pk": r[0],
                "subject_name": r[1],
                "dept_pk": r[2],
                "semester": r[3],
                "total_marks": r[4],
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/faculty/")
def list_faculties():
    """List all faculties with their primary keys."""
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


# --- POST Endpoints ---

@router.post("/assignment-marks/")
def create_assignment_mark(entry: AssignmentMarkCreate):
    """Insert a single assignment mark record and mark assignment as completed."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        insert_query = """
        INSERT INTO AssignmentMarks (assignment_pk, student_pk, marks, faculty_pk, status)
        VALUES (?, ?, ?, ?, 1)
        """
        cursor.execute(insert_query, (entry.assignment_pk, entry.student_pk, entry.marks, entry.faculty_pk))
        conn.commit()

        # Update assignment status to marked
        cursor.execute("UPDATE Assignment SET status = 1 WHERE assignment_pk = ?", (entry.assignment_pk,))
        conn.commit()

        cursor.execute("SELECT @@IDENTITY")
        new_id = cursor.fetchone()[0]
        return {"assignment_marks_pk": int(new_id), "message": "Marks recorded successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/assignment-marks/bulk")
def bulk_insert_marks(marks_list: List[AssignmentMarkCreate]):
    """Bulk insert marks and update assignment status."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        data_to_insert = [
            (m.assignment_pk, m.student_pk, m.marks, m.faculty_pk, 1)  # status = 1
            for m in marks_list
        ]
        insert_query = """
        INSERT INTO AssignmentMarks (assignment_pk, student_pk, marks, faculty_pk, status)
        VALUES (?, ?, ?, ?, ?)
        """
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()

        # Update all related assignments to marked
        assignment_ids = list({m.assignment_pk for m in marks_list})
        cursor.executemany("UPDATE Assignment SET status = 1 WHERE assignment_pk = ?", [(aid,) for aid in assignment_ids])
        conn.commit()

        return {"message": f"Successfully inserted {len(data_to_insert)} records and updated assignments"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# --- Uvicorn Entry Point ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("assignment_marks:router", host="0.0.0.0", port=8000, reload=True)
