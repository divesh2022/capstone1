/*
Overview
This SQL script defines views for the Campus ERP database. Views are virtual tables created from queries that simplify access to complex data relationships. They allow administrators, faculty, and developers to query consolidated information without repeatedly writing joins across multiple tables.

Key Components
🔹 Student Views
vw_students  
Provides a consolidated view of student records.

Includes: student_id, roll_no, name, dept_name, course_name, branch_name, semester.

Joins: student ↔ department ↔ course ↔ branch.

🔹 Faculty Views
vw_faculties  
Displays faculty details along with department and subject associations.

Includes: faculty_id, faculty_name, dept_name, subject_name.

Joins: faculty ↔ department ↔ subject.

🔹 Department Views
vw_departments  
Lists departments with their associated courses and branches.

Includes: dept_id, dept_name, course_name, branch_name.

🔹 Subject Views
vw_subjects  
Provides subject details linked to courses and semesters.

Includes: subject_id, subject_name, course_name, semester.

🔹 Exam & Marks Views
vw_mst_exams  
Displays MST exam details with subject and faculty linkage.

Includes: exam_id, exam_type, exam_date, subject_name, faculty_name.

vw_mst_exam_marks  
Consolidates MST exam marks with student and exam details.

Includes: exam_id, student_name, roll_no, marks, faculty_name.

🔹 Assignment Views
vw_assignments  
Shows assignment metadata with subject and faculty linkage.

Includes: assignment_id, title, description, due_date, subject_name, faculty_name.

vw_assignment_marks  
Displays assignment marks linked to students and assignments.

Includes: assignment_id, student_name, roll_no, marks, faculty_name.

🔹 Attendance Views
vw_attendance  
Provides detailed attendance records per student and subject.

Includes: student_name, roll_no, subject_name, date, status.

vw_attendance_aggregate  
Summarizes attendance data for reporting.

Includes: student_name, roll_no, subject_name, lectures_attended, total_lectures.    */
use [campus];
CREATE OR ALTER VIEW dbo.vw_total_internal_marks AS
WITH assignment_avg AS (
    SELECT
        st.roll_no,
        sub.subject_code,
        a.semester,
        AVG(CAST(am.marks AS FLOAT)
            / NULLIF(CAST(a.total_marks AS FLOAT),0)) AS avg_assign_frac
    FROM dbo.AssignmentMarks am
    JOIN dbo.Assignment a
        ON am.assignment_pk = a.assignment_pk
    JOIN dbo.Student st
        ON am.student_pk = st.student_pk
    JOIN dbo.Subject sub
        ON a.subject_pk = sub.subject_pk
    GROUP BY st.roll_no, sub.subject_code, a.semester
),
mst_ranked AS (
    SELECT
        st.roll_no,
        sub.subject_code,
        me.semester,
        mem.marks,
        me.total_marks,
        ROW_NUMBER() OVER (
            PARTITION BY st.roll_no, sub.subject_code, me.semester
            ORDER BY me.exam_date
        ) AS rn
    FROM dbo.MSTExamMarks mem
    JOIN dbo.MSTExam me
        ON mem.exam_pk = me.exam_pk
    JOIN dbo.Student st
        ON mem.student_pk = st.student_pk
    JOIN dbo.Subject sub
        ON me.subject_pk = sub.subject_pk
)
SELECT
    st.roll_no,
    sub.subject_code,
    aa.semester,
    d.dept_id,

    -- attendance component
    ROUND(5.0 * (CAST(aa.lectures_attended AS FLOAT)
                 / NULLIF(CAST(aa.total_lectures AS FLOAT),0)), 2)
        AS attendance_marks,

    -- assignment component
    ROUND(15.0 * COALESCE(a.avg_assign_frac, 0.0), 2) AS assignment_marks,

    -- MST‑1
    ROUND(10.0 * COALESCE(CAST(m1.marks AS FLOAT)
                 / NULLIF(CAST(m1.total_marks AS FLOAT),0), 0.0), 2)
        AS mst1_marks,

    -- MST‑2
    ROUND(10.0 * COALESCE(CAST(m2.marks AS FLOAT)
                 / NULLIF(CAST(m2.total_marks AS FLOAT),0), 0.0), 2)
        AS mst2_marks,

    -- total and status
    ROUND(
        (5.0 * (CAST(aa.lectures_attended AS FLOAT)
                / NULLIF(CAST(aa.total_lectures AS FLOAT),0))) +
        (15.0 * COALESCE(a.avg_assign_frac, 0.0)) +
        (10.0 * COALESCE(CAST(m1.marks AS FLOAT)
                         / NULLIF(CAST(m1.total_marks AS FLOAT),0),0.0)) +
        (10.0 * COALESCE(CAST(m2.marks AS FLOAT)
                         / NULLIF(CAST(m2.total_marks AS FLOAT),0),0.0))
    , 2) AS total_internal_marks,

    CASE WHEN ROUND(
        (5.0 * (CAST(aa.lectures_attended AS FLOAT)
                / NULLIF(CAST(aa.total_lectures AS FLOAT),0))) +
        (15.0 * COALESCE(a.avg_assign_frac, 0.0)) +
        (10.0 * COALESCE(CAST(m1.marks AS FLOAT)
                         / NULLIF(CAST(m1.total_marks AS FLOAT),0),0.0)) +
        (10.0 * COALESCE(CAST(m2.marks AS FLOAT)
                         / NULLIF(CAST(m2.total_marks AS FLOAT),0),0.0))
    , 2) < 16 THEN 'DETAIN' ELSE 'PASS' END AS status

FROM dbo.AttendanceAggregate aa
JOIN dbo.Student st
    ON aa.student_pk = st.student_pk
JOIN dbo.Subject sub
    ON aa.subject_pk = sub.subject_pk
JOIN dbo.Department d
    ON st.dept_pk = d.dept_pk
LEFT JOIN assignment_avg a
    ON st.roll_no = a.roll_no
   AND sub.subject_code = a.subject_code
   AND aa.semester = a.semester
LEFT JOIN mst_ranked m1
    ON st.roll_no = m1.roll_no
   AND sub.subject_code = m1.subject_code
   AND aa.semester = m1.semester
   AND m1.rn = 1
LEFT JOIN mst_ranked m2
    ON st.roll_no = m2.roll_no
   AND sub.subject_code = m2.subject_code
   AND aa.semester = m2.semester
   AND m2.rn = 2;
GO

create view BatchSemester AS
SELECT DISTINCT
    s.batch,
    ci.semester
FROM Student s
JOIN Class cl     ON cl.batch = s.batch AND cl.dept_pk = s.dept_pk
JOIN ClassIncharge ci ON ci.class_pk = cl.class_pk;
select * from vw_total_internal_marks;
