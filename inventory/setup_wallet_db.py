import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def setup_wallet():
    conn = mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'yusufimran787161'),
        database=os.environ.get('MYSQL_DB', 'inventory_db')
    )
    cursor = conn.cursor()

    print("Checking database for wallet requirements...")

    # 1. Create Wallets Table (One wallet per user)
    print("Creating wallets table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            balance DECIMAL(15, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 2. Recreate wallet_transactions table (Force correct schema)
    print("Dropping old wallet_transactions if exists...")
    cursor.execute("DROP TABLE IF EXISTS wallet_transactions")
    
    print("Creating wallet_transactions table...")
    cursor.execute("""
        CREATE TABLE wallet_transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            amount DECIMAL(15, 2) NOT NULL,
            type ENUM('CREDIT', 'DEBIT') NOT NULL,
            payment_method VARCHAR(50),
            transaction_id VARCHAR(100) NOT NULL UNIQUE,
            status VARCHAR(20) DEFAULT 'SUCCESS',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 3. Initialize Wallets for existing users
    print("Initializing wallets for existing users...")
    cursor.execute("INSERT IGNORE INTO wallets (user_id, balance) SELECT id, 0.00 FROM users")

    conn.commit()
    cursor.close()
    conn.close()
    print("Wallet setup completed successfully.")

if __name__ == '__main__':
    setup_wallet()
