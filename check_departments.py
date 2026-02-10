import sqlite3
import sys

# Connect to the database
conn = sqlite3.connect('data/dashboard.db')
cursor = conn.cursor()

# Query departments
cursor.execute("SELECT department_key, department_name, cost_centre_parent FROM departments")
departments = cursor.fetchall()

print(f"Total departments in database: {len(departments)}")
print("\nDepartment list:")
for dept in departments:
    print(f"  {dept[0]}: {dept[1]} (Parent: {dept[2]})")

conn.close()
