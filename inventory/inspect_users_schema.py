
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

def inspect_users_schema():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("DESCRIBE users")
            columns = cur.fetchall()
            for col in columns:
                print(col)
            cur.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    inspect_users_schema()
