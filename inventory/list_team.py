from flask import Flask
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'yusufimran787161')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'inventory_db')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM team_members")
    members = cur.fetchall()
    print(f"Total members: {len(members)}")
    for m in members:
        print(m)
    cur.close()
