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