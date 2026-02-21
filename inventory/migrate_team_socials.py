import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def migrate():
    try:
        db = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            passwd=os.environ.get('MYSQL_PASSWORD', 'yusufimran787161'),
            db=os.environ.get('MYSQL_DB', 'inventory_db')
        )
        cur = db.cursor()
        
        print("Adding social columns to team_members...")
        
        # Add columns if not exist
        cur.execute("DESCRIBE team_members")
        columns = [col[0] for col in cur.fetchall()]
        
        if 'linkedin' not in columns:
            cur.execute("ALTER TABLE team_members ADD COLUMN linkedin VARCHAR(255)")
            print("Added linkedin")
        if 'github' not in columns:
            cur.execute("ALTER TABLE team_members ADD COLUMN github VARCHAR(255)")
            print("Added github")
        if 'email' not in columns:
            cur.execute("ALTER TABLE team_members ADD COLUMN email VARCHAR(255)")
            print("Added email")
            
        db.commit()
        cur.close()
        db.close()
        print("Migration successful.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    migrate()
