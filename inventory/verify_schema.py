import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

try:
    db = MySQLdb.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        passwd=os.environ.get('MYSQL_PASSWORD', 'yusufimran787161'),
        db=os.environ.get('MYSQL_DB', 'inventory_db')
    )
    cur = db.cursor()
    cur.execute("DESCRIBE team_members")
    cols = cur.fetchall()
    for col in cols:
        print(col)
    cur.close()
    db.close()
except Exception as e:
    print(f"Error: {e}")
