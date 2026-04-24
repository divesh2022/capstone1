
# Campus ERP System – Capstone Project

## Overview
This repository contains the Campus ERP System, a modular application designed to streamline academic and administrative workflows for colleges and universities.  
It provides dashboards for different roles (Admin, HOD, Faculty, Student) and integrates with a backend database for managing courses, faculty, students, timetables, exams, attendance, and departmental decisions.

## Features
- Role-based Dashboards
  - Admin: Institution-wide management of users, roles, and departments.
  - HOD: Departmental workflows (faculty, courses, timetables, decisions).
  - Faculty: Attendance, exams, assignments, and student records.
  - Student: Attendance tracking, exam schedules, marks, corrections, and profile management.

- Database Integration
  - SQL scripts for schema, tables, views, data insertion, and modifications.
  - Referential integrity enforced with foreign keys and constraints.

- Frontend
  - Built with Streamlit for interactive dashboards.
  - Modular design: each workflow (attendance, timetable, exams, corrections, profile) is a separate file.

- Backend
  - RESTful APIs built with FastAPI.
  - Integration with SQL Server via pyodbc.

- Automation
  - Documentation scanner script to auto-generate text documentation from source code.
  - Supports multiple languages (.py, .js, .java, .c, .cpp, .ts, .sql).

## Repository Structure

```
capstone1/
├── .gitignore
├── .vscode/
│   └── settings.json
├── backend/
│   ├── __pycache__/
│   │   ├── admin.cpython-310.pyc
│   │   ├── assignment.cpython-310.pyc
│   │   ├── assignment_marks.cpython-310.pyc
│   │   ├── attendance_aggregate.cpython-310.pyc
│   │   ├── attendence.cpython-310.pyc
│   │   ├── connect.cpython-310.pyc
│   │   ├── correction.cpython-310.pyc
│   │   ├── faculty.cpython-310.pyc
│   │   ├── hod.cpython-310.pyc
│   │   ├── login.cpython-310.pyc
│   │   ├── main.cpython-310.pyc
│   │   ├── mst_exam.cpython-310.pyc
│   │   ├── mst_exam_marks.cpython-310.pyc
│   │   ├── student.cpython-310.pyc
│   │   └── view.cpython-310.pyc
│   ├── admin.py
│   ├── assignment.py
│   ├── assignment_marks.py
│   ├── attendance_aggregate.py
│   ├── attendence.py
│   ├── connect.py
│   ├── correction.py
│   ├── hod.py
│   ├── login.py
│   ├── main.py
│   ├── mst_exam.py
│   ├── mst_exam_marks.py
│   ├── student.py
│   └── view.py
├── database/
│   ├── ## GitHub Copilot Chat.md
│   ├── alter.sql
│   ├── data.sql
│   ├── database.sql
│   ├── drop.sql
│   ├── schema.sql
│   ├── show.sql
│   ├── t1.md
│   ├── table.sql
│   └── view.sql
├── doc.py
├── documentation.tex
├── documentation.txt
├── frontend/
│   ├── __init__.py
│   ├── __pycache__/
│   │   ├── __init__.cpython-310.pyc
│   │   ├── app.cpython-310.pyc
│   │   ├── assignment.cpython-310.pyc
│   │   ├── assignment_marks.cpython-310.pyc
│   │   ├── attendance_aggregate.cpython-310.pyc
│   │   ├── attendence.cpython-310.pyc
│   │   ├── login.cpython-310.pyc
│   │   ├── main.cpython-310.pyc
│   │   ├── mst_exam.cpython-310.pyc
│   │   ├── mst_exam_marks.cpython-310.pyc
│   │   └── view.cpython-310.pyc
│   ├── admin/
│   │   ├── __pycache__/
│   │   │   ├── branch.cpython-310.pyc
│   │   │   ├── course.cpython-310.pyc
│   │   │   ├── department.cpython-310.pyc
│   │   │   ├── faculty.cpython-310.pyc
│   │   │   ├── hod.cpython-310.pyc
│   │   │   ├── main.cpython-310.pyc
│   │   │   ├── query.cpython-310.pyc
│   │   │   ├── role.cpython-310.pyc
│   │   │   ├── student.cpython-310.pyc
│   │   │   ├── subject.cpython-310.pyc
│   │   │   ├── user.cpython-310.pyc
│   │   │   └── user_roles.cpython-310.pyc
│   │   ├── branch.py
│   │   ├── college.py
│   │   ├── course.py
│   │   ├── department.py
│   │   ├── faculty.py
│   │   ├── hod.py
│   │   ├── main.py
│   │   ├── query.py
│   │   ├── role.py
│   │   ├── student.py
│   │   ├── subject.py
│   │   ├── user.py
│   │   └── user_roles.py
│   ├── faculty/
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   │   ├── __init__.cpython-310.pyc
│   │   │   ├── a.cpython-310.pyc
│   │   │   ├── aa.cpython-310.pyc
│   │   │   ├── am.cpython-310.pyc
│   │   │   ├── ass.cpython-310.pyc
│   │   │   ├── assignment_marks.cpython-310.pyc
│   │   │   ├── attendance_aggregate.cpython-310.pyc
│   │   │   ├── main.cpython-310.pyc
│   │   │   ├── me.cpython-310.pyc
│   │   │   ├── mem.cpython-310.pyc
│   │   │   ├── mst_exam.cpython-310.pyc
│   │   │   ├── mst_exam_marks.cpython-310.pyc
│   │   │   ├── r.cpython-310.pyc
│   │   │   └── request.cpython-310.pyc
│   │   ├── a.py
│   │   ├── aa.py
│   │   ├── am.py
│   │   ├── ass.py
│   │   ├── main.py
│   │   ├── me.py
│   │   ├── mem.py
│   │   └── r.py
│   ├── hod/
│   │   ├── CF.py
│   │   ├── CS.py
│   │   ├── CSUB.py
│   │   ├── CSem.py
│   │   ├── Ci.py
│   │   ├── FS.py
│   │   ├── Tm.py
│   │   ├── __pycache__/
│   │   │   ├── CF.cpython-310.pyc
│   │   │   ├── CS.cpython-310.pyc
│   │   │   ├── CSUB.cpython-310.pyc
│   │   │   ├── CSem.cpython-310.pyc
│   │   │   ├── FS.cpython-310.pyc
│   │   │   ├── Tm.cpython-310.pyc
│   │   │   ├── decision.cpython-310.pyc
│   │   │   └── main.cpython-310.pyc
│   │   ├── decision.py
│   │   └── main.py
│   ├── login.py
│   ├── main.py
│   └── student/
│       ├── __pycache__/
│       │   ├── aa.cpython-310.pyc
│       │   ├── am.cpython-310.pyc
│       │   ├── main.cpython-310.pyc
│       │   ├── mm.cpython-310.pyc
│       │   ├── profile.cpython-310.pyc
│       │   └── tm.cpython-310.pyc
│       ├── aa.py
│       ├── am.py
│       ├── ci.py
│       ├── main.py
│       ├── mm.py
│       ├── profile.py
│       └── tm.py
├── marks_export.xlsx
├── marks_filtered.xlsx
└── uploads/
    ├── __pycache__/
    │   └── test.cpython-313.pyc
    └── test.csv
 
```

## Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/divesh2022/capstone1.git
   cd capstone1
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure database connection in backend (`backend/main.py`):
   - Update connection string for SQL Server.

4. Run backend:
   ```bash
   uvicorn backend.main:app --reload
   ```

5. Run frontend:
   ```bash
   streamlit run frontend/main.py
   ```

## Usage
- Login via `frontend/login.py`.
- Navigate to your role-specific dashboard.
- Perform CRUD operations on courses, faculty, students, timetables, and exams.
- Generate reports using SQL queries (`database/show.sql`).

## Documentation
- Auto-generated documentation is available via `documentation.txt` (produced by `utils/documentation_scanner.py`).
- SQL scripts are annotated with comments for schema design and data relationships.

## Author
Developed by Divesh Chauhan  
B.Tech Computer Science Engineering (AI & ML), JNGEC Himachal Pradesh
```

This version matches the file list you pulled from GitHub (`api.github.com/repos/divesh2022/capstone1/git/trees/main?recursive=1`) and is ready to drop into your repo as `README.md`.  

Would you like me to also add a **Future Enhancements** section (planned features like analytics dashboards, notifications, or mobile support) so the README looks more complete for GitHub?
