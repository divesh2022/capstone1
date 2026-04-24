'''
Overview
This SQL script contains schema modification commands for the Campus ERP database. It is used to alter existing tables, update constraints, and adjust relationships between entities such as students, faculties, courses, subjects, and exams.

Key Components
🔹 Table Alterations
ALTER TABLE statements  
Modify existing tables to add, drop, or change columns.
Typical changes include:

Adding new attributes (e.g., email, phone_no)

Updating data types for consistency (e.g., VARCHAR(50) → VARCHAR(100))

Setting NOT NULL or DEFAULT constraints

🔹 Foreign Key Constraints
Ensures referential integrity between tables.
Examples:

Linking student table to department, course, and branch tables

Linking faculty table to department and subject tables

Linking mst_exam_marks and assignment_marks to their respective exam/assignment tables

🔹 Indexes
May include CREATE INDEX or ALTER INDEX statements to improve query performance.

Commonly applied on frequently queried fields like roll_no, faculty_pk, subject_pk.

🔹 Relationship Adjustments
Updates relationships to ensure proper one-to-many and many-to-many mappings.
Examples:

A department can have multiple courses.

A course can have multiple subjects.

A student can have multiple attendance and exam records.
'''
use [campus];

ALTER TABLE Student 
ADD user_pk INT FOREIGN KEY REFERENCES Users(user_pk);

ALTER TABLE Faculty 
ADD user_pk INT FOREIGN KEY REFERENCES Users(user_pk);

-- Adding Faculty to MSTExam
ALTER TABLE MSTExam
ADD faculty_pk INT FOREIGN KEY REFERENCES Faculty(faculty_pk);

-- Adding Faculty to Assignment
ALTER TABLE Assignment
ADD faculty_pk INT FOREIGN KEY REFERENCES Faculty(faculty_pk);

-- Adding Faculty to MSTExamMarks
ALTER TABLE MSTExamMarks
ADD faculty_pk INT FOREIGN KEY REFERENCES Faculty(faculty_pk);

-- Adding Faculty to AssignmentMarks
ALTER TABLE AssignmentMarks
ADD faculty_pk INT FOREIGN KEY REFERENCES Faculty(faculty_pk);

-- 1. Drop the NOT NULL constraint on Users.password_hash
ALTER TABLE Users
ALTER COLUMN password_hash NVARCHAR(256) NULL;

-- 2. Drop the password_hash column from Users
ALTER TABLE Users
DROP COLUMN password_hash;

-- Add status column to MSTExam
ALTER TABLE MSTExam
ADD status BIT NOT NULL 
    CONSTRAINT DF_MSTExam_Status DEFAULT 0;

-- Add status column to AssignmentMarks
ALTER TABLE AssignmentMarks
ADD status BIT NOT NULL 
    CONSTRAINT DF_AssignmentMarks_Status DEFAULT 0;
ALTER TABLE Assignment
ADD status BIT NOT NULL 
    CONSTRAINT DF_Assignment_Status DEFAULT 0;

ALTER TABLE Class
ADD semester INT;
