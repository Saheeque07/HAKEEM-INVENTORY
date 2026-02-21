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

def count_records():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) as count FROM products")
            p_count = cur.fetchone()['count']
            cur.execute("SELECT COUNT(*) as count FROM categories")
            c_count = cur.fetchone()['count']
            cur.execute("SELECT COUNT(*) as count FROM users")
            u_count = cur.fetchone()['count']
            print(f"Products: {p_count}")
            print(f"Categories: {c_count}")
            print(f"Users: {u_count}")
            cur.close()
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == '__main__':
    count_records()
