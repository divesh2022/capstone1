SELECT name AS schema_name
FROM sys.schemas
ORDER BY name;

SELECT s.name AS schema_name,
       t.name AS table_name
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
ORDER BY s.name, t.name;

SELECT s.name AS schema_name,
       t.name AS table_name,
       c.name AS column_name,
       ty.name AS data_type,
       c.max_length,
       c.is_nullable
FROM sys.columns c
JOIN sys.tables t ON c.object_id = t.object_id
JOIN sys.schemas s ON t.schema_id = s.schema_id
JOIN sys.types ty ON c.user_type_id = ty.user_type_id
ORDER BY s.name, t.name, c.column_id;

SELECT s.name AS schema_name,
       t.name AS table_name,
       c.name AS column_name
FROM sys.indexes i
JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
JOIN sys.tables t ON i.object_id = t.object_id
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE i.is_primary_key = 1
ORDER BY s.name, t.name;

SELECT fk.name AS foreign_key_name,
       sch1.name AS schema_name,
       t1.name AS table_name,
       c1.name AS column_name,
       sch2.name AS referenced_schema,
       t2.name AS referenced_table,
       c2.name AS referenced_column
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
JOIN sys.tables t1 ON fkc.parent_object_id = t1.object_id
JOIN sys.columns c1 ON fkc.parent_object_id = c1.object_id AND fkc.parent_column_id = c1.column_id
JOIN sys.schemas sch1 ON t1.schema_id = sch1.schema_id
JOIN sys.tables t2 ON fkc.referenced_object_id = t2.object_id
JOIN sys.columns c2 ON fkc.referenced_object_id = c2.object_id AND fkc.referenced_column_id = c2.column_id
JOIN sys.schemas sch2 ON t2.schema_id = sch2.schema_id
ORDER BY sch1.name, t1.name;


-- Generate Graphviz DOT text for tables and foreign keys
WITH Tables AS (
    SELECT t.object_id, s.name AS schema_name, t.name AS table_name
    FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
),
Columns AS (
    SELECT c.object_id, c.column_id, c.name AS column_name, ty.name AS data_type
    FROM sys.columns c
    JOIN sys.types ty ON c.user_type_id = ty.user_type_id
),
PKs AS (
    SELECT ic.object_id, ic.column_id
    FROM sys.indexes i
    JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
    WHERE i.is_primary_key = 1
),
FKs AS (
    SELECT fk.name AS fk_name,
           sch1.name AS schema_name,
           t1.name AS table_name,
           c1.name AS column_name,
           sch2.name AS ref_schema,
           t2.name AS ref_table,
           c2.name AS ref_column
    FROM sys.foreign_keys fk
    JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
    JOIN sys.tables t1 ON fkc.parent_object_id = t1.object_id
    JOIN sys.columns c1 ON fkc.parent_object_id = c1.object_id AND fkc.parent_column_id = c1.column_id
    JOIN sys.schemas sch1 ON t1.schema_id = sch1.schema_id
    JOIN sys.tables t2 ON fkc.referenced_object_id = t2.object_id
    JOIN sys.columns c2 ON fkc.referenced_object_id = c2.object_id AND fkc.referenced_column_id = c2.column_id
    JOIN sys.schemas sch2 ON t2.schema_id = sch2.schema_id
)
SELECT 'digraph G {' UNION ALL
-- Nodes for tables
SELECT '  "' + schema_name + '.' + table_name + '" [shape=box];'
FROM Tables
UNION ALL
-- Edges for foreign keys
SELECT '  "' + schema_name + '.' + table_name + '" -> "' +
       ref_schema + '.' + ref_table + '" [label="' + column_name + '→' + ref_column + '"];'
FROM FKs
UNION ALL
SELECT '}'


-- Generate Mermaid entity blocks for all user tables
SELECT 
    '    ' + t.name + ' {' + CHAR(13) +
    STRING_AGG(
        '        ' + c.name + ' ' + ty.name +
        CASE 
            WHEN pk.column_id IS NOT NULL THEN ' PK'
            WHEN fk.parent_column_id IS NOT NULL THEN ' FK'
            ELSE ''
        END, CHAR(13)
    ) 
    + CHAR(13) + '    }' AS mermaid_entity
FROM sys.tables t
JOIN sys.columns c ON t.object_id = c.object_id
JOIN sys.types ty ON c.user_type_id = ty.user_type_id
LEFT JOIN (
    SELECT ic.object_id, ic.column_id
    FROM sys.indexes i
    JOIN sys.index_columns ic 
      ON i.object_id = ic.object_id AND i.index_id = ic.index_id
    WHERE i.is_primary_key = 1
) pk ON c.object_id = pk.object_id AND c.column_id = pk.column_id
LEFT JOIN (
    SELECT k.parent_object_id, k.parent_column_id
    FROM sys.foreign_key_columns k
) fk ON c.object_id = fk.parent_object_id AND c.column_id = fk.parent_column_id
WHERE t.type = 'U'
GROUP BY t.name;

/*
Result Set Batch 1 - Query 1
========================================

schema_name       
------------------
db_accessadmin    
db_backupoperator 
db_datareader     
db_datawriter     
db_ddladmin       
db_denydatareader 
db_denydatawriter 
db_owner          
db_securityadmin  
dbo               
guest             
INFORMATION_SCHEMA
sys               
((13 rows affected))

Result Set Batch 1 - Query 2
========================================

schema_name  table_name         
-----------  -------------------
dbo          Accepted           
dbo          Assignment         
dbo          AssignmentMarks    
dbo          Attendance         
dbo          AttendanceAggregate
dbo          Branch             
dbo          Class              
dbo          ClassFaculty       
dbo          ClassIncharge      
dbo          ClassStudent       
dbo          ClassSubject       
dbo          College            
dbo          Course             
dbo          Department         
dbo          Faculty            
dbo          FacultySubject     
dbo          HOD                
dbo          MSTExam            
dbo          MSTExamMarks       
dbo          Rejected           
dbo          Request            
dbo          Roles              
dbo          Student            
dbo          Subject            
dbo          UserRoles          
dbo          Users              
((26 rows affected))

Result Set Batch 1 - Query 3
========================================

schema_name  table_name           column_name          data_type   max_length  is_nullable
-----------  -------------------  -------------------  ----------  ----------  -----------
dbo          Accepted             accepted_id          int         4           0          
dbo          Accepted             request_id           int         4           0          
dbo          Accepted             hod_pk               int         4           0          
dbo          Accepted             reason               nvarchar    -1          1          
dbo          Accepted             accepted_at          datetime    8           1          
dbo          Assignment           assignment_pk        int         4           0          
dbo          Assignment           dept_pk              int         4           1          
dbo          Assignment           subject_pk           int         4           1          
dbo          Assignment           semester             int         4           1          
dbo          Assignment           assignment_pdf       nvarchar    -1          1          
dbo          Assignment           total_marks          int         4           1          
dbo          Assignment           faculty_pk           int         4           1          
dbo          Assignment           status               bit         1           0          
dbo          AssignmentMarks      assignment_marks_pk  int         4           0          
dbo          AssignmentMarks      assignment_pk        int         4           1          
dbo          AssignmentMarks      student_pk           int         4           1          
dbo          AssignmentMarks      marks                int         4           1          
dbo          AssignmentMarks      faculty_pk           int         4           1          
dbo          AssignmentMarks      status               bit         1           0          
dbo          Attendance           attendance_pk        int         4           0          
dbo          Attendance           class_pk             int         4           1          
dbo          Attendance           subject_pk           int         4           1          
dbo          Attendance           faculty_pk           int         4           1          
dbo          Attendance           student_pk           int         4           1          
dbo          Attendance           date                 date        3           1          
dbo          Attendance           status               bit         1           1          
dbo          AttendanceAggregate  agg_pk               int         4           0          
dbo          AttendanceAggregate  student_pk           int         4           1          
dbo          AttendanceAggregate  subject_pk           int         4           1          
dbo          AttendanceAggregate  semester             int         4           1          
dbo          AttendanceAggregate  faculty_pk           int         4           1          
dbo          AttendanceAggregate  lectures_attended    int         4           1          
dbo          AttendanceAggregate  total_lectures       int         4           1          
dbo          Branch               branch_pk            int         4           0          
dbo          Branch               branch_id            nvarchar    20          0          
dbo          Branch               branch_name          nvarchar    200         0          
dbo          Branch               dept_pk              int         4           1          
dbo          Branch               dept_id              nvarchar    20          0          
dbo          Branch               branch_code          nvarchar    40          0          
dbo          Class                class_pk             int         4           0          
dbo          Class                batch                nvarchar    20          1          
dbo          Class                dept_pk              int         4           1          
dbo          Class                semester             int         4           1          
dbo          ClassFaculty         class_faculty_pk     int         4           0          
dbo          ClassFaculty         class_pk             int         4           1          
dbo          ClassFaculty         faculty_pk           int         4           1          
dbo          ClassFaculty         semester             int         4           0          
dbo          ClassIncharge        class_incharge_pk    int         4           0          
dbo          ClassIncharge        class_pk             int         4           1          
dbo          ClassIncharge        faculty_pk           int         4           1          
dbo          ClassIncharge        semester             int         4           1          
dbo          ClassStudent         class_student_pk     int         4           0          
dbo          ClassStudent         class_pk             int         4           1          
dbo          ClassStudent         student_pk           int         4           1          
dbo          ClassStudent         semester             int         4           0          
dbo          ClassSubject         class_subject_pk     int         4           0          
dbo          ClassSubject         class_pk             int         4           1          
dbo          ClassSubject         subject_pk           int         4           1          
dbo          ClassSubject         semester             int         4           0          
dbo          College              college_pk           int         4           0          
dbo          College              college_id           nvarchar    20          0          
dbo          College              college_name         nvarchar    200         0          
dbo          Course               course_pk            int         4           0          
dbo          Course               course_code          nvarchar    20          0          
dbo          Course               course_name          nvarchar    200         0          
dbo          Course               branch_pk            int         4           1          
dbo          Department           dept_pk              int         4           0          
dbo          Department           dept_id              nvarchar    20          0          
dbo          Department           dept_name            nvarchar    200         0          
dbo          Department           college_pk           int         4           1          
dbo          Faculty              faculty_pk           int         4           0          
dbo          Faculty              dept_pk              int         4           1          
dbo          Faculty              email                nvarchar    200         0          
dbo          Faculty              name                 nvarchar    200         0          
dbo          Faculty              designation          nvarchar    100         1          
dbo          Faculty              user_pk              int         4           1          
dbo          FacultySubject       faculty_subject_pk   int         4           0          
dbo          FacultySubject       faculty_pk           int         4           1          
dbo          FacultySubject       subject_pk           int         4           1          
dbo          FacultySubject       semester             int         4           0          
dbo          HOD                  hod_pk               int         4           0          
dbo          HOD                  dept_pk              int         4           1          
dbo          HOD                  faculty_pk           int         4           1          
dbo          MSTExam              exam_pk              int         4           0          
dbo          MSTExam              dept_pk              int         4           1          
dbo          MSTExam              subject_pk           int         4           1          
dbo          MSTExam              semester             int         4           1          
dbo          MSTExam              exam_date            date        3           1          
dbo          MSTExam              exam_pdf             nvarchar    -1          1          
dbo          MSTExam              total_marks          int         4           1          
dbo          MSTExam              exam_name            nvarchar    20          0          
dbo          MSTExam              faculty_pk           int         4           1          
dbo          MSTExam              status               bit         1           0          
dbo          MSTExamMarks         exam_marks_pk        int         4           0          
dbo          MSTExamMarks         exam_pk              int         4           1          
dbo          MSTExamMarks         student_pk           int         4           1          
dbo          MSTExamMarks         marks                int         4           1          
dbo          MSTExamMarks         faculty_pk           int         4           1          
dbo          Rejected             rejected_id          int         4           0          
dbo          Rejected             request_id           int         4           0          
dbo          Rejected             hod_pk               int         4           0          
dbo          Rejected             reason               nvarchar    -1          1          
dbo          Rejected             rejected_at          datetime    8           1          
dbo          Request              request_id           int         4           0          
dbo          Request              user_pk              int         4           0          
dbo          Request              service_type         nvarchar    100         0          
dbo          Request              field_name           nvarchar    200         0          
dbo          Request              old_value            nvarchar    510         1          
dbo          Request              new_value            nvarchar    510         0          
dbo          Request              status               nvarchar    40          0          
dbo          Request              submitted_at         datetime    8           1          
dbo          Request              target_pk            int         4           0          
dbo          Roles                role_pk              int         4           0          
dbo          Roles                role_name            nvarchar    100         0          
dbo          Student              student_pk           int         4           0          
dbo          Student              roll_no              nvarchar    30          0          
dbo          Student              batch                nvarchar    20          1          
dbo          Student              dept_pk              int         4           1          
dbo          Student              phone_number         nvarchar    30          1          
dbo          Student              user_pk              int         4           1          
dbo          Subject              subject_pk           int         4           0          
dbo          Subject              subject_code         nvarchar    20          0          
dbo          Subject              subject_name         nvarchar    200         0          
dbo          Subject              course_pk            int         4           1          
dbo          Subject              syllabus_pdf         nvarchar    -1          1          
dbo          UserRoles            user_role_pk         int         4           0          
dbo          UserRoles            user_pk              int         4           0          
dbo          UserRoles            role_pk              int         4           0          
dbo          UserRoles            password_hash        nvarchar    512         0          
dbo          Users                user_pk              int         4           0          
dbo          Users                email                nvarchar    200         0          
dbo          Users                username             nvarchar    100         0          
dbo          Users                phone_number         nvarchar    30          1          
((133 rows affected))

Result Set Batch 1 - Query 4
========================================

schema_name  table_name           column_name        
-----------  -------------------  -------------------
dbo          Accepted             accepted_id        
dbo          Assignment           assignment_pk      
dbo          AssignmentMarks      assignment_marks_pk
dbo          Attendance           attendance_pk      
dbo          AttendanceAggregate  agg_pk             
dbo          Branch               branch_pk          
dbo          Class                class_pk           
dbo          ClassFaculty         class_faculty_pk   
dbo          ClassIncharge        class_incharge_pk  
dbo          ClassStudent         class_student_pk   
dbo          ClassSubject         class_subject_pk   
dbo          College              college_pk         
dbo          Course               course_pk          
dbo          Department           dept_pk            
dbo          Faculty              faculty_pk         
dbo          FacultySubject       faculty_subject_pk 
dbo          HOD                  hod_pk             
dbo          MSTExam              exam_pk            
dbo          MSTExamMarks         exam_marks_pk      
dbo          Rejected             rejected_id        
dbo          Request              request_id         
dbo          Roles                role_pk            
dbo          Student              student_pk         
dbo          Subject              subject_pk         
dbo          UserRoles            user_role_pk       
dbo          Users                user_pk            
((26 rows affected))

Result Set Batch 1 - Query 5
========================================

foreign_key_name                schema_name  table_name           column_name    referenced_schema  referenced_table  referenced_column
------------------------------  -----------  -------------------  -------------  -----------------  ----------------  -----------------
FK__Accepted__hod_pk__6CD828CA  dbo          Accepted             hod_pk         dbo                HOD               hod_pk           
FK__Accepted__reques__6BE40491  dbo          Accepted             request_id     dbo                Request           request_id       
FK__Assignmen__facul__3E1D39E1  dbo          Assignment           faculty_pk     dbo                Faculty           faculty_pk       
FK__Assignmen__dept___74AE54BC  dbo          Assignment           dept_pk        dbo                Department        dept_pk          
FK__Assignmen__subje__75A278F5  dbo          Assignment           subject_pk     dbo                Subject           subject_pk       
FK__Assignmen__facul__40058253  dbo          AssignmentMarks      faculty_pk     dbo                Faculty           faculty_pk       
FK__Assignmen__stude__797309D9  dbo          AssignmentMarks      student_pk     dbo                Student           student_pk       
FK__Assignmen__assig__787EE5A0  dbo          AssignmentMarks      assignment_pk  dbo                Assignment        assignment_pk    
FK__Attendanc__class__619B8048  dbo          Attendance           class_pk       dbo                Class             class_pk         
FK__Attendanc__facul__6383C8BA  dbo          Attendance           faculty_pk     dbo                Faculty           faculty_pk       
FK__Attendanc__stude__6477ECF3  dbo          Attendance           student_pk     dbo                Student           student_pk       
FK__Attendanc__subje__628FA481  dbo          Attendance           subject_pk     dbo                Subject           subject_pk       
FK__Attendanc__subje__68487DD7  dbo          AttendanceAggregate  subject_pk     dbo                Subject           subject_pk       
FK__Attendanc__stude__6754599E  dbo          AttendanceAggregate  student_pk     dbo                Student           student_pk       
FK__Attendanc__facul__693CA210  dbo          AttendanceAggregate  faculty_pk     dbo                Faculty           faculty_pk       
FK__Branch__dept_pk__44FF419A   dbo          Branch               dept_pk        dbo                Department        dept_pk          
FK__Class__dept_pk__5AEE82B9    dbo          Class                dept_pk        dbo                Department        dept_pk          
FK__ClassFacu__facul__1C873BEC  dbo          ClassFaculty         faculty_pk     dbo                Faculty           faculty_pk       
FK__ClassFacu__class__1B9317B3  dbo          ClassFaculty         class_pk       dbo                Class             class_pk         
FK__ClassInch__class__5DCAEF64  dbo          ClassIncharge        class_pk       dbo                Class             class_pk         
FK__ClassInch__facul__5EBF139D  dbo          ClassIncharge        faculty_pk     dbo                Faculty           faculty_pk       
FK__ClassStud__class__0C50D423  dbo          ClassStudent         class_pk       dbo                Class             class_pk         
FK__ClassStud__stude__0D44F85C  dbo          ClassStudent         student_pk     dbo                Student           student_pk       
FK__ClassSubj__class__10216507  dbo          ClassSubject         class_pk       dbo                Class             class_pk         
FK__ClassSubj__subje__11158940  dbo          ClassSubject         subject_pk     dbo                Subject           subject_pk       
FK__Course__branch_p__48CFD27E  dbo          Course               branch_pk      dbo                Branch            branch_pk        
FK__Departmen__colle__412EB0B6  dbo          Department           college_pk     dbo                College           college_pk       
FK__Faculty__dept_pk__5070F446  dbo          Faculty              dept_pk        dbo                Department        dept_pk          
FK__Faculty__user_pk__3C34F16F  dbo          Faculty              user_pk        dbo                Users             user_pk          
FK__FacultySu__subje__09746778  dbo          FacultySubject       subject_pk     dbo                Subject           subject_pk       
FK__FacultySu__facul__0880433F  dbo          FacultySubject       faculty_pk     dbo                Faculty           faculty_pk       
FK__HOD__dept_pk__571DF1D5      dbo          HOD                  dept_pk        dbo                Department        dept_pk          
FK__HOD__faculty_pk__5812160E   dbo          HOD                  faculty_pk     dbo                Faculty           faculty_pk       
FK__MSTExam__dept_pk__6C190EBB  dbo          MSTExam              dept_pk        dbo                Department        dept_pk          
FK__MSTExam__faculty__3D2915A8  dbo          MSTExam              faculty_pk     dbo                Faculty           faculty_pk       
FK__MSTExam__subject__6D0D32F4  dbo          MSTExam              subject_pk     dbo                Subject           subject_pk       
FK__MSTExamMa__facul__3F115E1A  dbo          MSTExamMarks         faculty_pk     dbo                Faculty           faculty_pk       
FK__MSTExamMa__stude__71D1E811  dbo          MSTExamMarks         student_pk     dbo                Student           student_pk       
FK__MSTExamMa__exam___70DDC3D8  dbo          MSTExamMarks         exam_pk        dbo                MSTExam           exam_pk          
FK__Rejected__reques__70A8B9AE  dbo          Rejected             request_id     dbo                Request           request_id       
FK__Rejected__hod_pk__719CDDE7  dbo          Rejected             hod_pk         dbo                HOD               hod_pk           
FK__Request__user_pk__65370702  dbo          Request              user_pk        dbo                Users             user_pk          
FK__Student__user_pk__3B40CD36  dbo          Student              user_pk        dbo                Users             user_pk          
FK__Student__dept_pk__5441852A  dbo          Student              dept_pk        dbo                Department        dept_pk          
FK__Subject__course___4CA06362  dbo          Subject              course_pk      dbo                Course            course_pk        
FK__UserRoles__role___03F0984C  dbo          UserRoles            role_pk        dbo                Roles             role_pk          
FK__UserRoles__user___02FC7413  dbo          UserRoles            user_pk        dbo                Users             user_pk          
((47 rows affected))


*/

SELECT 
    s.name + ' & ' +
    t.name + ' & ' +
    c.name + ' & ' +
    ty.name + ' & ' +
    CAST(c.max_length AS varchar(10)) + ' & ' +
    CASE WHEN c.is_nullable = 1 THEN 'Yes' ELSE 'No' END + ' \\'
AS latex_row
FROM sys.schemas s
JOIN sys.tables t
    ON t.schema_id = s.schema_id
JOIN sys.columns c
    ON c.object_id = t.object_id
JOIN sys.types ty
    ON c.user_type_id = ty.user_type_id
ORDER BY s.name, t.name, c.column_id;
