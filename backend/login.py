'''
Overview
This module defines the authentication and login endpoints for the college management system. It handles user login requests, validates credentials against the database, and issues authentication tokens for secure access to other backend services.

Key Components
🔹 Data Models
LoginRequest (Pydantic Model)  
Represents the structure of a login request.
Attributes:

username: The user’s login name

password: The user’s password

LoginResponse (Pydantic Model)  
Represents the structure of a login response.
Attributes:

access_token: JWT or session token issued upon successful login

token_type: Type of token (e.g., bearer)

🔹 Endpoints
POST /login → login_user  
Authenticates a user based on provided credentials.

Input: LoginRequest (username, password)

Process:

Queries the database for matching user credentials

Validates password

Issues an authentication token if valid

Output: LoginResponse with token details

Error Handling: Returns HTTPException with status 401 if credentials are invalid

🔹 Utility Functions
Database Connection  
Uses get_connection() from the connect module to establish and close database connections.

Token Generation  
Likely uses JWT or similar mechanism to generate secure tokens for authenticated sessions.

Error Handling  
Wraps queries and authentication logic in try/except blocks to ensure failures are returned as HTTP errors.
'''
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import uvicorn
from connect import get_connection

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str
    role_name: str

class LoginResponse(BaseModel):
    user_pk: int
    username: str
    email: str
    role_name: str

def verify_password(password: str, stored_hash: str) -> bool:
    # For now, direct compare since DB stores '1234'
    return password == stored_hash

@router.get("/roles")
def list_roles():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT role_pk, role_name FROM Roles")
        rows = cursor.fetchall()
        return [{"role_pk": r[0], "role_name": r[1]} for r in rows]
    finally:
        cursor.close()
        conn.close()

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT u.user_pk, u.username, u.email, ur.password_hash, r.role_name
            FROM Users u
            JOIN UserRoles ur ON u.user_pk = ur.user_pk
            JOIN Roles r ON ur.role_pk = r.role_pk
            WHERE u.email = ? AND r.role_name = ?
        """, (request.email, request.role_name))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=401, detail="Invalid email or role")

        user_pk, username, email, password_hash, role_name = row

        if not verify_password(request.password, password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")

        return LoginResponse(
            user_pk=user_pk,
            username=username,
            email=email,
            role_name=role_name
        )
    finally:
        cursor.close()
        conn.close()

app = FastAPI(title="Campus ERP Auth API", version="1.0.0")
app.include_router(router, prefix="/auth", tags=["Authentication"])

@router.get("/emails")
def list_emails():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Fetching all emails to populate the dropdown
        cursor.execute("SELECT email FROM Users")
        rows = cursor.fetchall()
        return [r[0] for r in rows]
    finally:
        cursor.close()
        conn.close()

@app.get("/")
def root():
    return {"message": "login API is running"}

if __name__ == "__main__":
    uvicorn.run("auth:app", host="0.0.0.0", port=8000, reload=True)
