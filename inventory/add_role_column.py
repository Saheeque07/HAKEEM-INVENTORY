
import os
from flask import Flask
from flask_mysqldb import MySQL
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST') or 'localhost'
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER') or 'root'
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD') or 'yusufimran787161'
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB') or 'inventory_db'

mysql = MySQL(app)

def add_role_column():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
            mysql.connection.commit()
            print("Successfully added role column to users table.")
            cur.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    add_role_column()
