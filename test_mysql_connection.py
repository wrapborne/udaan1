import mysql.connector

conn = mysql.connector.connect(
    host="lic-db.c9cm8c6yand4.eu-north-1.rds.amazonaws.com",      # e.g. lic-db.xxxxxx.us-east-1.rds.amazonaws.com
    user="admin",                  # or your actual username
    password="7824260Udaan",      # the password you created
    database="lic-db",       # e.g. lic_main
    port=3306                      # default MySQL port
)

cursor = conn.cursor()
cursor.execute("SHOW TABLES")
for table in cursor.fetchall():
    print(table)

conn.close()
