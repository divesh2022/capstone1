use campus;


-- User and Roles
CREATE TABLE [Roles] (
    role_pk INT PRIMARY KEY IDENTITY(1,1),
    role_name NVARCHAR(50) NOT NULL
);

CREATE TABLE [Users] (
    user_pk INT PRIMARY KEY IDENTITY(1,1),
    email NVARCHAR(100) UNIQUE NOT NULL,
    username NVARCHAR(50) NOT NULL,
    phone_number NVARCHAR(15)
);

CREATE TABLE UserRoles (
    user_pk INT FOREIGN KEY REFERENCES Users(user_pk),
    role_pk INT FOREIGN KEY REFERENCES Roles(role_pk),
    password_hash NVARCHAR(256) NOT NULL,
    PRIMARY KEY (user_pk, role_pk)
);

-- College, Department, Branch
CREATE TABLE [College] (
    college_pk INT PRIMARY KEY IDENTITY(1,1),
    college_id NVARCHAR(10) UNIQUE NOT NULL,
    college_name NVARCHAR(100) NOT NULL
);

CREATE TABLE Department (
    dept_pk INT PRIMARY KEY IDENTITY(1,1),
    dept_id NVARCHAR(10) UNIQUE NOT NULL,
    dept_name NVARCHAR(100) NOT NULL,
    college_pk INT FOREIGN KEY REFERENCES College(college_pk)
);

CREATE TABLE Branch (
    branch_pk INT PRIMARY KEY IDENTITY(1,1),
    branch_id NVARCHAR(10) UNIQUE NOT NULL,
    branch_name NVARCHAR(100) NOT NULL,
    dept_pk INT FOREIGN KEY REFERENCES Department(dept_pk),
    dept_id NVARCHAR(10) NOT NULL, -- keep natural key for code generation
    branch_code AS (dept_id + branch_id) PERSISTED
);

-- Course and Subject
CREATE TABLE Course (
    course_pk INT PRIMARY KEY IDENTITY(1,1),
    course_code NVARCHAR(10) UNIQUE NOT NULL,
    course_name NVARCHAR(100) NOT NULL,
    branch_pk INT FOREIGN KEY REFERENCES Branch(branch_pk)
);

CREATE TABLE Subject (
    subject_pk INT PRIMARY KEY IDENTITY(1,1),
    subject_code NVARCHAR(10) UNIQUE NOT NULL,
    subject_name NVARCHAR(100) NOT NULL,
    course_pk INT FOREIGN KEY REFERENCES Course(course_pk),
    syllabus_pdf NVARCHAR(MAX)
);

-- Faculty, Student, HOD
CREATE TABLE Faculty (
    faculty_pk INT PRIMARY KEY IDENTITY(1,1),
    dept_pk INT FOREIGN KEY REFERENCES Department(dept_pk),
    email NVARCHAR(100) UNIQUE NOT NULL,
    name NVARCHAR(100) NOT NULL,
    designation NVARCHAR(50)
);

CREATE TABLE Student (
    student_pk INT PRIMARY KEY IDENTITY(1,1),
    roll_no NVARCHAR(15) UNIQUE NOT NULL,
    batch NVARCHAR(10),
    dept_pk INT FOREIGN KEY REFERENCES Department(dept_pk),
    phone_number NVARCHAR(15)
);

CREATE TABLE HOD (
    hod_pk INT PRIMARY KEY IDENTITY(1,1),
    dept_pk INT FOREIGN KEY REFERENCES Department(dept_pk),
    faculty_pk INT FOREIGN KEY REFERENCES Faculty(faculty_pk)
);

-- Class and Class Incharge
CREATE TABLE Class (
    class_pk INT PRIMARY KEY IDENTITY(1,1),
    batch NVARCHAR(10),
    dept_pk INT FOREIGN KEY REFERENCES Department(dept_pk)
);

CREATE TABLE ClassIncharge (
    class_incharge_pk INT PRIMARY KEY IDENTITY(1,1),
    class_pk INT FOREIGN KEY REFERENCES Class(class_pk),
    faculty_pk INT FOREIGN KEY REFERENCES Faculty(faculty_pk),
    semester INT
);

-- Attendance
CREATE TABLE Attendance (
    attendance_pk INT PRIMARY KEY IDENTITY(1,1),
    class_pk INT FOREIGN KEY REFERENCES Class(class_pk),
    subject_pk INT FOREIGN KEY REFERENCES Subject(subject_pk),
    faculty_pk INT FOREIGN KEY REFERENCES Faculty(faculty_pk),
    student_pk INT FOREIGN KEY REFERENCES Student(student_pk),
    date DATE,
    status BIT
);

CREATE TABLE AttendanceAggregate (
    agg_pk INT PRIMARY KEY IDENTITY(1,1),
    student_pk INT FOREIGN KEY REFERENCES Student(student_pk),
    subject_pk INT FOREIGN KEY REFERENCES Subject(subject_pk),
    semester INT,
    faculty_pk INT FOREIGN KEY REFERENCES Faculty(faculty_pk),
    lectures_attended INT,
    total_lectures INT
);

-- Exams and Marks
CREATE TABLE MSTExam ( 
    exam_pk INT PRIMARY KEY IDENTITY(1,1), 
    dept_pk INT FOREIGN KEY REFERENCES Department(dept_pk), 
    subject_pk INT FOREIGN KEY REFERENCES Subject(subject_pk), 
    semester INT, exam_date DATE, exam_pdf NVARCHAR(MAX), 
    total_marks INT, 
    exam_name NVARCHAR(10) NOT NULL CHECK (exam_name IN ('MST-1', 'MST-2')) 
);

CREATE TABLE MSTExamMarks (
    exam_marks_pk INT PRIMARY KEY IDENTITY(1,1),
    exam_pk INT FOREIGN KEY REFERENCES MSTExam(exam_pk),
    student_pk INT FOREIGN KEY REFERENCES Student(student_pk),
    marks INT
);

-- Assignments
CREATE TABLE Assignment (
    assignment_pk INT PRIMARY KEY IDENTITY(1,1),
    dept_pk INT FOREIGN KEY REFERENCES Department(dept_pk),
    subject_pk INT FOREIGN KEY REFERENCES Subject(subject_pk),
    semester INT,
    assignment_pdf NVARCHAR(MAX),
    total_marks INT
);

CREATE TABLE AssignmentMarks (
    assignment_marks_pk INT PRIMARY KEY IDENTITY(1,1),
    assignment_pk INT FOREIGN KEY REFERENCES Assignment(assignment_pk),
    student_pk INT FOREIGN KEY REFERENCES Student(student_pk),
    marks INT
);
-- Table to store all correction requests
CREATE TABLE Request (
    request_id     INT PRIMARY KEY IDENTITY(1,1),
    user_pk        INT NOT NULL FOREIGN KEY REFERENCES Users(user_pk),
    service_type   NVARCHAR(50) NOT NULL CHECK (service_type IN ('mstmarks','assignment_marks','attendance')),
    field_name     NVARCHAR(100) NOT NULL,
    target_pk      INT NOT NULL,
    old_value      NVARCHAR(255),
    new_value      NVARCHAR(255) NOT NULL,
    status         NVARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','accepted','rejected')),
    submitted_at   DATETIME DEFAULT GETDATE()
);

-- Table to store accepted requests
CREATE TABLE Accepted (
    accepted_id    INT PRIMARY KEY IDENTITY(1,1),
    request_id     INT NOT NULL FOREIGN KEY REFERENCES Request(request_id),
    hod_pk         INT NOT NULL FOREIGN KEY REFERENCES HOD(hod_pk),
    reason         NVARCHAR(MAX),
    accepted_at    DATETIME DEFAULT GETDATE()
);

-- Table to store rejected requests
CREATE TABLE Rejected (
    rejected_id    INT PRIMARY KEY IDENTITY(1,1),
    request_id     INT NOT NULL FOREIGN KEY REFERENCES Request(request_id),
    hod_pk         INT NOT NULL FOREIGN KEY REFERENCES HOD(hod_pk),
    reason         NVARCHAR(MAX),
    rejected_at    DATETIME DEFAULT GETDATE()
);

CREATE TABLE FacultySubject (
    faculty_subject_pk INT PRIMARY KEY IDENTITY(1,1),
    faculty_pk INT FOREIGN KEY REFERENCES Faculty(faculty_pk),
    subject_pk INT FOREIGN KEY REFERENCES Subject(subject_pk),
    semester INT NOT NULL
);
CREATE TABLE ClassStudent (
    class_student_pk INT PRIMARY KEY IDENTITY(1,1),
    class_pk INT FOREIGN KEY REFERENCES Class(class_pk),
    student_pk INT FOREIGN KEY REFERENCES Student(student_pk),
    semester INT NOT NULL
);
CREATE TABLE ClassSubject (
    class_subject_pk INT PRIMARY KEY IDENTITY(1,1),
    class_pk INT FOREIGN KEY REFERENCES Class(class_pk),
    subject_pk INT FOREIGN KEY REFERENCES Subject(subject_pk),
    semester INT NOT NULL
);

-- class faculty allocation
CREATE TABLE ClassFaculty (
    class_faculty_pk INT PRIMARY KEY IDENTITY(1,1),
    class_pk INT FOREIGN KEY REFERENCES Class(class_pk),
    faculty_pk INT FOREIGN KEY REFERENCES Faculty(faculty_pk),
    semester INT NOT NULL
);
select * from sys.databases;