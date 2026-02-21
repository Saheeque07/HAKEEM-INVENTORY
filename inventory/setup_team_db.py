
import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def setup_team_table():
    try:
        db = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            passwd=os.environ.get('MYSQL_PASSWORD', 'yusufimran787161'),
            db=os.environ.get('MYSQL_DB', 'inventory_db')
        )
        cur = db.cursor()
        
        # Create table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                role VARCHAR(100),
                description TEXT,
                image_url VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if empty
        cur.execute("SELECT COUNT(*) FROM team_members")
        if cur.fetchone()[0] == 0:
            members = [
                ("Hakeem", "Project Leader & Architect", "Visionary leader driving the core strategy and system architecture.", "https://ui-avatars.com/api/?name=Hakeem&background=1e3a8a&color=fff&size=128"),
                ("Yusuf", "Co-Leader & Lead Dev", "Expert in backend synchronization and database integrity.", "https://ui-avatars.com/api/?name=Yusuf&background=2563eb&color=fff&size=128"),
                ("Imran", "Frontend Specialist", "Designing the modern, clean interface and user experience.", "https://ui-avatars.com/api/?name=Imran&background=10b981&color=fff&size=128"),
                ("Team Member 4", "Operations Manager", "Overseeing daily operations and logistics management.", "https://ui-avatars.com/api/?name=TM4&background=6366f1&color=fff&size=128"),
                ("Team Member 5", "Marketing Head", "Driving growth and managing client relationships.", "https://ui-avatars.com/api/?name=TM5&background=ec4899&color=fff&size=128"),
                ("Team Member 6", "Support Lead", "Ensuring customer satisfaction and providing technical support.", "https://ui-avatars.com/api/?name=TM6&background=f59e0b&color=fff&size=128")
            ]
            cur.executemany("INSERT INTO team_members (name, role, description, image_url) VALUES (%s, %s, %s, %s)", members)
            print("Seeded 6 team members.")
        
        db.commit()
        cur.close()
        db.close()
        print("Team table setup successful.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    setup_team_table()
