import sqlite3
import json

conn = sqlite3.connect('companies_data.db')
cursor = conn.cursor()

# Get specific products
products_to_check = ['ThinkSystem SR645 V3', 'ThinkSystem SR685a V3']

for product_name in products_to_check:
    print(f"\n=== {product_name} ===")
    cursor.execute('SELECT * FROM lenovo_data_lenovo_servers WHERE "Product Name" = ?', (product_name,))
    results = cursor.fetchall()
    
    if results:
        columns = [description[0] for description in cursor.description]
        for row in results:
            print(f"Product: {row[1]}")
            print(f"CPU: {row[2]}")
            print(f"GPU: {row[3]}")
            print(f"Memory: {row[4]}")
            print(f"Storage Drive Type: {row[5]}")
            print(f"Max Drive Configuration: {row[6]}")
            
            # Parse and check memory specifically
            if row[4]:
                try:
                    memory_data = json.loads(row[4]) if isinstance(row[4], str) else row[4]
                    print(f"\nParsed Memory ({len(memory_data)} items):")
                    for i, item in enumerate(memory_data):
                        print(f"  {i+1}. '{item}' (length: {len(str(item))})")
                        if str(item).strip() == 'A' or str(item).strip() == 'a':
                            print(f"     *** FOUND STANDALONE 'A'! ***")
                except:
                    print(f"Could not parse memory as JSON: {row[4]}")
    else:
        print("Product not found")

# Also check all products for any "A" in memory
print("\n=== Checking all Lenovo products for 'A' in memory ===")
cursor.execute('SELECT "Product Name", Memory FROM lenovo_data_lenovo_servers')
all_results = cursor.fetchall()

for row in all_results:
    product_name = row[0]
    memory_value = row[1]
    
    if memory_value:
        try:
            memory_data = json.loads(memory_value) if isinstance(memory_value, str) else memory_value
            for item in memory_data:
                if str(item).strip() == 'A' or str(item).strip() == 'a':
                    print(f"Found standalone 'A' in {product_name}: {memory_value}")
        except:
            # If not JSON, check the string directly
            if str(memory_value).strip() == 'A' or str(memory_value).strip() == 'a':
                print(f"Found standalone 'A' in {product_name}: {memory_value}")

conn.close()