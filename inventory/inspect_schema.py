import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def inspect():
    with open('schema_info.txt', 'w') as f:
        try:
            connection = pymysql.connect(
                host=os.environ.get('MYSQL_HOST') or 'localhost',
                user=os.environ.get('MYSQL_USER') or 'root',
                password=os.environ.get('MYSQL_PASSWORD'),
                database=os.environ.get('MYSQL_DB') or 'inventory_db',
                cursorclass=pymysql.cursors.DictCursor
            )
            
            with connection.cursor() as cursor:
                f.write("--- Connection Successful ---\n")
                
                # Check Table
                cursor.execute("SHOW TABLES LIKE 'wallet_transactions'")
                if not cursor.fetchone():
                    f.write("Table 'wallet_transactions' DOES NOT EXIST.\n")
                else:
                    f.write("Table 'wallet_transactions' EXISTS.\n")
                    cursor.execute("DESCRIBE wallet_transactions")
                    columns = cursor.fetchall()
                    for col in columns:
                        f.write(str(col) + "\n")
            
            connection.close()
            
        except Exception as e:
            f.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    inspect()
