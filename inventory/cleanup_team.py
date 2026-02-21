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
    cursor = conn.cursor()
    
    print("Cleaning up 'None' strings in team_members table...")
    
    cols = ['image_url', 'linkedin', 'github', 'email', 'description', 'role']
    for col in cols:
        cursor.execute(f"UPDATE team_members SET {col} = NULL WHERE {col} = 'None'")
        print(f"Cleaned up column: {col}")
        
    conn.commit()
    cursor.close()
    conn.close()
    print("Cleanup complete.")
except Exception as e:
    print(f"Error: {e}")
