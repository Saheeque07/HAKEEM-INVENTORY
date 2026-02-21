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

def reset_password(username, new_password):
    with app.app_context():
        password_hash = generate_password_hash(new_password)
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password_hash = %s WHERE username = %s", (password_hash, username))
        mysql.connection.commit()
        if cur.rowcount > 0:
            print(f"Password for '{username}' has been reset to '{new_password}'")
        else:
            print(f"User '{username}' not found.")
        cur.close()

if __name__ == '__main__':
    reset_password('yusuf', 'admin123')
