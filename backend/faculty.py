from fastapi import FastAPI, Query, HTTPException , APIRouter
import pyodbc
from connect import get_connection
router = APIRouter()


@router.get("/low")
def get_low_attendance(
    semester: int = Query(..., description="Semester number"),
    dept_name: str = Query(..., description="Department name"),
    subject_name: str = Query(..., description="Subject name"),
    faculty_id: int = Query(..., description="Faculty PK")
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
        SELECT 
            s.roll_no,
            s.phone_number,
            agg.semester,
            (CAST(agg.lectures_attended AS FLOAT) / NULLIF(agg.total_lectures, 0)) * 100 AS attendance_percentage,
            agg.lectures_attended,
            agg.total_lectures
        FROM Student s
        JOIN AttendanceAggregate agg ON s.student_pk = agg.student_pk
        JOIN Subject subj ON agg.subject_pk = subj.subject_pk
        JOIN Department d ON s.dept_pk = d.dept_pk
        WHERE agg.semester = ?
          AND d.dept_name = ?
          AND subj.subject_name = ?
          AND agg.faculty_pk = ?
          AND (CAST(agg.lectures_attended AS FLOAT) / NULLIF(agg.total_lectures, 0)) < 0.75
        ORDER BY s.roll_no;
        """
        cursor.execute(query, (semester, dept_name, subject_name, faculty_id))
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No students found below 75% attendance")

        result = []
        for r in rows:
            result.append({
                "roll_no": r[0],
                "phone_number": r[1],
                "semester": r[2],
                "attendance_percentage": float(r[3]),
                "lectures_attended": r[4],
                "total_lectures": r[5]
            })
        return result
    finally:
        cursor.close()
        conn.close()
