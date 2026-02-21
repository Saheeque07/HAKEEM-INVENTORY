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

def list_users():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, username, email, role FROM users")
            users = cur.fetchall()
            print("--- Current Users in Database ---")
            for user in users:
                print(user)
            cur.close()
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == '__main__':
    list_users()
