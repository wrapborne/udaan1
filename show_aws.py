import mysql.connector

# Connect to MySQL RDS
conn = mysql.connector.connect(
    host="lic-db.c9cm8c6yand4.eu-north-1.rds.amazonaws.com",
    user="admin",
    password="7824260Udaan",  # 🔁 Replace with your actual password
    database="lic-db",
    port=3306
)

cursor = conn.cursor()

# Get all table names
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()

print("📋 Tables and columns in 'lic-db':\n")

# Loop through each table and show its columns
for (table_name,) in tables:
    print(f"🔸 {table_name}")
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    columns = cursor.fetchall()
    for col in columns:
        print(f"   - {col[0]} ({col[1]})")
    print()

# Clean up
cursor.close()
conn.close()
