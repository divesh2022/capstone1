import uvicorn
from fastapi import FastAPI, HTTPException, APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from connect import get_connection

# ---------------------------
# Router
router = APIRouter()

# ---------------------------
# Model

# ---------------------------
# Helpers

# ---------------------------
# Endpoints
@router.get("/departments")
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

@router.get("/batches")
def get_batches():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT batch FROM BatchSemester ORDER BY batch")
        rows = cursor.fetchall()
        return {"data": [r[0] for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@router.get("/students")
def get_students(dept_pk: int = Query(...), batch: str = Query(...)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT roll_no FROM Student WHERE dept_pk = ? AND batch = ?", (dept_pk, batch))
        rows = cursor.fetchall()
        return {"data": [{"roll_no": r[0]} for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/internal-marks")
def get_internal_marks(dept_pk: str = Query(...), roll_no: str = Query(...), semester: int = Query(...)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT roll_no, subject_code, semester, dept_id,
                   attendance_marks, assignment_marks,
                   mst1_marks, mst2_marks,
                   total_internal_marks, status
            FROM vw_total_internal_marks
            WHERE dept_id = ? AND roll_no = ? AND semester = ?
        """, (dept_pk, roll_no, semester))
        rows = cursor.fetchall()
        return {"data": [
            {
                "roll_no": r[0],
                "subject_code": r[1],
                "semester": r[2],
                "dept_id": r[3],
                "attendance_marks": r[4],
                "assignment_marks": r[5],
                "mst1_marks": r[6],
                "mst2_marks": r[7],
                "total_internal_marks": r[8],
                "status": r[9]
            } for r in rows
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ---------------------------
# Main app
