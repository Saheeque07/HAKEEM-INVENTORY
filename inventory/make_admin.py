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

mysql = MySQL(app)

def promote_user(username):
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET role = 'admin' WHERE username = %s", (username,))
        mysql.connection.commit()
        if cur.rowcount > 0:
            print(f"Successfully promoted '{username}' to Admin!")
        else:
            print(f"User '{username}' not found.")
        cur.close()

if __name__ == '__main__':
    user_to_promote = input("Enter the username you want to make Admin: ")
    promote_user(user_to_promote)
