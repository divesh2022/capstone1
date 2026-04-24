'''
Overview
This module defines API endpoints for managing Heads of Departments (HODs) in the college management system. It provides CRUD operations to add, update, delete, and list HODs, ensuring proper linkage between departments and faculty members.

Key Components
🔹 Data Models
HODCreate (Pydantic Model)  
Represents the structure for creating a new HOD record.
Attributes:

faculty_pk: Primary key of the faculty member

dept_pk: Primary key of the department

HODUpdate (Pydantic Model)  
Used for updating existing HOD records.
Attributes:

hod_id: Identifier of the HOD record

faculty_pk: Updated faculty assignment

dept_pk: Updated department assignment

🔹 Endpoints
GET /hods/ → list_hods  
Retrieves all HOD records.

POST /hods/ → create_hod  
Adds a new HOD record.

PUT /hods/{id} → update_hod  
Updates an existing HOD record by ID.

DELETE /hods/{id} → delete_hod  
Removes a HOD record.

🔹 Utility Functions
Database Connection  
Uses get_connection() from the connect module to establish and close database connections.

Error Handling  
Wraps queries in try/except blocks to ensure exceptions are caught and returned as HTTP errors.
'''
import csv

from fastapi import APIRouter, FastAPI, File, HTTPException, Header , UploadFile
from typing import List

from pydantic import BaseModel, EmailStr
from typing import Optional
from scipy import io
from streamlit import status
from connect import get_connection

#app = APIapp()
router = APIRouter()
## class - faculty allocation handelling
@router.get("/faculties/")
def list_faculties():
    """List all faculty with dept, name, email, designation."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT f.faculty_pk, d.dept_name, f.name, f.email, f.designation
            FROM Faculty f
            JOIN Department d ON f.dept_pk = d.dept_pk
        """)
        rows = cursor.fetchall()
        return [
            {
                "faculty_pk": r[0],
                "dept_name": r[1],
                "name": r[2],
                "email": r[3],
                "designation": r[4]
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/class_incharge/")
def list_class_incharge():
    """List all class–faculty allocations."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ci.class_incharge_pk, c.batch, d.dept_name, f.email, f.name, ci.semester
            FROM ClassIncharge ci
            JOIN Class c ON ci.class_pk = c.class_pk
            JOIN Department d ON c.dept_pk = d.dept_pk
            JOIN Faculty f ON ci.faculty_pk = f.faculty_pk
        """)
        rows = cursor.fetchall()
        return [
            {"class_incharge_pk": r[0], "batch": r[1], "dept_name": r[2], "faculty_email": r[3], "semester": r[4]}
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/class_incharge/")
def create_class_incharge(batch: str, dept_name: str, faculty_email: str, semester: int):
    """Assign a faculty as class incharge by selecting batch, department name, and faculty email."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Resolve class_pk
        cursor.execute("""
            SELECT c.class_pk
            FROM Class c
            JOIN Department d ON c.dept_pk = d.dept_pk
            WHERE c.batch = ? AND d.dept_name = ?
        """, (batch, dept_name))
        class_row = cursor.fetchone()
        if not class_row:
            raise HTTPException(status_code=400, detail="Invalid class (batch/department)")

        class_pk = class_row[0]

        # Resolve faculty_pk
        cursor.execute("SELECT faculty_pk FROM Faculty WHERE email = ?", (faculty_email,))
        faculty_row = cursor.fetchone()
        if not faculty_row:
            raise HTTPException(status_code=400, detail="Invalid faculty email")

        faculty_pk = faculty_row[0]

        # Insert allocation
        cursor.execute(
            "INSERT INTO ClassIncharge (class_pk, faculty_pk, semester) VALUES (?, ?, ?)",
            (class_pk, faculty_pk, semester)
        )
        conn.commit()
        return {"message": "Class–Faculty allocation created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.put("/class_incharge/{class_incharge_pk}")
def update_class_incharge(class_incharge_pk: int, new_batch: str = None, new_dept_name: str = None,
                          new_faculty_email: str = None, new_semester: int = None):
    """Update an existing class–faculty allocation by natural keys."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if new_batch and new_dept_name:
            cursor.execute("""
                SELECT c.class_pk
                FROM Class c
                JOIN Department d ON c.dept_pk = d.dept_pk
                WHERE c.batch = ? AND d.dept_name = ?
            """, (new_batch, new_dept_name))
            class_row = cursor.fetchone()
            if not class_row:
                raise HTTPException(status_code=400, detail="Invalid class (batch/department)")
            cursor.execute("UPDATE ClassIncharge SET class_pk = ? WHERE class_incharge_pk = ?", (class_row[0], class_incharge_pk))

        if new_faculty_email:
            cursor.execute("SELECT faculty_pk FROM Faculty WHERE email = ?", (new_faculty_email,))
            faculty_row = cursor.fetchone()
            if not faculty_row:
                raise HTTPException(status_code=400, detail="Invalid faculty email")
            cursor.execute("UPDATE ClassIncharge SET faculty_pk = ? WHERE class_incharge_pk = ?", (faculty_row[0], class_incharge_pk))

        if new_semester:
            cursor.execute("UPDATE ClassIncharge SET semester = ? WHERE class_incharge_pk = ?", (new_semester, class_incharge_pk))

        conn.commit()
        return {"message": "Class–Faculty allocation updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/class_incharge/{class_incharge_pk}")
def delete_class_incharge(class_incharge_pk: int):
    """Delete a class–faculty allocation."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ClassIncharge WHERE class_incharge_pk = ?", (class_incharge_pk,))
        conn.commit()
        return {"message": "Class–Faculty allocation deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@router.get("/classes/")
def list_classes():
    """List all classes with batch and department name."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.class_pk, c.batch, d.dept_name
            FROM Class c
            JOIN Department d ON c.dept_pk = d.dept_pk
        """)
        rows = cursor.fetchall()
        return [
            {"class_pk": r[0], "batch": r[1], "dept_name": r[2]} for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/departments/")
def list_departments():
    """List all departments."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT dept_pk, dept_name FROM Department")
        rows = cursor.fetchall()
        return [
            {"dept_pk": r[0], "dept_name": r[1]} for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/classes/")
def create_class(batch: str, dept_name: str):
    """Create a new class by batch and department name."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT dept_pk FROM Department WHERE dept_name = ?", (dept_name,))
        dept_row = cursor.fetchone()
        if not dept_row:
            raise HTTPException(status_code=400, detail="Invalid department name")
        dept_pk = dept_row[0]

        cursor.execute("INSERT INTO Class (batch, dept_pk) VALUES (?, ?)", (batch, dept_pk))
        conn.commit()
        return {"message": "Class created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

## Class–Faculty Allocation

# List all classes
@router.get("/classes/")
def list_classes():
    """List all classes with batch and department name."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.class_pk, c.batch, d.dept_name
            FROM Class c
            JOIN Department d ON c.dept_pk = d.dept_pk
        """)
        rows = cursor.fetchall()
        return [
            {"class_pk": r[0], "batch": r[1], "dept_name": r[2]} for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in /classes/: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Create a new class
@router.post("CS/classes/")
def create_class(batch: str, dept_name: str):
    """Create a new class by batch and department name."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT dept_pk FROM Department WHERE dept_name = ?", (dept_name,))
        dept_row = cursor.fetchone()
        if not dept_row:
            raise HTTPException(status_code=400, detail="Invalid department name")
        dept_pk = dept_row[0]

        cursor.execute("INSERT INTO Class (batch, dept_pk) VALUES (?, ?)", (batch, dept_pk))
        conn.commit()
        return {"message": "Class created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating class: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Update an existing class
@router.put("/classes/{class_pk}")
def update_class(class_pk: int, new_batch: str = None, new_dept_name: str = None):
    """Update class batch or department by natural keys."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if new_batch:
            cursor.execute("UPDATE Class SET batch = ? WHERE class_pk = ?", (new_batch, class_pk))

        if new_dept_name:
            cursor.execute("SELECT dept_pk FROM Department WHERE dept_name = ?", (new_dept_name,))
            dept_row = cursor.fetchone()
            if not dept_row:
                raise HTTPException(status_code=400, detail="Invalid department name")
            cursor.execute("UPDATE Class SET dept_pk = ? WHERE class_pk = ?", (dept_row[0], class_pk))

        conn.commit()
        return {"message": "Class updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating class: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Delete a class
@router.delete("/classes/{class_pk}")
def delete_class(class_pk: int):
    """Delete a class by its PK."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Class WHERE class_pk = ?", (class_pk,))
        conn.commit()
        return {"message": "Class deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting class: {str(e)}")
    finally:
        cursor.close()
        conn.close()

## faculty subject allocation 



# --- Pydantic Schemas for Validation ---
class FacultySubjectBase(BaseModel):
    email: EmailStr
    subject_code: str
    semester: int

class FacultySubjectUpdate(BaseModel):
    new_subject_code: Optional[str] = None
    new_semester: Optional[int] = None

# --- Helper Function for DB Operations ---
def execute_query(query, params=None, commit=False, fetch=False):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
        if fetch:
            return cursor.fetchall()
        return None
    except Exception as e:
        if commit: conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- CSV Import Logic ---
@router.post("/faculty-subjects/upload-csv")
async def upload_faculty_subjects(file: UploadFile = File(...)):
    """Bulk insert faculty subject allocations via CSV."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    contents = await file.read()
    buffer = io.StringIO(contents.decode('utf-8'))
    reader = csv.DictReader(buffer)

    # Expected CSV columns: email, subject_code, semester
    query = """
    INSERT INTO FacultySubject (faculty_pk, subject_pk, semester)
    VALUES (
        (SELECT faculty_pk FROM Faculty WHERE email = ?),
        (SELECT subject_pk FROM Subject WHERE subject_code = ?),
        ?
    )
    """
    
    conn = get_connection()
    cursor = conn.cursor()
    success_count = 0
    
    try:
        for row in reader:
            cursor.execute(query, (row['email'], row['subject_code'], int(row['semester'])))
        conn.commit()
        return {"message": "CSV data imported successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error at row {success_count + 1}: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# --- CRUD Operations ---

@router.post("/faculty-subjects/allocate")
def allocate_subject(data: FacultySubjectBase):
    """Single insert for faculty subject allocation."""
    query = """
    INSERT INTO FacultySubject (faculty_pk, subject_pk, semester)
    VALUES (
        (SELECT faculty_pk FROM Faculty WHERE email = ?),
        (SELECT subject_pk FROM Subject WHERE subject_code = ?),
        ?
    )
    """
    execute_query(query, (data.email, data.subject_code, data.semester), commit=True)
    return {"status": "Allocation successful"}

@router.put("/faculty-subjects/update")
def update_allocation(email: str, old_subject_code: str, old_semester: int, update_data: FacultySubjectUpdate):
    """Update allocation by finding current record via email/code/semester."""
    query = """
    UPDATE FacultySubject
    SET subject_pk = COALESCE((SELECT subject_pk FROM Subject WHERE subject_code = ?), subject_pk),
        semester = COALESCE(?, semester)
    WHERE faculty_pk = (SELECT faculty_pk FROM Faculty WHERE email = ?)
      AND subject_pk = (SELECT subject_pk FROM Subject WHERE subject_code = ?)
      AND semester = ?
    """
    execute_query(query, (
        update_data.new_subject_code, 
        update_data.new_semester,
        email, 
        old_subject_code, 
        old_semester
    ), commit=True)
    return {"status": "Update successful"}

@router.delete("/faculty-subjects/delete")
def delete_allocation(email: str, subject_code: str, semester: int):
    """Delete specific allocation."""
    query = """
    DELETE FROM FacultySubject
    WHERE faculty_pk = (SELECT faculty_pk FROM Faculty WHERE email = ?)
      AND subject_pk = (SELECT subject_pk FROM Subject WHERE subject_code = ?)
      AND semester = ?
    """
    execute_query(query, (email, subject_code, semester), commit=True)
    return {"status": "Allocation deleted"}
@router.get("/FS/subjects/")
def get_subjects():
    """List all subjects with code and name."""
    query = """
    SELECT subject_pk, subject_code, subject_name FROM Subject
    """
    rows = execute_query(query, fetch=True)
    return [
        {"subject_pk": r[0], "subject_code": r[1], "subject_name": r[2]} for r in rows
    ]
## class student allocation

# --- Pydantic Schemas ---
class StudentAllocation(BaseModel):
    roll_no: str
    batch: str
    dept_name: str
    semester: int

# --- API Endpoints ---

@router.post("/class-students/allocate")
def allocate_student_to_class(data: StudentAllocation):
    """Assign a student to a class based on natural keys."""
    query = """
    INSERT INTO ClassStudent (student_pk, class_pk, semester)
    VALUES (
        (SELECT student_pk FROM Student WHERE roll_no = ?),
        (SELECT c.class_pk FROM Class c 
         JOIN Department d ON c.dept_pk = d.dept_pk 
         WHERE c.batch = ? AND d.dept_name = ?),
        ?
    )
    """
    execute_query(query, (data.roll_no, data.batch, data.dept_name, data.semester), commit=True)
    return {"status": "Student allocated to class successfully"}

@router.post("/class-students/upload-csv")
async def bulk_allocate_students(file: UploadFile = File(...)):
    """Bulk insert students into classes via CSV."""
    contents = await file.read()
    buffer = io.StringIO(contents.decode('utf-8'))
    reader = csv.DictReader(buffer)
    
    query = """
    INSERT INTO ClassStudent (student_pk, class_pk, semester)
    VALUES (
        (SELECT student_pk FROM Student WHERE roll_no = ?),
        (SELECT c.class_pk FROM Class c 
         JOIN Department d ON c.dept_pk = d.dept_pk 
         WHERE c.batch = ? AND d.dept_name = ?),
        ?
    )
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for row in reader:
            cursor.execute(query, (
                row['roll_no'], 
                row['batch'], 
                row['dept_name'], 
                int(row['semester'])
            ))
        conn.commit()
        return {"message": "Bulk student allocation successful"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.delete("/class-students/delete")
def delete_student_allocation(roll_no: str, batch: str, dept_name: str, semester: int):
    """Remove a student from a class allocation."""
    query = """
    DELETE FROM ClassStudent
    WHERE student_pk = (SELECT student_pk FROM Student WHERE roll_no = ?)
      AND semester = ?
      AND class_pk = (SELECT c.class_pk FROM Class c 
                      JOIN Department d ON c.dept_pk = d.dept_pk 
                      WHERE c.batch = ? AND d.dept_name = ?)
    """
    execute_query(query, (roll_no, semester, batch, dept_name), commit=True)
    return {"status": "Allocation removed"}
## class semester handling
class ClassSemesterBase(BaseModel):
    batch: str
    dept_name: str
    semester: int

class ClassSemesterUpdate(BaseModel):
    new_semester: int
@router.post("/class/semester")
def insert_class_semester(data: ClassSemesterBase):
    """Update the semester column for a specific class."""
    query = """
    UPDATE Class
    SET semester = ?
    WHERE batch = ? 
      AND dept_pk = (SELECT dept_pk FROM Department WHERE dept_name = ?)
    """
    execute_query(query, (data.semester, data.batch, data.dept_name), commit=True)
    return {"status": "Class semester record updated"}

@router.put("/class/semester/update")
def update_class_semester(batch: str, dept_name: str, old_semester: int, update_data: ClassSemesterUpdate):
    """Change an existing semester record to a new value."""
    query = """
    UPDATE Class
    SET semester = ?
    WHERE batch = ? 
      AND semester = ?
      AND dept_pk = (SELECT dept_pk FROM Department WHERE dept_name = ?)
    """
    execute_query(query, (update_data.new_semester, batch, old_semester, dept_name), commit=True)
    return {"status": "Semester updated successfully"}
## class subject handling
@router.get("classes")
def get_classes():
    """List all classes with batch and department name."""
    query = """
    SELECT c.class_pk, c.batch, d.dept_name
    FROM Class c
    JOIN Department d ON c.dept_pk = d.dept_pk
    """
    rows = execute_query(query, fetch=True)
    return [
        {"class_pk": r[0], "batch": r[1], "dept_name": r[2]} for r in rows
    ]
@router.get("/subjects")
def get_subjects():
    """List all subjects with code and name."""
    query = """
    SELECT subject_pk, subject_code, subject_name FROM Subject
    """
    rows = execute_query(query, fetch=True)
    return [
        {"subject_pk": r[0], "subject_code": r[1], "subject_name": r[2]} for r in rows
    ]
@router.post("/class-subjects/allocate/")
def allocate_subject_to_class(batch: str, dept_name: str, subject_code: str,semester: int):
        """Assign a subject to a class based on natural keys."""
        query = """
        INSERT INTO ClassSubject (class_pk, subject_pk, semester)
        VALUES (
            (SELECT c.class_pk FROM Class c 
             JOIN Department d ON c.dept_pk = d.dept_pk 
             WHERE c.batch = ? AND d.dept_name = ?),
            (SELECT subject_pk FROM Subject WHERE subject_code = ?),
            ?
        )
        """
        execute_query(query, (batch, dept_name, subject_code, semester), commit=True)
        return {"status": "Subject allocated to class successfully"}
@router.get("/class-subjects/")
def get_class_subject_allocations():
    """List all subject allocations grouped by class (batch + department)."""
    query = """
    SELECT 
        c.class_pk,
        c.batch,
        d.dept_name,
        s.subject_code,
        s.subject_name,
        cs.semester
    FROM ClassSubject cs
    JOIN Class c ON cs.class_pk = c.class_pk
    JOIN Department d ON c.dept_pk = d.dept_pk
    JOIN Subject s ON cs.subject_pk = s.subject_pk
    ORDER BY c.batch, d.dept_name, cs.semester
    """
    rows = execute_query(query, fetch=True)

    # Group allocations by class
    allocations = {}
    for r in rows:
        class_key = f"{r[1]} - {r[2]}"  # e.g. "2025 - Computer Science"
        if class_key not in allocations:
            allocations[class_key] = {
                "class_pk": r[0],
                "batch": r[1],
                "dept_name": r[2],
                "subjects": []
            }
        allocations[class_key]["subjects"].append({
            "subject_code": r[3],
            "subject_name": r[4],
            "semester": r[5]
        })

    return list(allocations.values())

## class incharge handling
@router.get("/Ci/class-incharge/")
def get_class_incharge_allocations():
    """List all class incharge allocations with class and faculty details."""
    query = """
    SELECT 
        ci.class_incharge_pk,
        c.batch,
        d.dept_name,
        f.email,
        f.name,
        ci.semester
    FROM ClassIncharge ci
    JOIN Class c ON ci.class_pk = c.class_pk
    JOIN Department d ON c.dept_pk = d.dept_pk
    JOIN Faculty f ON ci.faculty_pk = f.faculty_pk
    ORDER BY c.batch, d.dept_name, ci.semester
    """
    rows = execute_query(query, fetch=True)
    return [
        {
            "class_incharge_pk": r[0],
            "batch": r[1],
            "dept_name": r[2],
            "faculty_email": r[3],
            "faculty_name": r[4],
            "semester": r[5]
        } for r in rows
    ]
@router.get("/Ci/faculties/")
def get_faculties():
    """List all faculty with dept, name, email, designation."""
    query = """
    SELECT f.faculty_pk, d.dept_name, f.name, f.email, f.designation
    FROM Faculty f
    JOIN Department d ON f.dept_pk = d.dept_pk
    """
    rows = execute_query(query, fetch=True)
    return [
        {
            "faculty_pk": r[0],
            "dept_name": r[1],
            "name": r[2],
            "email": r[3],
            "designation": r[4]
        } for r in rows
    ]
@router.get("/Ci/classes/")
def get_classes():
    """List all classes with batch and department."""
    query = """
    SELECT c.class_pk, c.batch, d.dept_name
    FROM Class c
    JOIN Department d ON c.dept_pk = d.dept_pk
    """
    rows = execute_query(query, fetch=True)
    return [
        {"class_pk": r[0], "batch": r[1], "dept_name": r[2]} for r in rows
    ]
@router.post("/Ci/class-incharge/")
def allocate_class_incharge(batch: str, dept_name: str, faculty_email: str, semester: int):
    """Assign a faculty as class incharge by selecting batch, department name, and faculty email."""
    query = """
    INSERT INTO ClassIncharge (class_pk, faculty_pk, semester)
    VALUES (
        (SELECT c.class_pk FROM Class c 
         JOIN Department d ON c.dept_pk = d.dept_pk 
         WHERE c.batch = ? AND d.dept_name = ?),
        (SELECT faculty_pk FROM Faculty WHERE email = ?),
        ?
    )
    """
    execute_query(query, (batch, dept_name, faculty_email, semester), commit=True)
    return {"status": "Class incharge allocated successfully"}

## MST handelling
## refference : mst.py in facultyfile change the route 
## internal marks handelling
@router.get("/Tm/total-internal-marks")
def total_internal_marks():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT roll_no, subject_code, semester, dept_id,
                   attendance_marks, assignment_marks,
                   mst1_marks, mst2_marks, total_internal_marks, status
            FROM vw_total_internal_marks
        """)
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No internal marks found")

        # Convert each row into a dictionary
        result = [
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
            }
            for r in rows
        ]

        return result
    finally:
        cursor.close()
        conn.close()

@router.get("/Tm/subjects/")
def get_subjects():
    """List all subjects with code and name."""
    query = """
    SELECT subject_pk, subject_code, subject_name FROM Subject
    """
    rows = execute_query(query, fetch=True)
    
    return [
        {"subject_pk": r[0], "subject_code": r[1], "subject_name": r[2]} for r in rows
    ]
@router.get("/Tm/faculties/")
def get_faculties():
    """List all faculty with dept, name, email, designation."""
    query = """
    SELECT f.faculty_pk, d.dept_name, f.name, f.email, f.designation
    FROM Faculty f
    JOIN Department d ON f.dept_pk = d.dept_pk
    """
    rows = execute_query(query, fetch=True)
    return [
        {
            "faculty_pk": r[0],
            "dept_name": r[1],
            "name": r[2],
            "email": r[3],
            "designation": r[4]
        } for r in rows
    ]
@router.get("/")
def root():
    return {"message": "HOD API is running"}
