# db_utils.py
import mysql.connector
import pandas as pd
import streamlit as st
from db_config import DB_CONFIG

# === Connection Helper ===
def get_mysql_connection(db_name=None):
    db_config = DB_CONFIG.copy()
    if db_name:
        db_config["database"] = db_name
    return mysql.connector.connect(**db_config)

def get_db_connection():
    if "db_name" not in st.session_state:
        st.error("No database selected. Please log in again.")
        st.stop()

    return mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=st.session_state["db_name"]
    )

# === Initialization ===
def init_db():
    with get_mysql_connection("lic-db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(100) PRIMARY KEY,
                password VARCHAR(100) NOT NULL,
                role VARCHAR(50) NOT NULL,
                start_date DATE,
                admin_username VARCHAR(100),
                db_name VARCHAR(200),
                do_code VARCHAR(100),
                agency_code VARCHAR(100),
                name VARCHAR()
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100),
                password VARCHAR(100),
                role VARCHAR(50),
                admin_username VARCHAR(100),
                db_name VARCHAR(200),
                do_code VARCHAR(100),
                agency_code VARCHAR(100),
                name VARCHAR()
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failed_attempts (
                username VARCHAR(100) PRIMARY KEY,
                attempts INT DEFAULT 0
            )
        """)
        conn.commit()

def check_credentials(username, password):
    import mysql.connector

    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database="lic-db"  # Central DB where all user credentials are stored
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        do_code = user['do_code']  # Ensure this column exists in your users table
        st.session_state['username'] = user['username']
        st.session_state['role'] = user['role']
        st.session_state['agency_code'] = user['agency_code']
        st.session_state['current_db'] = f"lic_{do_code}"  # 👈 Main point: route to DO’s DB
        return True
    else:
        return False

def user_exists(username):
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username.upper(),))
        return cursor.fetchone() is not None

def get_admin_by_do_code(do_code):
    with get_mysql_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE role = 'admin' AND do_code = %s", (do_code,))
        return cursor.fetchone()


# === Users Management ===
def get_user(username):
    with get_mysql_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username.upper(),))
        return cursor.fetchone()

def add_user(username, password, role, start_date=None, admin_username=None, db_name=None, do_code=None, agency_code = None, name = None):
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, role, start_date, admin_username, db_name, do_code, agency_code, name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (username.upper(), password, role, start_date, admin_username, db_name, do_code, agency_code, name))
        conn.commit()

def delete_user(username):
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = %s", (username.upper(),))
        conn.commit()

# === Pending Registration ===
def add_pending_user(username, password, role, admin_username, db_name, do_code = None, agency_code = None, name):
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pending_users (username, password, role, admin_username, db_name, do_code, agency_code, name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (username.upper(), password, role, admin_username, db_name, do_code, agency_code, name))
        conn.commit()

def get_pending_users():
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, role, admin_username, db_name, do_code, agency_code, name FROM pending_users")
        return cursor.fetchall()

def delete_pending_user(rowid):
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pending_users WHERE id = %s", (rowid,))
        conn.commit()

# === Login Tracking ===
def log_failed_attempt(username):
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM failed_attempts WHERE username = %s", (username.upper(),))
        if cursor.fetchone():
            cursor.execute("UPDATE failed_attempts SET attempts = attempts + 1 WHERE username = %s", (username.upper(),))
        else:
            cursor.execute("INSERT INTO failed_attempts (username, attempts) VALUES (%s, 1)", (username.upper(),))
        conn.commit()

def reset_failed_attempts(username):
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM failed_attempts WHERE username = %s", (username.upper(),))
        conn.commit()

# === Utilities ===
def load_users():
    with get_mysql_connection() as conn:
        return pd.read_sql("SELECT * FROM users", conn)

def get_all_users():
    with get_mysql_connection() as conn:
        df = pd.read_sql("SELECT username, role, start_date, do_code, namen agency_code FROM users", conn)
        return df.values.tolist()

def update_user_role_and_start(username, new_role, new_start_date):
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET role = %s, start_date = %s
            WHERE username = %s
        """, (new_role, new_start_date, username.upper()))
        conn.commit()
