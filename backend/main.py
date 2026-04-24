'''
Overview
This is the entry point for the Campus ERP backend. It initializes the FastAPI application and registers all routers that handle different modules of the system (attendance, assignments, exams, corrections, administration, etc.). It also provides basic health-check endpoints.

Key Components
🔹 Application Initialization
app = FastAPI(...)  
Creates the FastAPI application instance with metadata:

title="Campus ERP API"

version="1.0.0"

🔹 Router Inclusions
The file imports and registers routers from multiple backend modules, each with a prefix and tag for organization:

Attendance

attendence.router → /faculty/attendance

attendance_aggregate.router → /faculty/attendance_aggregate

Assignments

assignment.router → /faculty/assignment

assignment_marks.router → /faculty/assignment_marks

Exams

mst_exam.router → /faculty/mst_exam

mst_exam_marks.router → /faculty/mst_exam_marks

Corrections

correction.router → /faculty/correction

Administration

admin.router → /admin

Head of Department (HOD)

hod.router → /hod

Students

student.router → /student

Authentication

login.router → /auth

🔹 Endpoints
GET / → root()  
Returns a simple JSON message:

json
{ "message": "Campus ERP API is running" }
GET /health  
Provides a health-check endpoint to verify that the API is operational.
'''
from fastapi import FastAPI

# Import all routers
import attendence
import attendance_aggregate
import assignment
import assignment_marks
import view
import mst_exam
import mst_exam_marks
import login
import correction
import admin
import hod
import student

app = FastAPI(title="Campus ERP API", version="1.0.0")


# Include all routers
app.include_router(attendence.router, prefix="/faculty/attendance", tags=["Attendance"])
app.include_router(attendance_aggregate.router, prefix="/faculty/attendance_aggregate", tags=["Attendance Aggregate"])
app.include_router(assignment.router, prefix="/faculty/assignment", tags=["Assignment"])
app.include_router(assignment_marks.router, prefix="/faculty/assignment_marks", tags=["Assignment Marks"])
app.include_router(mst_exam.router, prefix="/faculty/mst_exam", tags=["MST Exam"])
app.include_router(mst_exam_marks.router, prefix="/faculty/mst_exam_marks", tags=["MST Exam Marks"])
app.include_router(correction.router, prefix="/faculty/correction", tags=["Correction Workflow"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(hod.router, prefix="/hod", tags=["HOD"])
app.include_router(student.router, prefix="/student", tags=["Student"])
app.include_router(login.router, prefix="/auth", tags=["Authentication"])
@app.get("/")
def root():
    return {"message": "Campus ERP API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
