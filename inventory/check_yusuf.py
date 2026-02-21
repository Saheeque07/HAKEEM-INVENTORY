import os
from flask import Flask
from flask_mysqldb import MySQL
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'yusufimran787161')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'inventory_db')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def check_role():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SELECT username, role FROM users WHERE username = 'yusuf'")
        user = cur.fetchone()
        print(f"User info: {user}")
        cur.close()

if __name__ == '__main__':
    check_role()
