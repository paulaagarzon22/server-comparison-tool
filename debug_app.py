import streamlit as st
import pandas as pd
import sqlite3
import json
import hashlib
import os
import sys

# Debug current working directory
st.write(f"Current working directory: {os.getcwd()}")
st.write(f"Script location: {__file__}")
st.write(f"Python executable: {sys.executable}")

# Check if database exists
db_path = 'companies_data.db'
st.write(f"Database path: {db_path}")
st.write(f"Database exists: {os.path.exists(db_path)}")

# Try to connect to database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    st.write(f"Tables in database: {len(tables)}")
    for table in tables:
        st.write(f"- {table[0]}")
    conn.close()
    st.success("Database connection successful!")
except Exception as e:
    st.error(f"Database error: {e}")

st.write("---")
st.write("Basic Streamlit test completed successfully!")
