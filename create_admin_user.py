import mysql.connector
from datetime import datetime

# Replace these with your actual MySQL RDS config
DB_CONFIG = {
    "host": "lic-db.c9cm8c6yand4.eu-north-1.rds.amazonaws.com",
    "user": "admin",
    "password": "7824260Udaan",
    "database": "lic-db",  # This is your main DB where the users table exists
    "port": 3306
}

def create_admin(username, password, start_date=None):
    username = username.upper()
    db_name = f"lic_{username}.db"  # Or you can use a MySQL DB: e.g. `lic_{username}`

    if not start_date:
        start_date = datetime.today().strftime("%Y-%m-%d")

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # Insert into users table
        cursor.execute("""
            INSERT INTO users (username, password, role, start_date, admin_username, db_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, password, "admin", start_date, username, db_name))

        conn.commit()
        print(f"✅ Admin {username} created with DB reference: {db_name}")
    except mysql.connector.IntegrityError as e:
        print(f"❌ Admin already exists or error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

# Example usage:
if __name__ == "__main__":
    create_admin("viplovesaini", "232599", "2023-09-16")
