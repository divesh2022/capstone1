from fastapi import APIRouter, FastAPI, HTTPException, Header
from connect import get_connection

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Student API is running"}

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.get("/profile")
def profile(rollno: str = Header(...)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT st.roll_no, st.batch, st.phone_number, d.dept_name , c.college_name
            FROM Student st
            JOIN Department d ON st.dept_pk = d.dept_pk
            JOIN College c ON d.college_pk = c.college_pk
            WHERE st.roll_no = ?
        """, (rollno,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Student not found")

        roll_no, batch, phone_number, dept_name, college_name = row
        return {
            "roll_no": roll_no,
            "batch": batch,
            "phone_number": phone_number,
            "department": dept_name,
            "college": college_name
        }
    finally:
        cursor.close()
        conn.close()
## attendence

@router.get("/attendance_aggregate")
def attendance_aggregate(rollno: str = Header(...)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT sa.lectures_attended, sa.total_lectures, s.subject_code, sa.semester, d.dept_name
            FROM AttendanceAggregate sa
            JOIN Student st ON sa.student_pk = st.student_pk
            JOIN Department d ON st.dept_pk = d.dept_pk
            JOIN Subject s ON sa.subject_pk = s.subject_pk
            WHERE st.roll_no = ?
        """, (rollno,))
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="Attendance records not found")

        results = []
        for lectures_attended, total_lectures, subject_code, semester, dept_name in rows:
            results.append({
                "lectures_attended": lectures_attended,
                "total_lectures": total_lectures,
                "subject_code": subject_code,
                "semester": semester,
                "department": dept_name
            })

        return {"roll_no": rollno, "attendance_summary": results}
    finally:
        cursor.close()
        conn.close()
## assignment marks
@router.get("/assignment_marks")
def assignment_marks(rollno: str = Header(...)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT am.marks, a.total_marks, s.subject_code, a.semester, d.dept_name
            FROM AssignmentMarks am
            JOIN Student st ON am.student_pk = st.student_pk
            JOIN Department d ON st.dept_pk = d.dept_pk
            JOIN Assignment a ON am.assignment_pk = a.assignment_pk
            JOIN Subject s ON a.subject_pk = s.subject_pk
            WHERE st.roll_no = ?
        """, (rollno,))
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="Assignment marks not found")

        results = []
        for marks, total_marks, subject_code, semester, dept_name in rows:
            results.append({
                "marks_obtained": marks,
                "total_marks": total_marks,
                "subject_code": subject_code,
                "semester": semester,
                "department": dept_name
            })

        return {"roll_no": rollno, "assignment_marks_summary": results}
    finally:
        cursor.close()
        conn.close()
## mst marks
@router.get("/mst_marks")
def mst_marks(rollno: str = Header(...)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT mm.marks, m.total_marks, s.subject_code, m.semester, d.dept_name
            FROM MSTExamMarks mm
            JOIN Student st ON mm.student_pk = st.student_pk
            JOIN Department d ON st.dept_pk = d.dept_pk
            JOIN MSTExam m ON mm.exam_pk = m.exam_pk
            JOIN Subject s ON m.subject_pk = s.subject_pk
            WHERE st.roll_no = ?
        """, (rollno,))
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="MST marks not found")

        results = []
        for marks, total_marks, subject_code, semester, dept_name in rows:
            results.append({
                "marks_obtained": marks,
                "total_marks": total_marks,
                "subject_code": subject_code,
                "semester": semester,
                "department": dept_name
            })

        return {"roll_no": rollno, "mst_marks_summary": results}
    finally:
        cursor.close()
        conn.close()

## class info
@router.get("/class_info")
def class_info(rollno: str = Header(...)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT cs.semester,st.roll_no FROM ClassStudent cs JOIN Student st ON cs.student_pk = st.student_pk where st.roll_no = ?;
        """, (rollno,))
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="Class information")
        results = []
        for Semester, dept_name in rows:
            results.append({
                "Semester": Semester,
                "department": dept_name
            })
        return {"roll_no": rollno, "class_info": results}
    finally:
        cursor.close()
        conn.close()

## total internal marks
@router.get("/total_internal_marks")
def total_internal_marks(rollno: str = Header(...)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT roll_no, subject_code, semester, dept_id, attendance_marks, assignment_marks, mst1_marks, mst2_marks, total_internal_marks, status
            FROM vw_total_internal_marks
            WHERE roll_no = ?
        """, (rollno,))
        rows = cursor.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="Total internal marks not found")
        results = []
        for roll_no, subject_code, semester, dept_id, attendance_marks, assignment_marks, mst1_marks, mst2_marks, total_internal_marks, status in rows:
            results.append({
                "roll_no": roll_no,
                "subject_code": subject_code,
                "semester": semester,
                "dept_id": dept_id,
                "attendance_marks": attendance_marks,
                "assignment_marks": assignment_marks,
                "mst1_marks": mst1_marks,
                "mst2_marks": mst2_marks,
                "total_internal_marks": total_internal_marks,
                "status": status
            })
        return {"roll_no": rollno, "total_internal_marks": results}
    finally:
        cursor.close()
        conn.close()

## View faculty teaching their class
## View subjects allocated to class
## View class allocation