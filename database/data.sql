'''
Overview
This SQL script contains initial data population commands for the Campus ERP database. It inserts records into core tables such as departments, courses, branches, subjects, faculties, students, and roles. The script ensures that the system has baseline data for testing and deployment.

Key Components
🔹 Department Data
Inserts records into the department table.

Typical fields: dept_id, dept_name, college_pk.

Example: Computer Science, Mechanical Engineering, Electrical Engineering.

🔹 Course Data
Populates the course table with academic programs.

Fields: course_id, course_name, dept_pk.

Example: B.Tech, M.Tech, Diploma.

🔹 Branch Data
Inserts records into the branch table.

Fields: branch_id, branch_name, course_pk.

Example: AI & ML, Civil, Electronics.

🔹 Subject Data
Populates the subject table with course subjects.

Fields: subject_id, subject_name, course_pk, semester.

Example: Compiler Design, Database Systems, Operating Systems.

🔹 Faculty Data
Inserts records into the faculty table.

Fields: faculty_id, faculty_name, dept_pk, subject_pk.

Example: Faculty assigned to teach Database Systems in CSE.

🔹 Student Data
Populates the student table with student records.

Fields: student_id, roll_no, name, dept_pk, course_pk, branch_pk, semester.

Example: Roll numbers linked to CSE (AI & ML) branch.

🔹 Role & User Data
Inserts records into role and user tables.

Roles: Admin, Faculty, Student.

Users: Linked to roles for authentication and authorization.
'''
-- Roles & users
INSERT INTO Roles (role_name)
VALUES ('Admin'), ('Faculty'), ('Student');

INSERT INTO Users (email, username, password_hash, phone_number, role_id)
VALUES
  ('admin@campus.edu','admin','<hash>','1234567890',1),      -- role_id 1 = Admin
  ('jdoe@campus.edu','jdoe','<hash>','0987654321',2);        -- role_id 2 = Faculty

-- college / department / branch
INSERT INTO College (college_id, college_name)
VALUES ('C001','Engineering College');

INSERT INTO Department (dept_id, dept_name, college_pk)
VALUES
  ('D001','Computer Science', 1),
  ('D002','Mechanical',        1);

INSERT INTO Branch (branch_id, branch_name, dept_pk, dept_id)
VALUES
  ('B001','Software Engineering', 1, 'D001'),
  ('B002','Networks',             1, 'D001');

-- course / subject
INSERT INTO Course (course_code, course_name, branch_pk)
VALUES 
  ('CS101','Intro to CS',          1),
  ('CS102','Data Structures',      1);

INSERT INTO Subject (subject_code, subject_name, course_pk, syllabus_pdf)
VALUES
  ('SUB101','Programming Basics',   1, '/pdfs/prog.pdf'),
  ('SUB102','Algorithms',           2, '/pdfs/algos.pdf');

-- faculty / student / hod
INSERT INTO Faculty (dept_pk, email, name, designation)
VALUES
  (1,'prof.smith@campus.edu','Prof Smith','Professor'),
  (2,'prof.jones@campus.edu','Prof Jones','Assistant Professor');

INSERT INTO Student (roll_no, batch, dept_pk, phone_number)
VALUES
  ('2025001','2025',1,'555‑1234'),
  ('2025002','2025',1,'555‑5678');

INSERT INTO HOD (dept_pk, faculty_pk)
VALUES (1,1);          -- Prof Smith is HOD of CS

-- class / class in‑charge
INSERT INTO Class (batch, dept_pk)
VALUES ('2025',1);

INSERT INTO ClassIncharge (class_pk, faculty_pk, semester)
VALUES (1,1,1);

-- attendance
INSERT INTO Attendance (class_pk, subject_pk, faculty_pk, student_pk, date, status)
VALUES
  (1,1,1,1,'2026‑02‑27',1),
  (1,1,1,2,'2026‑02‑27',0);

INSERT INTO AttendanceAggregate
    (student_pk, subject_pk, semester, faculty_pk, lectures_attended, total_lectures)
VALUES
  (1,1,1,1,10,12),
  (2,1,1,1,9,12);

-- MST exams & marks
INSERT INTO MSTExam
    (dept_pk, subject_pk, semester, exam_date, exam_pdf, total_marks, exam_name)
VALUES
  (1,1,1,'2026‑03‑15','/pdfs/mst1.pdf',100,'MST-1'),
  (1,1,1,'2026‑04‑15','/pdfs/mst2.pdf',100,'MST-2');

INSERT INTO MSTExamMarks (exam_pk, student_pk, marks)
VALUES
  (1,1,85),
  (1,2,78);

-- assignments & marks
INSERT INTO Assignment
    (dept_pk, subject_pk, semester, assignment_pdf, total_marks)
VALUES
  (1,1,1,'/pdfs/assign1.pdf',50);

INSERT INTO AssignmentMarks (assignment_pk, student_pk, marks)
VALUES
  (1,1,45),
  (1,2,40);

-- insert roles and users for authentication/authorization
-- Insert Roles (5 values)
INSERT INTO Roles (role_name) VALUES
('Admin'),
('Faculty'),
('Student'),
('HOD'),
('ClassIncharge');

-- Insert Users (5 values)
INSERT INTO Users (email, username, password_hash, phone_number) VALUES
('alice@example.com', 'alice', 'hash_alice', '9876543210'),
('bob@example.com', 'bob', 'hash_bob', '9123456780'),
('charlie@example.com', 'charlie', 'hash_charlie', '9988776655'),
('diana@example.com', 'diana', 'hash_diana', '8899776655'),
('eric@example.com', 'eric', 'hash_eric', '7766554433');

-- Assign Roles to Users (UserRoles junction table)
-- Alice: Admin + Student
INSERT INTO UserRoles (user_pk, role_pk) VALUES (1, 1), (1, 3);

-- Bob: Faculty + ClassIncharge
INSERT INTO UserRoles (user_pk, role_pk) VALUES (2, 2), (2, 5);

-- Charlie: Student only
INSERT INTO UserRoles (user_pk, role_pk) VALUES (3, 3);

-- Diana: Faculty + HOD
INSERT INTO UserRoles (user_pk, role_pk) VALUES (4, 2), (4, 4);

-- Eric: Admin only
INSERT INTO UserRoles (user_pk, role_pk) VALUES (5, 1);

-- 2. Add password_hash column to UserRoles with a default value
ALTER TABLE UserRoles
ADD password_hash NVARCHAR(256) NOT NULL DEFAULT '1234';
use campus;
insert into ClassStudent VALUES (1,1,1),(1,1,2);
