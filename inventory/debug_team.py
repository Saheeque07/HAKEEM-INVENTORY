import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'yusufimran787161'),
        database=os.environ.get('MYSQL_DB', 'inventory_db')
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM team_members")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} team members.")
    for row in rows:
        print(row)
    cursor.close()
    conn.close()
except Exception as e:
    print(f"DATABASE ERROR: {e}")
