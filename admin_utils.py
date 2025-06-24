import mysql.connector
from db_config import DB_CONFIG


def create_new_admin(
    username,
    password,
    start_date,
    host=None,
    user=None,
    db_password=None
):
    # Use values from DB_CONFIG if not passed explicitly
    host = host or DB_CONFIG["host"]
    user = user or DB_CONFIG["user"]
    db_password = db_password or DB_CONFIG["password"]

    db_name = f"lic_{username.upper()}"  # 🔧 unique DB for this admin

    # Connect to MySQL server (no DB selected yet)
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=db_password
    )
    cursor = conn.cursor()

    # Step 1: Create the admin-specific database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")

    # Step 2: Switch to the new database
    cursor.execute(f"USE {db_name}")

    # Step 3: Create required tables in that admin's DB

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lic_data (
            `Policy No` VARCHAR(50),
            `Short Name` VARCHAR(100),
            `DOC` DATE,
            `Term` INT,
            `Plan` VARCHAR(10),
            `Mode` VARCHAR(20),
            `Premium` DECIMAL(10,2),
            `ENACH Date` DATE,
            `ANANDA` VARCHAR(10),
            `Agency Code` VARCHAR(20),
            `Agent Name` VARCHAR(100)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS premium_summary (
            agency_code VARCHAR(50),
            report_month VARCHAR(20),
            total_premium DECIMAL(15,2),
            fp_sch_prem DECIMAL(15,2),
            fy_sch_prem DECIMAL(15,2),
            uploaded_by VARCHAR(50)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(100),
            role VARCHAR(20),
            start_date DATE,
            admin_username VARCHAR(50),
            db_name VARCHAR(100)
        )
    """)

    conn.commit()
    conn.close()

    # Step 4: Save this admin to the central registry in lic_db
    # Connect again to lic_db
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=db_password,
        database="lic-db"
    )
    cursor = conn.cursor()

#    cursor.execute("""
#        INSERT INTO users (username, password, role, start_date, db_name)
#        VALUES (%s, %s, %s, %s, %s)
#    """, (username, password, "admin", start_date, db_name))

    conn.commit()
    conn.close()
