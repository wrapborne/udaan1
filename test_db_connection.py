# test_db_connection.py
from db_utils import get_mysql_connection  # make sure db_utils is in the same folder or Python path

def test_connection():
    try:
        conn = get_mysql_connection()  # Or pass your db_name if required
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")  # MySQL command
        tables = cursor.fetchall()
        print("✅ Connection successful. Tables:")
        for table in tables:
            print(f" - {table[0]}")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
