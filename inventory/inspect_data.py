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
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def inspect_data():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            print("--- Categories ---")
            cur.execute("SELECT * FROM categories")
            categories = cur.fetchall()
            for c in categories:
                print(c)
                
            print("\n--- Products ---")
            cur.execute("SELECT * FROM products")
            products = cur.fetchall()
            for p in products:
                print(p)
                
            print("\n--- Users ---")
            cur.execute("SELECT id, username, email FROM users")
            users = cur.fetchall()
            for u in users:
                print(u)
                
            cur.close()
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == '__main__':
    inspect_data()
