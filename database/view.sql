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
