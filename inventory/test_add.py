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

def test_add():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO categories (name, description) VALUES (%s, %s)", ("Test Category", "Test Description"))
            mysql.connection.commit()
            print("Successfully added Test Category.")
            
            cur.execute("SELECT * FROM categories WHERE name = 'Test Category'")
            cat = cur.fetchone()
            print(f"Retrieved: {cat}")
            
            # Now try products
            if cat:
                cat_id = cat['id']
                cur.execute("""
                    INSERT INTO products (name, category_id, price, quantity, description, image_url, low_stock_threshold) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, ("Test Product", cat_id, 99.99, 10, "Test Description", None, 5))
                mysql.connection.commit()
                print("Successfully added Test Product.")
                
                cur.execute("SELECT * FROM products WHERE name = 'Test Product'")
                prod = cur.fetchone()
                print(f"Retrieved: {prod}")
            
            cur.close()
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == '__main__':
    test_add()
