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

def check():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            print("Successfully connected to the database.")
            
            cur.execute("SHOW TABLES")
            tables = cur.fetchall()
            print(f"Tables: {tables}")
            
            for table in tables:
                table_name = list(table.values())[0]
                print(f"\nStructure of {table_name}:")
                cur.execute(f"DESC {table_name}")
                desc = cur.fetchall()
                for row in desc:
                    print(row)
            
            cur.close()
        except Exception as e:
            print(f"Error connecting to the database: {str(e)}")

if __name__ == '__main__':
    check()
