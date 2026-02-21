import os
import time
import io
import secrets
import string
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from functools import wraps
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
# Import our modular models
from models import UserModel, CategoryModel, ProductModel, StockHistoryModel, CustomerModel, SupplierModel, SaleModel, PurchaseModel, WalletModel, TeamModel

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- Configuration ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'super-secret-key-donot-share'
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST') or 'localhost'
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER') or 'root'
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD') or 'yusufimran787161'
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB') or 'inventory_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Initialize Extensions ---
mysql = MySQL(app)
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# --- Initialize Models ---
user_model = UserModel(mysql)
category_model = CategoryModel(mysql)
product_model = ProductModel(mysql)
stock_model = StockHistoryModel(mysql, product_model)
customer_model = CustomerModel(mysql)
supplier_model = SupplierModel(mysql)
sale_model = SaleModel(mysql, customer_model)
purchase_model = PurchaseModel(mysql, supplier_model)
wallet_model = WalletModel(mysql)
team_model = TeamModel(mysql)


# --- Helpers ---
def is_logged_in():
    return 'user_id' in session

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied: Admins only', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def check_auth():
    open_routes = ['login', 'signup', 'static', 'google_callback', 'login_google']
    if request.endpoint not in open_routes and not is_logged_in():
        if request.endpoint:
            return redirect(url_for('login'))

# --- Routes ---
@app.route('/')
def index():
    return redirect(url_for('dashboard')) if is_logged_in() else redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username, email = request.form.get('username'), request.form.get('email')
        password, confirm = request.form.get('password'), request.form.get('confirm_password')

        if not all([username, email, password]):
            flash('Please fill out all fields', 'danger')
        elif password != confirm:
            flash('Passwords do not match', 'danger')
        else:
            try:
                user_model.create_user(username, email, password)
                flash('Account created successfully!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier, password = request.form.get('username'), request.form.get('password')
        user = user_model.find_by_identifier(identifier)
        if user and user_model.verify_password(user['password_hash'], password):
            session['user_id'], session['username'], session['role'] = user['id'], user['username'], user.get('role', 'user')
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/login/google')
def login_google():
    return google.authorize_redirect(url_for('google_callback', _external=True))

@app.route('/login/google/callback')
def google_callback():
    token = google.authorize_access_token()
    user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
    email, name = user_info['email'], user_info['name']
    
    user = user_model.find_by_identifier(email)
    if not user:
        rand_pass = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
        user_model.create_user(name, email, rand_pass)
        user = user_model.find_by_identifier(email)
    
    session['user_id'], session['username'], session['role'] = user['id'], user['username'], user.get('role', 'user')
    flash(f'Welcome back, {name}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    stats = product_model.get_stats()
    chart_data = product_model.get_chart_data()
    total_sales, outstanding_dues = sale_model.get_stats()
    total_purchases = purchase_model.get_stats()
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as count FROM categories")
    categories_count = cur.fetchone()['count']
    cur.execute("""
        SELECT sh.*, p.name as product_name 
        FROM stock_history sh
        LEFT JOIN products p ON sh.product_id = p.id
        ORDER BY sh.created_at DESC LIMIT 5
    """)
    recent_activity = cur.fetchall()
    
    # Get low stock items
    cur.execute("SELECT * FROM products WHERE quantity <= 5 ORDER BY quantity ASC LIMIT 5")
    low_stock = cur.fetchall()
    cur.close()

    wallet_balance = wallet_model.get_balance(session.get('user_id'))

    return render_template('dashboard.html', stats=stats, chart_data=chart_data, 
                         total_sales=total_sales, outstanding_dues=outstanding_dues, 
                         total_purchases=total_purchases, categories_count=categories_count,
                         recent_activity=recent_activity, low_stock=low_stock,
                         customers=customer_model.get_all(),
                         suppliers=supplier_model.get_all(),
                         wallet_balance=wallet_balance)





@app.route('/categories')
def categories():
    return render_template('categories.html', categories=category_model.get_all())

@app.route('/categories/add', methods=['POST'])
@admin_required
def add_category():
    name, desc = request.form.get('name'), request.form.get('description')
    if name:
        category_model.add(name, desc)
        flash('Category added', 'success')
    return redirect(url_for('categories'))

@app.route('/categories/edit/<int:id>', methods=['POST'])
@admin_required
def edit_category(id):
    name, desc = request.form.get('name'), request.form.get('description')
    category_model.update(id, name, desc)
    flash('Category updated', 'success')
    return redirect(url_for('categories'))

@app.route('/categories/delete/<int:id>')
@admin_required
def delete_category(id):
    category_model.delete(id)
    flash('Category deleted', 'success')
    return redirect(url_for('categories'))

@app.route('/products')
def products():
    return render_template('products.html', products=product_model.get_all(), categories=category_model.get_all())

@app.route('/products/add', methods=['POST'])
@admin_required
def add_product():
    data = request.form.to_dict()
    file = request.files.get('image')
    data['image_url'] = None
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{int(time.time())}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data['image_url'] = filename
    product_model.add(data)
    flash('Product added', 'success')
    return redirect(url_for('products'))

@app.route('/products/edit/<int:id>', methods=['POST'])
@admin_required
def edit_product(id):
    data = request.form.to_dict()
    product = product_model.get_by_id(id)
    file = request.files.get('image')
    data['image_url'] = product['image_url']
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{int(time.time())}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data['image_url'] = filename
    product_model.update(id, data)
    flash('Product updated', 'success')
    return redirect(url_for('products'))

@app.route('/products/delete/<int:id>')
@admin_required
def delete_product(id):
    product_model.delete(id)
    flash('Product deleted', 'success')
    return redirect(url_for('products'))

@app.route('/products/view/<int:id>')
def product_view(id):
    product = product_model.get_by_id(id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('products'))
    return render_template('product_view.html', product=product)

@app.route('/stock')
def stock():
    return render_template('stock.html', history=stock_model.get_all(), products=product_model.get_all())

@app.route('/stock/add', methods=['POST'])
@admin_required
def add_stock_transaction():
    p_id, t_type, qty, reason = request.form.get('product_id'), request.form.get('type'), request.form.get('quantity'), request.form.get('reason')
    if t_type == 'OUT' and product_model.get_by_id(p_id)['quantity'] < int(qty):
        flash('Insufficient stock', 'danger')
    else:
        stock_model.add_transaction(p_id, session.get('user_id'), t_type, qty, reason)
        flash('Stock updated', 'success')
    return redirect(url_for('stock'))

@app.route('/reports')
@admin_required
def reports():
    cur = mysql.connection.cursor()
    cur.execute("SELECT SUM(price * quantity) as total_value FROM products")
    total_value = cur.fetchone()['total_value'] or 0
    cur.execute("SELECT * FROM products WHERE quantity <= low_stock_threshold")
    low_stock = cur.fetchall()
    cur.execute("""
        SELECT c.name, COUNT(p.id) as product_count, SUM(p.quantity) as total_qty
        FROM categories c LEFT JOIN products p ON c.id = p.category_id GROUP BY c.id
    """)
    cat_stats = cur.fetchall()
    cur.close()
    return render_template('reports.html', total_value=total_value, low_stock_products=low_stock, category_stats=cat_stats)

@app.route('/export/products')
@admin_required
def export_products():
    products = product_model.get_all()
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory Report"
    headers = ['ID', 'Name', 'Category', 'Price (₹)', 'Quantity', 'Status', 'Description']
    ws.append(headers)
    for p in products:
        status = "Low Stock" if p['quantity'] <= p['low_stock_threshold'] else "Healthy"
        ws.append([p['id'], p['name'], p['category_name'], float(p['price']), p['quantity'], status, p['description'] or ""])
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name=f"Inventory_Report_{int(time.time())}.xlsx")

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = user_model.find_by_id(session['user_id'])
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_info':
            user_model.update_profile(session['user_id'], request.form.get('username'), request.form.get('email'))
            session['username'] = request.form.get('username')
            flash('Profile updated', 'success')
        elif action == 'change_password':
            if user_model.verify_password(user['password_hash'], request.form.get('old_password')):
                if request.form.get('new_password') == request.form.get('confirm_password'):
                    user_model.update_password(session['user_id'], request.form.get('new_password'))
                    flash('Password changed', 'success')
                else: flash('Passwords do not match', 'danger')
            else: flash('Incorrect old password', 'danger')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        session['theme'] = request.form.get('theme')
        flash('Settings saved', 'success')
    return render_template('settings.html')

@app.route('/users')
@admin_required
def users():
    return render_template('users.html', users=user_model.get_all_users())

@app.route('/users/role/<int:user_id>', methods=['POST'])
@admin_required
def update_user_role(user_id):
    user_model.update_role(user_id, request.form.get('role'))
    flash('User role updated', 'success')
    return redirect(url_for('users'))

@app.route('/users/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    if user_id == session.get('user_id'): flash('Cannot delete yourself', 'danger')
    else: 
        user_model.delete_user(user_id)
        flash('User deleted', 'success')
    return redirect(url_for('users'))

@app.route('/customers')
def customers():
    return render_template('customers.html', customers=customer_model.get_all())

@app.route('/customers/add', methods=['POST'])
def add_customer():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    id = customer_model.add(name, email, phone, address)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'status': 'success', 'id': id, 'name': name}
    flash('Customer added', 'success')
    return redirect(url_for('customers'))

@app.route('/customers/ledger/<int:id>')
def customer_ledger(id):
    customer = customer_model.get_all() # Just to find it
    customer = next((c for c in customer if c['id'] == id), None)
    if not customer:
        flash('Customer not found', 'danger')
        return redirect(url_for('customers'))
    return render_template('ledger.html', entity=customer, ledger=customer_model.get_ledger(id), type='Customer')

@app.route('/customers/edit/<int:id>', methods=['POST'])
def edit_customer(id):
    customer_model.update(id, request.form.get('name'), request.form.get('email'), request.form.get('phone'), request.form.get('address'))
    flash('Customer updated', 'success')
    return redirect(url_for('customers'))

@app.route('/customers/delete/<int:id>')
def delete_customer(id):
    customer_model.delete(id)
    flash('Customer deleted', 'success')
    return redirect(url_for('customers'))

@app.route('/suppliers')
def suppliers():
    return render_template('suppliers.html', suppliers=supplier_model.get_all())

@app.route('/suppliers/add', methods=['POST'])
def add_supplier():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    id = supplier_model.add(name, email, phone, address)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'status': 'success', 'id': id, 'name': name}
    flash('Supplier added', 'success')
    return redirect(url_for('suppliers'))

@app.route('/suppliers/edit/<int:id>', methods=['POST'])
def edit_supplier(id):
    supplier_model.update(id, request.form.get('name'), request.form.get('email'), request.form.get('phone'), request.form.get('address'))
    flash('Supplier updated', 'success')
    return redirect(url_for('suppliers'))

@app.route('/suppliers/delete/<int:id>')
def delete_supplier(id):
    supplier_model.delete(id)
    flash('Supplier deleted', 'success')
    return redirect(url_for('suppliers'))

@app.route('/suppliers/ledger/<int:id>')
def supplier_ledger(id):
    supplier = supplier_model.get_all()
    supplier = next((s for s in supplier if s['id'] == id), None)
    if not supplier:
        flash('Supplier not found', 'danger')
        return redirect(url_for('suppliers'))
    return render_template('ledger.html', entity=supplier, ledger=supplier_model.get_ledger(id), type='Supplier')

@app.route('/sales/add', methods=['POST'])
def add_sale():
    data = request.form
    try:
        total = float(data['total'])
        paid = float(data['paid'])
        due = total - paid
        sale_id = sale_model.add(int(data['customer_id']), total, paid, due, data['method'])
        flash(f'Sale recorded! Invoice #INV-{sale_id}', 'success')
    except Exception as e:
        flash(f'Error recording sale: {str(e)}', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/purchases/add', methods=['POST'])
def add_purchase():
    data = request.form
    try:
        total = float(data['total'])
        paid = float(data['paid'])
        due = total - paid
        purchase_id = purchase_model.add(int(data['supplier_id']), total, paid, due, data['method'])
        flash(f'Purchase recorded! Invoice #PUR-{purchase_id}', 'success')
    except Exception as e:
         flash(f'Error recording purchase: {str(e)}', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/invoice/<type>/<int:id>')
def generate_invoice(type, id):
    is_receipt = request.args.get('receipt', False)
    cur = mysql.connection.cursor()
    if type == 'sale':
        cur.execute("SELECT s.*, c.name as customer_name, c.email as customer_email, c.phone as customer_phone FROM sales s JOIN customers c ON s.customer_id = c.id WHERE s.id = %s", (id,))
    else:
        cur.execute("SELECT p.*, s.name as supplier_name, s.email as supplier_email, s.phone as supplier_phone FROM purchases p JOIN suppliers s ON p.supplier_id = s.id WHERE p.id = %s", (id,))
    data = cur.fetchone()
    cur.close()
    if not data:
        flash('Document not found', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('invoice.html', data=data, type=type, is_receipt=is_receipt)

@app.route('/members')
def members():
    return render_template('members.html', team=team_model.get_all())

@app.route('/admin/members', methods=['GET', 'POST'])
@admin_required
def manage_members():
    if request.method == 'POST':
        action = request.form.get('action')
        flash(f"Processing action: {action}", 'info')
        # Handle Image Upload
        file = request.files.get('image')
        image_url = request.form.get('image_url') # Fallback to URL if no file
        
        print(f"DEBUG: Action={action}, File={file.filename if file else 'None'}, URL={image_url}")

        if file and allowed_file(file.filename):
            filename = secure_filename(f"team_{int(time.time())}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = filename

        if action == 'add':
            print(f"Adding member: {request.form.get('name')}")
            try:
                team_model.add(
                    request.form.get('name'), 
                    request.form.get('role'), 
                    request.form.get('description'), 
                    image_url,
                    request.form.get('linkedin') or None,
                    request.form.get('github') or None,
                    request.form.get('email') or None
                )
                flash('Member added successfully', 'success')
            except Exception as e:
                print(f"ADD ERROR: {e}")
                flash(f"Error adding member: {e}", 'danger')
        elif action == 'edit':
            member_id = request.form.get('id')
            print(f"Editing member ID: {member_id}")
            # Keep old image if no new one provided
            if not (file and file.filename) and not request.form.get('image_url'):
                existing = team_model.get_by_id(member_id)
                if existing:
                    image_url = existing['image_url']
                    print(f"Keeping existing image: {image_url}")
            
            try:
                team_model.update(
                    member_id, 
                    request.form.get('name'), 
                    request.form.get('role'), 
                    request.form.get('description'), 
                    image_url,
                    request.form.get('linkedin') or None,
                    request.form.get('github') or None,
                    request.form.get('email') or None
                )
                flash('Member updated successfully', 'success')
            except Exception as e:
                print(f"UPDATE ERROR: {e}")
                flash(f"Error updating member: {e}", 'danger')
        return redirect(url_for('manage_members'))
    return render_template('manage_members.html', team=team_model.get_all())

@app.route('/admin/members/delete/<int:id>')
@admin_required
def delete_member(id):
    team_model.delete(id)
    flash('Member deleted', 'success')
    return redirect(url_for('manage_members'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/wallet', methods=['GET', 'POST'])
def wallet():
    if not is_logged_in(): return redirect(url_for('login'))
    user_id = session['user_id']
    
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount'))
            method = request.form.get('method', 'UPI')
            transaction_id = f"TXN-{secrets.token_hex(4).upper()}"
            
            if amount > 0:
                if wallet_model.add_transaction(user_id, amount, 'CREDIT', method, transaction_id, 'SUCCESS'):
                    flash(f'₹{amount} added to wallet successfully!', 'success')
                else:
                    flash('Transaction failed. Please try again.', 'danger')
            else:
                flash('Invalid amount entered.', 'danger')
        except ValueError:
            flash('Invalid amount format.', 'danger')
            
        return redirect(url_for('wallet'))

    balance = wallet_model.get_balance(user_id)
    transactions = wallet_model.get_transactions(user_id)
    
    total_credit = sum(float(t['amount']) for t in transactions if t['type'] == 'CREDIT')
    total_debit = sum(float(t['amount']) for t in transactions if t['type'] == 'DEBIT')

    return render_template('wallet.html', balance=balance, transactions=transactions, 
                         total_credit=total_credit, total_debit=total_debit)

@app.route('/wallet/edit/<int:id>', methods=['POST'])
def edit_wallet_transaction(id):
    if not is_logged_in(): return redirect(url_for('login'))
    amount = float(request.form.get('amount'))
    t_type = request.form.get('type')
    method = request.form.get('method')
    if wallet_model.update_transaction(id, amount, t_type, method):
        flash('Transaction corrected successfully', 'success')
    else:
        flash('Failed to update transaction', 'danger')
    return redirect(url_for('wallet'))

@app.route('/wallet/delete/<int:id>')
def delete_wallet_transaction(id):
    if not is_logged_in(): return redirect(url_for('login'))
    if wallet_model.delete_transaction(id):
        flash('Transaction deleted and balance adjusted', 'success')
    else:
        flash('Failed to delete transaction', 'danger')
    return redirect(url_for('wallet'))

@app.route('/admin/wallet')
@admin_required
def admin_wallet():
    transactions = wallet_model.get_all_transactions()
    return render_template('admin_wallet.html', transactions=transactions)

if __name__ == '__main__':
    print("Starting Hakeem Inventory System...")
    app.run(debug=True, host='0.0.0.0', port=5000)
