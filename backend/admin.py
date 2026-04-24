## endpoints to insert / update / delete data in the database, only accessible by admin users
## custom query editor for admin users to run any query on the database and see the results execpt drop database or delete from table without where clause
import csv

from fastapi import APIRouter, FastAPI, File, HTTPException, Header , UploadFile
from typing import List, Optional

from pydantic import BaseModel
from connect import get_connection

#app = FastAPI()
router = APIRouter()

# role table
@router.post("/role/roles/")
def create_role(role_name: str):
    """Create a new role."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Roles (role_name) VALUES (?)", (role_name,))
        conn.commit()
        return {"message": "Role created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.put("/role/roles/{role_id}")
def update_role(role_id: int, role_name: str):
    """Update an existing role."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Roles SET role_name = ? WHERE role_pk = ?", (role_name, role_id))
        conn.commit()
        return {"message": "Role updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@router.delete("/role/roles/{role_id}")
def delete_role(role_id: int):
    """Delete a role."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Roles WHERE role_pk = ?", (role_id,))
        conn.commit()
        return {"message": "Role deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@router.get("/role/roles/")
def list_roles():
    """Fetch all roles."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT role_pk, role_name FROM Roles")
        rows = cursor.fetchall()
        results = [{"role_id": r[0], "role_name": r[1]} for r in rows]
        return {"roles": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/")
def root():
    return {"message": "Admin API is running"}
@router.get("/health")
def health_check():
    return {"status": "healthy"}

## user table
@router.get("/user/users/")
def list_users():
    """List all users with their primary keys."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, user_pk FROM Users")
        rows = cursor.fetchall()
        return [
            {"username": r[0], "user_pk": r[1]} for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@router.post("/user/users/")
def create_user(username: str, email: str, phone_number: str):
    """Create a new user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Users (username, email, phone_number) VALUES (?, ?, ?)",
            (username, email, phone_number),
        )
        conn.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@router.put("/user/users/{user_id}")
def update_user(user_id: int, username: str = None, email: str = None, phone_number: str = None):
    """Update an existing user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if username:
            cursor.execute("UPDATE Users SET username = ? WHERE user_pk = ?", (username, user_id))
        if email:
            cursor.execute("UPDATE Users SET email = ? WHERE user_pk = ?", (email, user_id))
        if phone_number:
            cursor.execute("UPDATE Users SET phone_number = ? WHERE user_pk = ?", (phone_number, user_id))
        conn.commit()
        return {"message": "User updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@router.delete("/user/users/{user_id}")
def delete_user(user_id: int):
    """Delete a user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Users WHERE user_pk = ?", (user_id,))
        conn.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
# bulk upload of users from csv file, only accessible by admin users
@router.post("/user/users/bulk")
def bulk_upload_users(file: UploadFile = File(...)):
    """Bulk upload users from a CSV file."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        content = file.file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(content)

        for row in reader:
            cursor.execute(
                "INSERT INTO Users (username, email, phone_number) VALUES (?, ?, ?)",
                (row.get("username"), row.get("email"), row.get("phone_number")),
            )
        conn.commit()
        return {"message": "Users uploaded successfully"}  # always return JSON
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



## UserRoles table
@router.get("/UR/users/list")
def list_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_pk, email FROM Users")
    rows = cursor.fetchall()
    return [{"user_pk": r[0], "email": r[1]} for r in rows]

@router.get("/UR/roles/list")
def list_roles():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role_pk, role_name FROM Roles")
    rows = cursor.fetchall()
    return [{"role_pk": r[0], "role_name": r[1]} for r in rows]

# Insert a new UserRole with default password
@router.post("/UR/userroles/")
def insert_userrole(user_pk: int, role_pk: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get username to build default password
        cursor.execute("SELECT username FROM Users WHERE user_pk = ?", (user_pk,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        default_password = f"{row[0]}_123"

        cursor.execute(
            "INSERT INTO UserRoles (user_pk, role_pk, password_hash) VALUES (?, ?, ?)",
            (user_pk, role_pk, default_password),
        )
        conn.commit()
        return {"message": "UserRole inserted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# Update password for a UserRole
@router.put("/UR/userroles/{user_pk}/{role_pk}")
def update_userrole(user_pk: int, role_pk: int, password_hash: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE UserRoles SET password_hash = ? WHERE user_pk = ? AND role_pk = ?",
            (password_hash, user_pk, role_pk),
        )
        conn.commit()
        return {"message": "UserRole updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# Delete a UserRole
@router.delete("/UR/userroles/{user_pk}/{role_pk}")
def delete_userrole(user_pk: int, role_pk: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM UserRoles WHERE user_pk = ? AND role_pk = ?",
            (user_pk, role_pk),
        )
        conn.commit()
        return {"message": "UserRole deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()




# Query endpoint: join Users, UserRoles, Roles
@router.get("/UR/userroles/view")
def view_userroles():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT u.user_pk, u.username, r.role_name
            FROM Users u
            JOIN UserRoles ur ON u.user_pk = ur.user_pk
            JOIN Roles r ON ur.role_pk = r.role_pk
        """)
        rows = cursor.fetchall()
        results = [{"user_pk": r[0], "username": r[1], "role_name": r[2]} for r in rows]
        return {"user_roles": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

## query editor endpoint for admin users to run any query on the database and see the results execpt drop database or delete from table without where clause
@router.post("/admin/query")
def run_query(query: str):
    """Run arbitrary SQL query with safety checks (no API key)."""

    q_lower = query.strip().lower()
    if "drop database" in q_lower:
        raise HTTPException(status_code=400, detail="DROP DATABASE is not allowed")
    if q_lower.startswith("delete from") and "where" not in q_lower:
        raise HTTPException(status_code=400, detail="DELETE without WHERE is not allowed")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        queries = [q.strip() for q in query.split(";") if q.strip()]
        results_list = []

        for q in queries:
            cursor.execute(q)
            if cursor.description:  # SELECT or similar
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
                results_list.append({"query": q, "results": results})
            else:  # UPDATE/INSERT/DELETE with WHERE
                conn.commit()
                results_list.append({"query": q, "message": "Query executed successfully"})

        return {"queries": results_list}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
## college
## college
@router.get("/cg/colleges/")
def list_colleges():
    """List all colleges with their primary keys."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT college_pk, college_id, college_name FROM College")
        rows = cursor.fetchall()
        return [
            {"college_pk": r[0], "college_id": r[1], "college_name": r[2]} for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/cg/colleges/")
def create_college(college_id: str, college_name: str):
    """Create a new college."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO College (college_id, college_name) VALUES (?, ?)",
            (college_id, college_name),
        )
        conn.commit()
        return {"message": "College created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.put("/cg/colleges/{college_pk}")
def update_college(college_pk: int, college_id: str = None, college_name: str = None):
    """Update an existing college."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if college_id:
            cursor.execute("UPDATE College SET college_id = ? WHERE college_pk = ?", (college_id, college_pk))
        if college_name:
            cursor.execute("UPDATE College SET college_name = ? WHERE college_pk = ?", (college_name, college_pk))
        conn.commit()
        return {"message": "College updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/cg/colleges/{college_pk}")
def delete_college(college_pk: int):
    """Delete a college."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM College WHERE college_pk = ?", (college_pk,))
        conn.commit()
        return {"message": "College deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
## department

# ---------------------------
# Models
class Department(BaseModel):
    dept_id: str
    dept_name: str
    college_pk: int

class DepartmentUpdate(BaseModel):
    dept_id: Optional[str] = None
    dept_name: Optional[str] = None
    college_pk: Optional[int] = None

# ---------------------------
# Helpers
def fetch_query(sql: str, params: tuple = ()):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            results = []
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

# ---------------------------
# Endpoints

@router.get("/dp/departments/{college_pk}")
def get_departments(college_pk: int):
    sql = "SELECT dept_pk, dept_id, dept_name, college_pk FROM Department WHERE college_pk = ?"
    return fetch_query(sql, (college_pk,))

@router.post("/dp/departments/")
def create_department(dept_id: str, dept_name: str, college_pk: int):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO Department (dept_id, dept_name, college_pk) VALUES (?, ?, ?)"
    try:
        cursor.execute(sql, (dept_id, dept_name, college_pk))
        conn.commit()

        return {"message": "Department created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@router.put("/dp/departments/{dept_pk}")
def update_department(dept_pk: int, dept_id: Optional[str] = None, dept_name: Optional[str] = None, college_pk: Optional[int] = None):
    sql = "UPDATE Department SET dept_id = ?, dept_name = ?, college_pk = ? WHERE dept_pk = ?"
    fetch_query(sql, (dept_id, dept_name, college_pk, dept_pk))
    return {"message": "Department updated successfully"}

@router.delete("/dp/departments/{dept_pk}")
def delete_department(dept_pk: int):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM Department WHERE dept_pk = ?"
    try:
        cursor.execute(sql, (dept_pk,))
        conn.commit()
        return {"message": "Department deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/dp/colleges/")
def get_colleges():
    sql = "SELECT college_pk, college_name FROM College"
    return fetch_query(sql)

### branch
@router.get("/br/branches/")
def list_branches():
    """List all branches with their primary keys."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT branch_pk, branch_id, branch_name, dept_pk, dept_id, branch_code FROM Branch")
        rows = cursor.fetchall()
        return [
            {
                "branch_pk": r[0],
                "branch_id": r[1],
                "branch_name": r[2],
                "dept_pk": r[3],
                "dept_id": r[4],
                "branch_code": r[5],
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/br/branches/")
def create_branch(branch_id: str, branch_name: str, dept_name: str):
    """
    Create a new branch by selecting department name.
    Backend resolves dept_pk and dept_id internally.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Resolve dept_pk and dept_id from department name
        cursor.execute("SELECT dept_pk, dept_id FROM Department WHERE dept_name = ?", (dept_name,))
        dept_row = cursor.fetchone()
        if not dept_row:
            raise HTTPException(status_code=400, detail="Invalid department name: Department does not exist")

        dept_pk, dept_id = dept_row

        cursor.execute(
            "INSERT INTO Branch (branch_id, branch_name, dept_pk, dept_id) VALUES (?, ?, ?, ?)",
            (branch_id, branch_name, dept_pk, dept_id),
        )
        conn.commit()
        return {"message": "Branch created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.put("/br/branches/{branch_name}")
def update_branch(branch_name: str, new_branch_id: str = None, new_branch_name: str = None, new_dept_name: str = None):
    """
    Update an existing branch by branch_name.
    If new_dept_name is provided, resolve dept_pk and dept_id internally.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if new_branch_id:
            cursor.execute("UPDATE Branch SET branch_id = ? WHERE branch_name = ?", (new_branch_id, branch_name))
        if new_branch_name:
            cursor.execute("UPDATE Branch SET branch_name = ? WHERE branch_name = ?", (new_branch_name, branch_name))
        if new_dept_name:
            cursor.execute("SELECT dept_pk, dept_id FROM Department WHERE dept_name = ?", (new_dept_name,))
            dept_row = cursor.fetchone()
            if not dept_row:
                raise HTTPException(status_code=400, detail="Invalid department name: Department does not exist")
            dept_pk, dept_id = dept_row
            cursor.execute("UPDATE Branch SET dept_pk = ?, dept_id = ? WHERE branch_name = ?", (dept_pk, dept_id, branch_name))
        conn.commit()
        return {"message": "Branch updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/br/branches/{branch_name}")
def delete_branch(branch_name: str):
    """Delete a branch by branch_name (no PK typing required)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Branch WHERE branch_name = ?", (branch_name,))
        conn.commit()
        return {"message": "Branch deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

## course
## course
@router.get("/Cr/courses/")
def list_courses():
    """List all courses with their primary keys."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT course_pk, course_code, course_name, branch_pk FROM Course")
        rows = cursor.fetchall()
        return [
            {"course_pk": r[0], "course_code": r[1], "course_name": r[2], "branch_pk": r[3]}
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/Cr/courses/")
def create_course(course_code: str, course_name: str, branch_name: str):
    """
    Create a new course by selecting branch name.
    Backend resolves branch_pk internally.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Resolve branch_pk from branch name
        cursor.execute("SELECT branch_pk FROM Branch WHERE branch_name = ?", (branch_name,))
        branch_row = cursor.fetchone()
        if not branch_row:
            raise HTTPException(status_code=400, detail="Invalid branch name: Branch does not exist")

        branch_pk = branch_row[0]

        cursor.execute(
            "INSERT INTO Course (course_code, course_name, branch_pk) VALUES (?, ?, ?)",
            (course_code, course_name, branch_pk),
        )
        conn.commit()
        return {"message": "Course created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.put("/Cr/courses/{course_code}")
def update_course(course_code: str, new_course_name: str = None, new_branch_name: str = None):
    """
    Update an existing course by course_code.
    If new_branch_name is provided, resolve branch_pk internally.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if new_course_name:
            cursor.execute("UPDATE Course SET course_name = ? WHERE course_code = ?", (new_course_name, course_code))
        if new_branch_name:
            cursor.execute("SELECT branch_pk FROM Branch WHERE branch_name = ?", (new_branch_name,))
            branch_row = cursor.fetchone()
            if not branch_row:
                raise HTTPException(status_code=400, detail="Invalid branch name: Branch does not exist")
            branch_pk = branch_row[0]
            cursor.execute("UPDATE Course SET branch_pk = ? WHERE course_code = ?", (branch_pk, course_code))
        conn.commit()
        return {"message": "Course updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/Cr/courses/{course_code}")
def delete_course(course_code: str):
    """Delete a course by course_code (no PK typing required)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Course WHERE course_code = ?", (course_code,))
        conn.commit()
        return {"message": "Course deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

## subject
@router.get("/Sub/subjects/")
def list_subjects():
    """List all subjects with their primary keys."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT subject_pk, subject_code, subject_name, course_pk, syllabus_pdf FROM Subject")
        rows = cursor.fetchall()
        return [
            {
                "subject_pk": r[0],
                "subject_code": r[1],
                "subject_name": r[2],
                "course_pk": r[3],
                "syllabus_pdf": r[4],
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/Sub/subjects/")
def create_subject(subject_code: str, subject_name: str, course_name: str, syllabus_pdf: str = None):
    """
    Create a new subject by selecting course name.
    Backend resolves course_pk internally.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Resolve course_pk from course name
        cursor.execute("SELECT course_pk FROM Course WHERE course_name = ?", (course_name,))
        course_row = cursor.fetchone()
        if not course_row:
            raise HTTPException(status_code=400, detail="Invalid course name: Course does not exist")

        course_pk = course_row[0]

        cursor.execute(
            "INSERT INTO Subject (subject_code, subject_name, course_pk, syllabus_pdf) VALUES (?, ?, ?, ?)",
            (subject_code, subject_name, course_pk, syllabus_pdf),
        )
        conn.commit()
        return {"message": "Subject created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.put("/Sub/subjects/{subject_code}")
def update_subject(subject_code: str, new_subject_name: str = None, new_course_name: str = None, new_syllabus_pdf: str = None):
    """
    Update an existing subject by subject_code.
    If new_course_name is provided, resolve course_pk internally.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if new_subject_name:
            cursor.execute("UPDATE Subject SET subject_name = ? WHERE subject_code = ?", (new_subject_name, subject_code))
        if new_syllabus_pdf:
            cursor.execute("UPDATE Subject SET syllabus_pdf = ? WHERE subject_code = ?", (new_syllabus_pdf, subject_code))
        if new_course_name:
            cursor.execute("SELECT course_pk FROM Course WHERE course_name = ?", (new_course_name,))
            course_row = cursor.fetchone()
            if not course_row:
                raise HTTPException(status_code=400, detail="Invalid course name: Course does not exist")
            course_pk = course_row[0]
            cursor.execute("UPDATE Subject SET course_pk = ? WHERE subject_code = ?", (course_pk, subject_code))
        conn.commit()
        return {"message": "Subject updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/Sub/subjects/{subject_code}")
def delete_subject(subject_code: str):
    """Delete a subject by subject_code (no PK typing required)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Subject WHERE subject_code = ?", (subject_code,))
        conn.commit()
        return {"message": "Subject deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
##
## faculty
@router.get("/fc/faculties/")
def list_faculties():
    """List all faculty members."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT faculty_pk, name, email, designation, dept_pk FROM Faculty")
        rows = cursor.fetchall()
        return [
            {"faculty_pk": r[0], "name": r[1], "email": r[2], "designation": r[3], "dept_pk": r[4]}
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/fc/faculties/")
def create_faculty(name: str, email: str, designation: str, dept_name: str):
    """Create a new faculty by selecting department name."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT dept_pk FROM Department WHERE dept_name = ?", (dept_name,))
        dept_row = cursor.fetchone()
        if not dept_row:
            raise HTTPException(status_code=400, detail="Invalid department name: Department does not exist")
        dept_pk = dept_row[0]

        cursor.execute(
            "INSERT INTO Faculty (name, email, designation, dept_pk) VALUES (?, ?, ?, ?)",
            (name, email, designation, dept_pk),
        )
        conn.commit()
        return {"message": "Faculty created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

## faculty
@router.put("/fc/faculties/{email}")
def update_faculty(email: str, new_name: str = None, new_designation: str = None, new_dept_name: str = None):
    """Update faculty by email. Resolve dept_pk internally if department changes."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if new_name:
            cursor.execute("UPDATE Faculty SET name = ? WHERE email = ?", (new_name, email))
        if new_designation:
            cursor.execute("UPDATE Faculty SET designation = ? WHERE email = ?", (new_designation, email))
        if new_dept_name:
            cursor.execute("SELECT dept_pk FROM Department WHERE dept_name = ?", (new_dept_name,))
            dept_row = cursor.fetchone()
            if not dept_row:
                raise HTTPException(status_code=400, detail="Invalid department name")
            dept_pk = dept_row[0]
            cursor.execute("UPDATE Faculty SET dept_pk = ? WHERE email = ?", (dept_pk, email))
        conn.commit()
        return {"message": "Faculty updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/fc/faculties/{email}")
def delete_faculty(email: str):
    """Delete faculty by email."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Faculty WHERE email = ?", (email,))
        conn.commit()
        return {"message": "Faculty deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

## student
@router.get("/st/students/")
def list_students():
    """List all students."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT student_pk, roll_no, batch, phone_number, dept_pk FROM Student")
        rows = cursor.fetchall()
        return [
            {"student_pk": r[0], "roll_no": r[1], "batch": r[2], "phone_number": r[3], "dept_pk": r[4]}
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/st/students/")
def create_student(roll_no: str, batch: str, phone_number: str, dept_name: str):
    """Create a new student by selecting department name."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT dept_pk FROM Department WHERE dept_name = ?", (dept_name,))
        dept_row = cursor.fetchone()
        if not dept_row:
            raise HTTPException(status_code=400, detail="Invalid department name: Department does not exist")
        dept_pk = dept_row[0]

        cursor.execute(
            "INSERT INTO Student (roll_no, batch, phone_number, dept_pk) VALUES (?, ?, ?, ?)",
            (roll_no, batch, phone_number, dept_pk),
        )
        conn.commit()
        return {"message": "Student created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@router.put("/st/students/{roll_no}")
def update_student(roll_no: str, new_batch: str = None, new_phone_number: str = None, new_dept_name: str = None):
    """Update student by roll number. Resolve dept_pk internally if department changes."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if new_batch:
            cursor.execute("UPDATE Student SET batch = ? WHERE roll_no = ?", (new_batch, roll_no))
        if new_phone_number:
            cursor.execute("UPDATE Student SET phone_number = ? WHERE roll_no = ?", (new_phone_number, roll_no))
        if new_dept_name:
            cursor.execute("SELECT dept_pk FROM Department WHERE dept_name = ?", (new_dept_name,))
            dept_row = cursor.fetchone()
            if not dept_row:
                raise HTTPException(status_code=400, detail="Invalid department name")
            dept_pk = dept_row[0]
            cursor.execute("UPDATE Student SET dept_pk = ? WHERE roll_no = ?", (dept_pk, roll_no))
        conn.commit()
        return {"message": "Student updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/st/students/{roll_no}")
def delete_student(roll_no: str):
    """Delete student by roll number."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Student WHERE roll_no = ?", (roll_no,))
        conn.commit()
        return {"message": "Student deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


## hod
@router.get("/hd/hods/")
def list_hods():
    """List all HODs."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT hod_pk, dept_pk, faculty_pk FROM HOD")
        rows = cursor.fetchall()
        return [
            {"hod_pk": r[0], "dept_pk": r[1], "faculty_pk": r[2]}
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/hd/hods/")
def create_hod(dept_name: str, faculty_email: str):
    """Assign a faculty as HOD by selecting department name and faculty email."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Resolve dept_pk
        cursor.execute("SELECT dept_pk FROM Department WHERE dept_name = ?", (dept_name,))
        dept_row = cursor.fetchone()
        if not dept_row:
            raise HTTPException(status_code=400, detail="Invalid department name: Department does not exist")
        dept_pk = dept_row[0]

        # Resolve faculty_pk
        cursor.execute("SELECT faculty_pk FROM Faculty WHERE email = ?", (faculty_email,))
        faculty_row = cursor.fetchone()
        if not faculty_row:
            raise HTTPException(status_code=400, detail="Invalid faculty email: Faculty does not exist")
        faculty_pk = faculty_row[0]

        cursor.execute(
            "INSERT INTO HOD (dept_pk, faculty_pk) VALUES (?, ?)",
            (dept_pk, faculty_pk),
        )
        conn.commit()
        return {"message": "HOD assigned successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


## student


## hod
@router.put("/hd/hods/{dept_name}")
def update_hod(dept_name: str, new_faculty_email: str):
    """Update HOD assignment by department name. Resolve faculty_pk internally."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Resolve dept_pk
        cursor.execute("SELECT dept_pk FROM Department WHERE dept_name = ?", (dept_name,))
        dept_row = cursor.fetchone()
        if not dept_row:
            raise HTTPException(status_code=400, detail="Invalid department name")
        dept_pk = dept_row[0]

        # Resolve faculty_pk
        cursor.execute("SELECT faculty_pk FROM Faculty WHERE email = ?", (new_faculty_email,))
        faculty_row = cursor.fetchone()
        if not faculty_row:
            raise HTTPException(status_code=400, detail="Invalid faculty email")
        faculty_pk = faculty_row[0]

        cursor.execute("UPDATE HOD SET faculty_pk = ? WHERE dept_pk = ?", (faculty_pk, dept_pk))
        conn.commit()
        return {"message": "HOD updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/hd/hods/{dept_name}")
def delete_hod(dept_name: str):
    """Delete HOD assignment by department name."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM HOD WHERE dept_pk = (SELECT dept_pk FROM Department WHERE dept_name = ?)", (dept_name,))
        conn.commit()
        return {"message": "HOD deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
