import os
import MySQLdb
from dotenv import load_dotenv

load_dotenv()

def migrate():
    try:
        conn = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            passwd=os.environ.get('MYSQL_PASSWORD', 'yusufimran787161'),
            db=os.environ.get('MYSQL_DB', 'inventory_db')
        )
        cur = conn.cursor()

        # Create Customers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(20),
                address TEXT,
                balance DECIMAL(10, 2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create Suppliers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(20),
                address TEXT,
                balance DECIMAL(10, 2) DEFAULT 0.00,
                status VARCHAR(50) DEFAULT 'Debtor',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create Sales table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                total_amount DECIMAL(10, 2) NOT NULL,
                paid_amount DECIMAL(10, 2) DEFAULT 0.00,
                due_amount DECIMAL(10, 2) DEFAULT 0.00,
                payment_method VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)

        # Create Purchases table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                supplier_id INT,
                total_amount DECIMAL(10, 2) NOT NULL,
                paid_amount DECIMAL(10, 2) DEFAULT 0.00,
                due_amount DECIMAL(10, 2) DEFAULT 0.00,
                payment_method VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        """)


        # Add image_url to products if not exists
        try:
            cur.execute("ALTER TABLE products ADD COLUMN image_url VARCHAR(255)")
        except:
            pass

        conn.commit()
        cur.close()
        conn.close()
        print("Migration completed successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == '__main__':
    migrate()
