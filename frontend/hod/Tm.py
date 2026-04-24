import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://localhost:8000/hod"  # Adjust if FastAPI runs elsewhere

st.title("Total Internal Marks Dashboard")

tab1, tab2, tab3 = st.tabs(["View Marks", "Export Data", "Filter, Sort & Export"])

with tab1:
    st.header("All Internal Marks")
    resp = requests.get(f"{BASE_URL}/Tm/total-internal-marks")
    if resp.ok:
        data = resp.json()
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.session_state["marks_data"] = df
    else:
        st.error(resp.text)

with tab2:
    st.header("Export Raw Marks")
    if "marks_data" in st.session_state and not st.session_state["marks_data"].empty:
        df = st.session_state["marks_data"]

        # CSV export
        csv_file = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV File",
            data=csv_file,
            file_name="marks_export.csv",
            mime="text/csv"
        )

        # Excel export (requires openpyxl)
        try:
            excel_file = "marks_export.xlsx"
            df.to_excel(excel_file, index=False, engine="openpyxl")
            with open(excel_file, "rb") as f:
                st.download_button(
                    label="Download Excel File",
                    data=f,
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except ImportError:
            st.warning("Excel export requires 'openpyxl'. Install it with: pip install openpyxl")
    else:
        st.info("No marks data available yet. Please fetch marks first in the 'View Marks' tab.")

with tab3:
    st.header("Filter, Sort & Export Subset")
    if "marks_data" in st.session_state and not st.session_state["marks_data"].empty:
        df = st.session_state["marks_data"]

        # Filter by subject code
        subject_codes = df["subject_code"].unique().tolist()
        selected_subject = st.selectbox("Filter by Subject Code", ["All"] + subject_codes)
        if selected_subject != "All":
            df = df[df["subject_code"] == selected_subject]

        # Select columns to display
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect("Select columns to display", all_columns, default=all_columns)
        df = df[selected_columns]

        # Multi-column sorting
        sort_columns = st.multiselect("Select columns to sort by", all_columns)
        if sort_columns:
            ascending = st.radio("Sort order", ["Ascending", "Descending"]) == "Ascending"
            df = df.sort_values(by=sort_columns, ascending=ascending)

        st.dataframe(df)

        # Export the filtered/sorted subset
        csv_file = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered CSV",
            data=csv_file,
            file_name="marks_filtered.csv",
            mime="text/csv"
        )

        try:
            excel_file = "marks_filtered.xlsx"
            df.to_excel(excel_file, index=False, engine="openpyxl")
            with open(excel_file, "rb") as f:
                st.download_button(
                    label="Download Filtered Excel",
                    data=f,
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except ImportError:
            st.warning("Excel export requires 'openpyxl'. Install it with: pip install openpyxl")
    else:
        st.info("No marks data available yet. Please fetch marks first in the 'View Marks' tab.")
