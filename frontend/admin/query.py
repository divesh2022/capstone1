'''
Admin Query Editor App Documentation
Overview
This Streamlit application provides a frontend interface for executing SQL queries against a FastAPI backend (http://127.0.0.1:8000/admin). It allows administrators to run single or multiple queries, view results in tables, and receive success/error messages directly in the UI.

🔗 Backend API Endpoint
Admin Query

POST /admin/query → Executes SQL queries.

Accepts parameter: query (string, can contain multiple queries separated by ;).

Returns JSON response with either:

queries: list of executed queries with results/messages.

results: single query result.

message: confirmation message for queries without results.

🖥️ Application Workflow
1. SQL Input
Text area (st.text_area) allows entry of one or more SQL queries.

Queries can be separated by semicolons (;).

2. Run Query
On Run Query button click:

Sends POST /query with the SQL string.

Handles both single and multiple queries.

3. Response Handling
Multiple Queries:

If response contains "queries", iterate through each query.

Display subheader with query text.

Show results in a table if available, otherwise display success message.

Single Query:

If response contains "results", display results in a table.

Otherwise, show success message.

4. Error Handling
If backend returns non-200 status:

Display error message from backend.

If exception occurs:

Display error message with exception details.
'''
import streamlit as st
import requests
a = "http://127.0.0.1:8000/admin"

API_URL = "http://127.0.0.1:8000/admin/admin"  # FastAPI backend

st.title("Admin Query Editor")

# Text area for SQL input
query = st.text_area("Enter SQL query (you can run multiple queries separated by ;)")

# Run query button
if st.button("Run Query"):
    try:
        response = requests.post(
            f"{API_URL}/query",
            params={"query": query}
        )
        if response.status_code == 200:
            data = response.json()

            # Handle multiple queries
            if "queries" in data:
                for q in data["queries"]:
                    st.subheader(f"Results for: {q['query']}")
                    if "results" in q:
                        st.table(q["results"])
                    else:
                        st.success(q["message"])
            else:
                # Single query fallback
                if "results" in data:
                    st.subheader("Query Results")
                    st.table(data["results"])
                else:
                    st.success(data.get("message", "Query executed successfully"))
        else:
            st.error(response.json())
    except Exception as e:
        st.error(f"Error: {e}")
