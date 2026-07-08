import streamlit as st
import pandas as pd
import sqlite3

# Simple test to see if basic imports work
st.title("Test App")
st.write("Database connection test")

try:
    conn = sqlite3.connect('companies_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    st.write(f"Tables found: {len(tables)}")
    for table in tables:
        st.write(f"- {table[0]}")
    conn.close()
    st.success("Database connection successful!")
except Exception as e:
    st.error(f"Database error: {e}")
