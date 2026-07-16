import sqlite3
import json

conn = sqlite3.connect('companies_data.db')
cursor = conn.cursor()

# First check if Lenovo table exists and has data
cursor.execute('SELECT COUNT(*) FROM lenovo_data_lenovo_servers')
count = cursor.fetchone()[0]
print(f"Lenovo table has {count} rows")

if count > 0:
    # Get all Lenovo data to see what's there
    cursor.execute('SELECT * FROM lenovo_data_lenovo_servers')
    all_results = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    print("Columns:", columns)
    
    # Check for specific products
    products_to_check = ['SR645', 'SR685a']
    
    for product_keyword in products_to_check:
        print(f"\n=== Checking for products containing '{product_keyword}' ===")
        cursor.execute('SELECT * FROM lenovo_data_lenovo_servers WHERE "Product Name" LIKE ?', (f'%{product_keyword}%',))
        results = cursor.fetchall()
        
        if results:
            for row in results:
                print(f"Product: {row[1]}")
                print(f"Full row data:")
                for i, col in enumerate(columns):
                    print(f"  {col}: {row[i]}")
                
                # Check memory specifically
                memory_value = row[4]  # Memory column
                print(f"\nMemory value: {memory_value}")
                if memory_value:
                    memory_str = str(memory_value)
                    print(f"Memory as string: {memory_str}")
                    if isinstance(memory_value, str):
                        try:
                            parsed = json.loads(memory_value)
                            print(f"Parsed Memory: {parsed}")
                            # Check for "A" in parsed list
                            for i, item in enumerate(parsed):
                                if str(item).strip() == 'A' or str(item).strip() == 'a':
                                    print(f"  Found standalone 'A' at index {i} in memory list!")
                                print(f"  Item {i}: '{item}' (length: {len(str(item))})")
                        except:
                            print(f"Memory is not JSON: {memory_value}")
                    else:
                        print(f"Memory is not a string: {type(memory_value)}")
        else:
            print("No data found")
    
    # Check all Lenovo products for any "A" entries in memory
    print("\n=== Checking all Lenovo products for 'A' entries in memory ===")
    cursor.execute('SELECT "Product Name", Memory FROM lenovo_data_lenovo_servers')
    all_results = cursor.fetchall()
    
    for row in all_results:
        product_name = row[0]
        memory_value = row[1]
        
        if memory_value:
            memory_str = str(memory_value)
            if 'A' in memory_str or 'a' in memory_str:
                # Check if it's just "A" or contains "A" as part of a word
                if memory_str.strip() == 'A' or memory_str.strip() == 'a':
                    print(f"Found single 'A' in {product_name}: {memory_value}")
                elif ' A ' in memory_str or ' a ' in memory_str or memory_str.startswith('A ') or memory_str.startswith('a '):
                    print(f"Found standalone 'A' in {product_name}: {memory_value}")
                elif '"A"' in memory_str or "'A'" in memory_str:
                    print(f"Found 'A' in quotes in {product_name}: {memory_value}")
else:
    print("Lenovo table is empty")

conn.close()