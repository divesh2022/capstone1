/*
 Overview
This SQL script provides read-only queries to inspect and verify the data stored in the Campus ERP database. It is primarily used for debugging, validation, and reporting purposes, allowing administrators and developers to quickly view records across different tables.

Key Components
🔹 Student Records
SELECT * FROM student;  
Displays all student records including roll number, name, department, course, branch, and semester.

🔹 Faculty Records
SELECT * FROM faculty;  
Retrieves faculty details such as faculty ID, name, department, and assigned subjects.

🔹 Department Records
SELECT * FROM department;  
Lists all departments with their IDs and names.

🔹 Course & Branch Records
SELECT * FROM course;  
Shows available courses linked to departments.

SELECT * FROM branch;  
Displays branches linked to courses.

🔹 Subject Records
SELECT * FROM subject;  
Retrieves subject details including subject code, name, course, and semester.

🔹 Attendance Records
SELECT * FROM attendance;  
Displays individual attendance entries for students.

SELECT * FROM attendance_aggregate;  
Shows summarized attendance data (lectures attended vs. total lectures).

🔹 Exam & Marks Records
SELECT * FROM mst_exam;  
Lists MST exam details (exam type, date, subject, faculty).

SELECT * FROM mst_exam_marks;  
Displays marks awarded in MST exams.

🔹 Assignment Records
SELECT * FROM assignment;  
Shows assignment metadata (title, description, due date, subject).

SELECT * FROM assignment_marks;  
Displays marks awarded for assignments.

🔹 Administrative Records
SELECT * FROM hod;  
Lists Heads of Departments linked to faculty and departments.

SELECT * FROM role;  
Displays system roles (Admin, Faculty, Student).

SELECT * FROM user;  
Shows login credentials and role associations.

SELECT * FROM correction;  
Displays correction records made by faculty for student data.           */
            
use [campus];
-- basic dumps
SELECT * FROM Roles;
SELECT * FROM Users;
SELECT * FROM UserRoles;
SELECT * FROM College;
SELECT * FROM Department;
SELECT * FROM Branch;
SELECT * FROM Course;
SELECT * FROM Subject;
SELECT * FROM Faculty;
SELECT * FROM Student;
SELECT * FROM HOD;
SELECT * FROM Class;
SELECT * FROM ClassIncharge;
SELECT * FROM Attendance;
SELECT * FROM AttendanceAggregate;
SELECT * FROM MSTExam;
SELECT * FROM MSTExamMarks;
SELECT * FROM Assignment;
SELECT * FROM AssignmentMarks;
SELECT * FROM FacultySubject;

            SELECT c.class_pk, c.batch, d.dept_name
            FROM Class c
            JOIN Department d ON c.dept_pk = d.dept_pk;

            

-- a few examples with joins to show relationships
SELECT u.user_pk, u.username, r.role_name
FROM Users u
JOIN UserRoles ur ON u.user_pk = ur.user_pk
JOIN Roles r ON ur.role_pk = r.role_pk;

-- departments with their college
SELECT d.dept_id, d.dept_name, c.college_name
FROM Department d
JOIN College c ON d.college_pk = c.college_pk;

-- branches including computed code
SELECT b.branch_pk, b.branch_id, b.branch_name, b.dept_id, b.branch_code
FROM Branch b;

-- students with their department and class (if any)
SELECT s.roll_no, s.batch, d.dept_name, cl.batch AS class_batch
FROM Student s
LEFT JOIN Department d ON s.dept_pk = d.dept_pk
LEFT JOIN Class cl ON s.batch = cl.batch AND s.dept_pk = cl.dept_pk;

-- attendance records with student and subject names
SELECT a.date, s.roll_no, subj.subject_name, a.status
FROM Attendance a
JOIN Student  s   ON a.student_pk = s.student_pk
JOIN Subject  subj ON a.subject_pk = subj.subject_pk;

-- …etc. tailor the `SELECT … JOIN …` queries to whatever output you need.
-- class list with their in‑charge and department
SELECT 
    cl.class_pk,
    cl.batch,
    d.dept_name,
    f.name      AS incharge_name,
    ci.semester
FROM Class cl
JOIN Department d    ON cl.dept_pk = d.dept_pk
LEFT JOIN ClassIncharge ci ON ci.class_pk = cl.class_pk
LEFT JOIN Faculty f  ON ci.faculty_pk = f.faculty_pk;

-- students and their current class‑in‑charge faculty (via batch/dept match)
SELECT 
    s.student_pk,
    s.roll_no,
    s.batch,
    d.dept_name,
    f.name                AS class_incharge
FROM Student s
JOIN Department d      ON s.dept_pk = d.dept_pk
LEFT JOIN Class cl     ON cl.batch = s.batch AND cl.dept_pk = s.dept_pk
LEFT JOIN ClassIncharge ci ON ci.class_pk = cl.class_pk
LEFT JOIN Faculty f    ON ci.faculty_pk = f.faculty_pk;

-- attendance summary per subject, per student
SELECT
    s.roll_no,
    subj.subject_name,
    COUNT(*)                           AS sessions,
    SUM(CAST(a.status AS INT))         AS attended
FROM Attendance a
JOIN Student s     ON a.student_pk   = s.student_pk
JOIN Subject subj ON a.subject_pk   = subj.subject_pk
GROUP BY s.roll_no, subj.subject_name;

-- attendance aggregates, with student and faculty names
SELECT
    agg.agg_pk,
    agg.student_pk,
    s.roll_no,
    subj.subject_name,
    agg.semester,
    f.name AS faculty,
    agg.lectures_attended,
    agg.total_lectures
FROM AttendanceAggregate agg
JOIN Student s   ON agg.student_pk = s.student_pk
JOIN Subject subj ON agg.subject_pk = subj.subject_pk
JOIN Faculty f   ON agg.faculty_pk = f.faculty_pk;

-- MST exam marks with exam info and student details
SELECT
    mm.exam_marks_pk,
    m.exam_pk,
    m.exam_name,
    m.exam_date,
    subj.subject_name,
    s.roll_no,
    s.batch,
    mm.marks
FROM MSTExam m
JOIN MSTExamMarks mm ON mm.exam_pk = m.exam_pk
JOIN Subject subj    ON m.subject_pk = subj.subject_pk
JOIN Student s       ON mm.student_pk = s.student_pk;

-- assignment marks with department and subject context
SELECT
    am.assignment_marks_pk,
    ass.assignment_pk,
    d.dept_name,
    subj.subject_name,
    ass.total_marks,
    am.marks,
    s.roll_no
FROM Assignment ass
JOIN Department d      ON ass.dept_pk = d.dept_pk
JOIN Subject subj      ON ass.subject_pk = subj.subject_pk
JOIN AssignmentMarks am ON am.assignment_pk = ass.assignment_pk
JOIN Student s         ON am.student_pk = s.student_pk;

-- faculty list with their department and any HOD role
SELECT
    f.faculty_pk,
    f.name,
    f.designation,
    d.dept_name,
    CASE WHEN h.hod_pk IS NOT NULL THEN 'Yes' ELSE 'No' END AS is_hod
FROM Faculty f
JOIN Department d ON f.dept_pk = d.dept_pk
LEFT JOIN HOD h   ON h.faculty_pk = f.faculty_pk;

-- users with their assigned role and any linked faculty/student record
SELECT
    u.user_pk,
    u.username,
    u.email,
    r.role_name,
    f.name      AS faculty_name,
    s.roll_no   AS student_roll
FROM Users u
JOIN UserRoles ur ON u.user_pk = ur.user_pk
JOIN Roles r ON ur.role_pk = r.role_pk
LEFT JOIN Faculty f ON f.email = u.email
LEFT JOIN Student s ON s.phone_number = u.phone_number;   -- or another join key

-- courses with branch and department
SELECT
    c.course_pk,
    c.course_code,
    c.course_name,
    b.branch_name,
    d.dept_name
FROM Course c
JOIN Branch b      ON c.branch_pk = b.branch_pk
JOIN Department d  ON b.dept_pk = d.dept_pk;
select * from vw_total_internal_marks;

select * from BatchSemester;

SELECT faculty_id, name, faculty_pk FROM Faculty

-- …add more queries as needed to explore the data and relationships in your database!
-- Comprehensive Student Profile
SELECT 
    s.roll_no, 
    s.batch, 
    d.dept_name, 
    u.username,
    cl.batch AS class_batch,
    f.name AS class_incharge
FROM Student s
JOIN Users u ON s.user_pk = u.user_pk
LEFT JOIN Department d ON s.dept_pk = d.dept_pk
LEFT JOIN Class cl ON s.batch = cl.batch AND s.dept_pk = cl.dept_pk
LEFT JOIN ClassIncharge ci ON ci.class_pk = cl.class_pk
LEFT JOIN Faculty f ON ci.faculty_pk = f.faculty_pk;

-- Student Performance (MST + Assignments)
SELECT 
    s.roll_no,
    subj.subject_name,
    m.exam_name,
    mm.marks AS mst_marks,
    am.marks AS assignment_marks
FROM Student s
JOIN MSTExamMarks mm ON s.student_pk = mm.student_pk
JOIN MSTExam m ON mm.exam_pk = m.exam_pk
JOIN Subject subj ON m.subject_pk = subj.subject_pk
LEFT JOIN AssignmentMarks am ON s.student_pk = am.student_pk AND subj.subject_pk = (SELECT subject_pk FROM Assignment WHERE assignment_pk = am.assignment_pk);
-- Faculty Teaching Load
-- Faculty List with HOD status and User Details
SELECT 
    f.faculty_pk, 
    f.name, 
    f.designation, 
    d.dept_name, 
    u.email,
    CASE WHEN h.hod_pk IS NOT NULL THEN 'Head of Dept' ELSE 'Teaching Staff' END AS staff_role
FROM Faculty f
JOIN Users u ON f.user_pk = u.user_pk
JOIN Department d ON f.dept_pk = d.dept_pk
LEFT JOIN HOD h ON h.faculty_pk = f.faculty_pk;

-- Faculty Teaching Load (Attendance they have marked)
SELECT 
    f.name, 
    subj.subject_name, 
    COUNT(DISTINCT a.date) AS sessions_taken
FROM Faculty f
JOIN Attendance a ON f.faculty_pk = a.faculty_pk
JOIN Subject subj ON a.subject_pk = subj.subject_pk
GROUP BY f.name, subj.subject_name;
-- Class Incharge List with their Classes and Departments
-- Organizational Hierarchy
SELECT 
    col.college_name, 
    d.dept_name, 
    b.branch_name, 
    b.branch_code, 
    c.course_name
FROM College col
JOIN Department d ON col.college_pk = d.college_pk
JOIN Branch b ON d.dept_pk = b.dept_pk
JOIN Course c ON b.branch_pk = c.branch_pk;

select * from UserRoles;

sp_help Users;
sp_help UserRoles;
sp_help Roles;

SELECT 
    u.email,
    r.role_name,
    ur.password_hash
FROM Users u
JOIN UserRoles ur ON u.user_pk = ur.user_pk
JOIN Roles r ON ur.role_pk = r.role_pk;

select * from Request;
select * from Accepted;
select * from Rejected;

SELECT a.assignment_pk, s.subject_name, a.dept_pk, a.semester, a.total_marks
FROM Assignment a
JOIN Subject s ON a.subject_pk = s.subject_pk
WHERE a.status = 0;

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
        WHERE e.status = 0;

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

select * from Request;
select * from Accepted;
select * from Rejected;
            SELECT sa.lectures_attended, sa.total_lectures
            FROM AttendanceAggregate sa
            JOIN Student st ON sa.student_pk = st.student_pk
            WHERE st.roll_no = 2025001;

SELECT cs.semester,st.roll_no FROM ClassStudent cs JOIN Student st ON cs.student_pk = st.student_pk where st.roll_no = '2025002';

select * from ClassSubject;

-- Verify subject allocations for a given batch and department
SELECT 
    cs.class_subject_pk,
    c.class_pk,
    c.batch,
    d.dept_name,
    s.subject_pk,
    s.subject_code,
    s.subject_name,
    cs.semester
FROM ClassSubject cs
JOIN Class c ON cs.class_pk = c.class_pk
JOIN Department d ON c.dept_pk = d.dept_pk
JOIN Subject s ON cs.subject_pk = s.subject_pk
WHERE c.batch = '2025' AND d.dept_name = 'Computer Science';
-- Insert dummy allocations into ClassSubject
INSERT INTO ClassSubject (class_pk, subject_pk, semester)
VALUES 
    (1, 1, 1),  -- Class 2025, Programming Basics, Semester 1
    (1, 2, 2);  -- Class 2025, Algorithms, Semester 2

SELECT subject_pk, subject_code, subject_name FROM Subject;
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
    ORDER BY c.batch, d.dept_name, ci.semester;

        SELECT subject_pk, subject_code, subject_name FROM Subject;
