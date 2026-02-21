import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

try:
    with open('output.txt', 'w', encoding='utf-8') as f:
        try:
            connection = pymysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD'),
                database=os.environ.get('MYSQL_DB', 'inventory_db'),
                cursorclass=pymysql.cursors.DictCursor
            )

            with connection.cursor() as cursor:
                cursor.execute("DESCRIBE sales")
                rows = cursor.fetchall()
                f.write(f"Columns in sales table: {len(rows)}\n")
                for row in rows:
                    f.write(f"{row['Field']}: {row['Type']}\n")

            connection.close()
        except Exception as e:
            f.write(f"Error connecting/querying: {str(e)}\n")
except Exception as io_err:
    print(f"File IO Error: {io_err}")
