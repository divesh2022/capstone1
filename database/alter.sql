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