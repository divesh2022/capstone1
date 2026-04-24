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
