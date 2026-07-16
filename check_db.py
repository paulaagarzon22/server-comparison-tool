import sqlite3
import json

conn = sqlite3.connect('companies_data.db')
cursor = conn.cursor()

# Get table names
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print("Tables:", tables)

# Check row counts for all tables
for table in tables:
    table_name = table[0]
    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    count = cursor.fetchone()[0]
    print(f"{table_name}: {count} rows")

# Get a sample Dell row
cursor.execute('SELECT * FROM dell_configurations_dell_servers LIMIT 1')
results = cursor.fetchall()
print(f"\nDell sample data:")
if results:
    columns = [description[0] for description in cursor.description]
    print("Columns:", columns)
    for row in results:
        print(row)
        # Check CPU format
        cpu_value = row[2]  # CPU column
        if isinstance(cpu_value, str):
            try:
                parsed = json.loads(cpu_value)
                print(f"  Parsed CPU: {parsed}")
            except:
                print(f"  CPU is not JSON: {cpu_value}")
else:
    print("No data found")

# Get a sample Lenovo row
cursor.execute('SELECT * FROM lenovo_data_lenovo_servers LIMIT 1')
results = cursor.fetchall()
print(f"\nLenovo sample data:")
if results:
    columns = [description[0] for description in cursor.description]
    print("Columns:", columns)
    for row in results:
        print(row)
        # Check CPU format
        cpu_value = row[2]  # CPU column
        if isinstance(cpu_value, str):
            try:
                parsed = json.loads(cpu_value)
                print(f"  Parsed CPU: {parsed}")
            except:
                print(f"  CPU is not JSON: {cpu_value}")
else:
    print("No data found")

conn.close()