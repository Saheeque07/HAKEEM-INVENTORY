import os
from flask import Flask
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'yusufimran787161')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'inventory_db')

mysql = MySQL(app)

def setup_admin(username, password):
    with app.app_context():
        password_hash = generate_password_hash(password)
        cur = mysql.connection.cursor()
        
        # Check if user exists
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        if user:
            # Update existing user
            cur.execute("UPDATE users SET password_hash = %s, role = 'admin' WHERE username = %s", (password_hash, username))
            print(f"User '{username}' updated with new password and admin role.")
        else:
            # Create new admin user
            # Note: email is required in the schema usually, let's check app.py for default email or just use admin@example.com
            email = f"{username}@example.com"
            cur.execute("INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, 'admin')", 
                        (username, email, password_hash))
            print(f"New user '{username}' created with admin role and password '{password}'.")
            
        mysql.connection.commit()
        cur.close()

if __name__ == '__main__':
    setup_admin('admin', '123admin')
