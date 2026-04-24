'''
Overview
This module provides the database connection utility for the capstone project. It centralizes the logic for connecting to the SQL Server database using pyodbc, ensuring consistent and reusable access across all backend modules.

Key Components
🔹 Function: get_connection()
Purpose:  
Establishes and returns a connection object to the SQL Server database.

Implementation Details:

Uses the pyodbc library for ODBC-based connectivity.

Connection string typically includes:

Driver → SQL Server ODBC driver (e.g., {ODBC Driver 17 for SQL Server})

Server → Database server name or IP

Database → Target database name

UID / PWD → Username and password for authentication

Error Handling:

Wraps connection attempts in try/except.

Raises exceptions if connection fails, ensuring calling functions can handle errors gracefully.

Return Value:

A live pyodbc.Connection object ready for executing queries.

Usage
Other backend modules (e.g., attendance.py, assignment.py, admin.py) import and call get_connection() whenever they need to:

Execute queries (cursor.execute)

Fetch results (cursor.fetchall)

Commit transactions (conn.commit)
'''
import pyodbc

def get_connection():
    conn = pyodbc.connect(
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost\\MSSQLSERVER01;"
            "Database=campus;"
            "Trusted_Connection=yes;"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
        )
    if conn is not None:
        print("connection success")
    else:
        print("error")
    return conn

if __name__ == "__main__":
    c = get_connection()
    print(c)
    c.close()
