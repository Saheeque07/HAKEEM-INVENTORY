import secrets
import string
import time
import os
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def create_user(self, username, email, password, role='user'):
        password_hash = generate_password_hash(password)
        cur = self.mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)", 
                    (username, email, password_hash, role))
        user_id = cur.lastrowid
        # Automatically create wallet record
        cur.execute("INSERT INTO wallets (user_id, balance) VALUES (%s, %s)", (user_id, 0.00))
        self.mysql.connection.commit()
        cur.close()

    def find_by_identifier(self, identifier):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (identifier, identifier))
        user = cur.fetchone()
        cur.close()
        return user

    def find_by_id(self, user_id):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        return user

    def verify_password(self, stored_hash, password):
        return check_password_hash(stored_hash, password)

    def update_profile(self, user_id, username, email):
        cur = self.mysql.connection.cursor()
        cur.execute("UPDATE users SET username = %s, email = %s WHERE id = %s", (username, email, user_id))
        self.mysql.connection.commit()
        cur.close()

    def update_password(self, user_id, new_password):
        password_hash = generate_password_hash(new_password)
        cur = self.mysql.connection.cursor()
        cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))
        self.mysql.connection.commit()
        cur.close()

    def get_all_users(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cur.fetchall()
        cur.close()
        return users

    def update_role(self, user_id, new_role):
        cur = self.mysql.connection.cursor()
        cur.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
        self.mysql.connection.commit()
        cur.close()

    def delete_user(self, user_id):
        cur = self.mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        self.mysql.connection.commit()
        cur.close()

class CategoryModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_all(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM categories ORDER BY name ASC")
        categories = cur.fetchall()
        cur.close()
        return categories
    
    def add(self, name, description):
        cur = self.mysql.connection.cursor()
        cur.execute("INSERT INTO categories (name, description) VALUES (%s, %s)", (name, description))
        self.mysql.connection.commit()
        cur.close()

    def update(self, cat_id, name, description):
        cur = self.mysql.connection.cursor()
        cur.execute("UPDATE categories SET name = %s, description = %s WHERE id = %s", (name, description, cat_id))
        self.mysql.connection.commit()
        cur.close()

    def delete(self, cat_id):
        cur = self.mysql.connection.cursor()
        cur.execute("DELETE FROM categories WHERE id = %s", (cat_id,))
        self.mysql.connection.commit()
        cur.close()

class ProductModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_all(self):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            ORDER BY p.name ASC
        """)
        products = cur.fetchall()
        cur.close()
        return products

    def get_by_id(self, product_id):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            WHERE p.id = %s
        """, (product_id,))
        product = cur.fetchone()
        cur.close()
        return product

    def add(self, data):
        cur = self.mysql.connection.cursor()
        price = float(data.get('price', 0)) if data.get('price') else 0.0
        quantity = int(data.get('quantity', 0)) if data.get('quantity') else 0
        threshold = int(data.get('low_stock_threshold', 10)) if data.get('low_stock_threshold') else 10
        cat_id = int(data.get('category_id')) if data.get('category_id') else None
        
        cur.execute("""
            INSERT INTO products (name, category_id, price, quantity, description, image_url, low_stock_threshold) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data['name'], cat_id, price, quantity, 
              data['description'], data['image_url'], threshold))
        self.mysql.connection.commit()
        cur.close()

    def update(self, product_id, data):
        cur = self.mysql.connection.cursor()
        price = float(data.get('price', 0)) if data.get('price') else 0.0
        quantity = int(data.get('quantity', 0)) if data.get('quantity') else 0
        threshold = int(data.get('low_stock_threshold', 10)) if data.get('low_stock_threshold') else 10
        cat_id = int(data.get('category_id')) if data.get('category_id') else None

        cur.execute("""
            UPDATE products 
            SET name = %s, category_id = %s, price = %s, quantity = %s, description = %s, image_url = %s, low_stock_threshold = %s 
            WHERE id = %s
        """, (data['name'], cat_id, price, quantity, 
              data['description'], data['image_url'], threshold, product_id))
        self.mysql.connection.commit()
        cur.close()

    def delete(self, product_id):
        cur = self.mysql.connection.cursor()
        cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
        self.mysql.connection.commit()
        cur.close()

    def update_quantity(self, product_id, amount):
        cur = self.mysql.connection.cursor()
        cur.execute("UPDATE products SET quantity = quantity + %s WHERE id = %s", (amount, product_id))
        self.mysql.connection.commit()
        cur.close()

    def get_stats(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as count FROM products")
        total_products = cur.fetchone()['count']
        cur.execute("SELECT SUM(quantity) as total_stock FROM products")
        result = cur.fetchone()
        total_stock = result['total_stock'] if result['total_stock'] is not None else 0
        cur.execute("SELECT COUNT(*) as low_stock FROM products WHERE quantity <= low_stock_threshold")
        low_stock_count = cur.fetchone()['low_stock']
        cur.execute("SELECT COUNT(*) as count FROM categories")
        total_categories = cur.fetchone()['count']
        cur.close()
        return {
            'total_products': total_products,
            'total_stock': total_stock,
            'low_stock_count': low_stock_count,
            'total_categories': total_categories
        }

    def get_chart_data(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT name, quantity FROM products ORDER BY quantity DESC LIMIT 5")
        bar_data = cur.fetchall()
        cur.execute("""
            SELECT c.name, COUNT(p.id) as count 
            FROM categories c 
            LEFT JOIN products p ON c.id = p.category_id 
            GROUP BY c.id
        """)
        pie_data = cur.fetchall()
        cur.close()
        return {
            'bar_labels': [item['name'] for item in bar_data],
            'bar_values': [item['quantity'] for item in bar_data],
            'pie_labels': [item['name'] for item in pie_data],
            'pie_values': [item['count'] for item in pie_data]
        }

class StockHistoryModel:
    def __init__(self, mysql, product_model):
        self.mysql = mysql
        self.product_model = product_model

    def get_all(self):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            SELECT sh.*, p.name as product_name, u.username 
            FROM stock_history sh
            LEFT JOIN products p ON sh.product_id = p.id
            LEFT JOIN users u ON sh.user_id = u.id
            ORDER BY sh.created_at DESC
        """)
        history = cur.fetchall()
        cur.close()
        return history

    def add_transaction(self, product_id, user_id, type_in_out, quantity, reason):
        qty = int(quantity) if quantity else 0
        if qty <= 0: raise ValueError("Quantity must be greater than zero")
        cur = self.mysql.connection.cursor()
        cur.execute("""
            INSERT INTO stock_history (product_id, user_id, type, quantity, reason) 
            VALUES (%s, %s, %s, %s, %s)
        """, (product_id, user_id, type_in_out, qty, reason))
        self.mysql.connection.commit()
        cur.close()
        change = qty if type_in_out == 'IN' else -qty
        self.product_model.update_quantity(product_id, change)

class CustomerModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_all(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM customers ORDER BY name ASC")
        customers = cur.fetchall()
        cur.close()
        return customers

    def add(self, name, email, phone, address):
        cur = self.mysql.connection.cursor()
        cur.execute("INSERT INTO customers (name, email, phone, address) VALUES (%s, %s, %s, %s)", 
                    (name, email, phone, address))
        last_id = cur.lastrowid
        self.mysql.connection.commit()
        cur.close()
        return last_id

    def update_balance(self, customer_id, amount):
        cur = self.mysql.connection.cursor()
        cur.execute("UPDATE customers SET balance = balance + %s WHERE id = %s", (amount, customer_id))
        self.mysql.connection.commit()
        cur.close()

    def update(self, customer_id, name, email, phone, address):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            UPDATE customers SET name = %s, email = %s, phone = %s, address = %s 
            WHERE id = %s
        """, (name, email, phone, address, customer_id))
        self.mysql.connection.commit()
        cur.close()

    def delete(self, customer_id):
        cur = self.mysql.connection.cursor()
        cur.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
        self.mysql.connection.commit()
        cur.close()

    def get_ledger(self, customer_id):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            SELECT 'SALE' as type, id, total_amount, paid_amount, due_amount, created_at 
            FROM sales WHERE customer_id = %s
            ORDER BY created_at DESC
        """, (customer_id,))
        ledger = cur.fetchall()
        cur.close()
        return ledger

class SupplierModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_all(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM suppliers ORDER BY name ASC")
        suppliers = cur.fetchall()
        cur.close()
        return suppliers

    def add(self, name, email, phone, address):
        cur = self.mysql.connection.cursor()
        cur.execute("INSERT INTO suppliers (name, email, phone, address) VALUES (%s, %s, %s, %s)", 
                    (name, email, phone, address))
        last_id = cur.lastrowid
        self.mysql.connection.commit()
        cur.close()
        return last_id

    def update_balance(self, supplier_id, amount):
        cur = self.mysql.connection.cursor()
        cur.execute("UPDATE suppliers SET balance = balance + %s WHERE id = %s", (amount, supplier_id))
        cur.execute("UPDATE suppliers SET status = IF(balance > 0, 'Creditor', 'Debtor') WHERE id = %s", (supplier_id,))
        self.mysql.connection.commit()
        cur.close()

    def update(self, supplier_id, name, email, phone, address):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            UPDATE suppliers SET name = %s, email = %s, phone = %s, address = %s 
            WHERE id = %s
        """, (name, email, phone, address, supplier_id))
        self.mysql.connection.commit()
        cur.close()

    def delete(self, supplier_id):
        cur = self.mysql.connection.cursor()
        cur.execute("DELETE FROM suppliers WHERE id = %s", (supplier_id,))
        self.mysql.connection.commit()
        cur.close()

    def get_ledger(self, supplier_id):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            SELECT 'PURCHASE' as type, id, total_amount, paid_amount, due_amount, created_at 
            FROM purchases WHERE supplier_id = %s
            ORDER BY created_at DESC
        """, (supplier_id,))
        ledger = cur.fetchall()
        cur.close()
        return ledger

class SaleModel:
    def __init__(self, mysql, customer_model):
        self.mysql = mysql
        self.customer_model = customer_model

    def add(self, customer_id, total, paid, due, method):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            INSERT INTO sales (customer_id, total_amount, paid_amount, due_amount, payment_method) 
            VALUES (%s, %s, %s, %s, %s)
        """, (customer_id, total, paid, due, method))
        sale_id = cur.lastrowid
        self.mysql.connection.commit()
        cur.close()
        if due > 0:
            self.customer_model.update_balance(customer_id, due)
        return sale_id

    def get_stats(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT SUM(total_amount) as total_sales FROM sales")
        total_sales = cur.fetchone()['total_sales'] or 0
        cur.execute("SELECT SUM(due_amount) as outstanding_sales FROM sales")
        outstanding_sales = cur.fetchone()['outstanding_sales'] or 0
        cur.close()
        return total_sales, outstanding_sales

class PurchaseModel:
    def __init__(self, mysql, supplier_model):
        self.mysql = mysql
        self.supplier_model = supplier_model

    def add(self, supplier_id, total, paid, due, method):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            INSERT INTO purchases (supplier_id, total_amount, paid_amount, due_amount, payment_method) 
            VALUES (%s, %s, %s, %s, %s)
        """, (supplier_id, total, paid, due, method))
        purchase_id = cur.lastrowid
        self.mysql.connection.commit()
        cur.close()
        if due > 0:
            self.supplier_model.update_balance(supplier_id, due)
        return purchase_id

    def get_stats(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT SUM(total_amount) as total_purchases FROM purchases")
        total_purchases = cur.fetchone()['total_purchases'] or 0
        cur.close()
        return total_purchases

class WalletModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_balance(self, user_id):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT balance FROM wallets WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        if not result:
            # Fallback/Safety: Create wallet if missing
            cur.execute("INSERT IGNORE INTO wallets (user_id, balance) VALUES (%s, %s)", (user_id, 0.00))
            self.mysql.connection.commit()
            cur.close()
            return 0.0
        cur.close()
        return float(result['balance'])

    def add_transaction(self, user_id, amount, type, method, transaction_id, status='SUCCESS'):
        cur = self.mysql.connection.cursor()
        try:
            # 1. Add Transaction
            cur.execute("""
                INSERT INTO wallet_transactions (user_id, amount, type, payment_method, transaction_id, status) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, amount, type, method, transaction_id, status))
            
            # 2. Update Balance in Wallets Table if SUCCESS
            if status == 'SUCCESS':
                if type == 'CREDIT':
                    cur.execute("UPDATE wallets SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
                elif type == 'DEBIT':
                    cur.execute("UPDATE wallets SET balance = balance - %s WHERE user_id = %s", (amount, user_id))
            
            self.mysql.connection.commit()
            return True
        except Exception as e:
            self.mysql.connection.rollback()
            print(f"Error adding transaction: {e}")
            return False
        finally:
            cur.close()

    def get_transaction_by_id(self, tx_id):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM wallet_transactions WHERE id = %s", (tx_id,))
        tx = cur.fetchone()
        cur.close()
        return tx

    def update_transaction(self, tx_id, amount, type, method, status='SUCCESS'):
        cur = self.mysql.connection.cursor()
        try:
            # 1. Get old transaction
            cur.execute("SELECT * FROM wallet_transactions WHERE id = %s", (tx_id,))
            old_tx = cur.fetchone()
            if not old_tx: return False

            # 2. Reverse old balance change if it was SUCCESS
            if old_tx['status'] == 'SUCCESS':
                if old_tx['type'] == 'CREDIT':
                    cur.execute("UPDATE wallets SET balance = balance - %s WHERE user_id = %s", (old_tx['amount'], old_tx['user_id']))
                else:
                    cur.execute("UPDATE wallets SET balance = balance + %s WHERE user_id = %s", (old_tx['amount'], old_tx['user_id']))

            # 3. Update record
            cur.execute("""
                UPDATE wallet_transactions 
                SET amount = %s, type = %s, payment_method = %s, status = %s 
                WHERE id = %s
            """, (amount, type, method, status, tx_id))

            # 4. Apply new balance change if SUCCESS
            if status == 'SUCCESS':
                if type == 'CREDIT':
                    cur.execute("UPDATE wallets SET balance = balance + %s WHERE user_id = %s", (amount, old_tx['user_id']))
                else:
                    cur.execute("UPDATE wallets SET balance = balance - %s WHERE user_id = %s", (amount, old_tx['user_id']))

            self.mysql.connection.commit()
            return True
        except Exception as e:
            self.mysql.connection.rollback()
            print(f"Error updating transaction: {e}")
            return False
        finally:
            cur.close()

    def delete_transaction(self, tx_id):
        cur = self.mysql.connection.cursor()
        try:
            # 1. Get transaction
            cur.execute("SELECT * FROM wallet_transactions WHERE id = %s", (tx_id,))
            tx = cur.fetchone()
            if not tx: return False

            # 2. Reverse balance change if it was SUCCESS
            if tx['status'] == 'SUCCESS':
                if tx['type'] == 'CREDIT':
                    cur.execute("UPDATE wallets SET balance = balance - %s WHERE user_id = %s", (tx['amount'], tx['user_id']))
                else:
                    cur.execute("UPDATE wallets SET balance = balance + %s WHERE user_id = %s", (tx['amount'], tx['user_id']))

            # 3. Delete record
            cur.execute("DELETE FROM wallet_transactions WHERE id = %s", (tx_id,))
            
            self.mysql.connection.commit()
            return True
        except Exception as e:
            self.mysql.connection.rollback()
            print(f"Error deleting transaction: {e}")
            return False
        finally:
            cur.close()

    def get_transactions(self, user_id, limit=20):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM wallet_transactions WHERE user_id = %s ORDER BY created_at DESC LIMIT %s", (user_id, limit))
        txs = cur.fetchall()
        cur.close()
        return txs

    def get_all_transactions(self):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            SELECT wt.*, u.username, u.email 
            FROM wallet_transactions wt 
            JOIN users u ON wt.user_id = u.id 
            ORDER BY wt.created_at DESC
        """)
        txs = cur.fetchall()
        cur.close()
        return txs

class TeamModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_all(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM team_members ORDER BY id ASC")
        members = cur.fetchall()
        cur.close()
        return members

    def get_by_id(self, member_id):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM team_members WHERE id = %s", (member_id,))
        member = cur.fetchone()
        cur.close()
        return member

    def add(self, name, role, description, image_url, linkedin=None, github=None, email=None):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            INSERT INTO team_members (name, role, description, image_url, linkedin, github, email) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, role, description, image_url, linkedin, github, email))
        self.mysql.connection.commit()
        cur.close()

    def update(self, member_id, name, role, description, image_url, linkedin=None, github=None, email=None):
        cur = self.mysql.connection.cursor()
        cur.execute("""
            UPDATE team_members SET name = %s, role = %s, description = %s, image_url = %s, 
            linkedin = %s, github = %s, email = %s 
            WHERE id = %s
        """, (name, role, description, image_url, linkedin, github, email, member_id))
        self.mysql.connection.commit()
        cur.close()

    def delete(self, member_id):
        cur = self.mysql.connection.cursor()
        cur.execute("DELETE FROM team_members WHERE id = %s", (member_id,))
        self.mysql.connection.commit()
        cur.close()




