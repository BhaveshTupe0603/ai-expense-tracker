import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import date

from database import get_db_connection, init_db
from models import User
from ocr_engine import extract_text, get_image_hash, check_duplicate_image
from ai_assistant import get_ai_insight, clean_receipt_with_ai

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production' 
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup Login Manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# --- AUTH ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get all new fields
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form.get('full_name', '')
        age = request.form.get('age', 0)
        occupation = request.form.get('occupation', '')
        role = request.form.get('role', 'Employee') # Default to Employee if not selected

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user:
            flash('Username already exists.')
        else:
            hashed_pw = generate_password_hash(password, method='scrypt')
            # Insert with new profile fields
            conn.execute('''INSERT INTO users 
                         (username, email, password_hash, full_name, age, occupation, role) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (username, email, hashed_pw, full_name, age, occupation, role))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            # Create User object with ALL fields
            user = User(
                id=user_data['id'], 
                username=user_data['username'], 
                email=user_data['email'],
                full_name=user_data['full_name'],
                age=user_data['age'],
                occupation=user_data['occupation'],
                role=user_data['role'],
                monthly_budget=user_data['monthly_budget']
            )
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- DASHBOARD & API ---

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.json
    conn = get_db_connection()
    conn.execute('''UPDATE users SET full_name=?, age=?, occupation=?, role=? WHERE id=?''',
                 (data['name'], data['age'], data['occupation'], data['role'], current_user.id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Profile updated"}), 200

@app.route('/api/expenses', methods=['GET', 'POST'])
@login_required
def handle_expenses():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.json
        c = conn.cursor()
        
        c.execute('''INSERT INTO expenses (user_id, date, merchant, amount, currency, category, type, payment_mode, notes, source, is_flagged, flag_reason)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (current_user.id, 
                   data['date'], 
                   data['merchant'], 
                   data['amount'], 
                   data.get('currency', 'INR'), 
                   data['category'], 
                   data['type'], 
                   data.get('payment_mode', 'Cash'),
                   data.get('notes', ''),
                   data.get('source', 'manual'), 
                   data.get('is_flagged', 0), 
                   data.get('flag_reason')))
        
        conn.commit()
        conn.close()
        return jsonify({"message": "Saved"}), 201

    # --- GET LOGIC (UPDATED FOR MULTI-MONTH FILTERS) ---
    months_param = request.args.get('months') # Expecting "01,02,05"
    search = request.args.get('search') # Text
    
    query = "SELECT * FROM expenses WHERE user_id = ?"
    params = [current_user.id]

    # Filter by Multiple Months
    if months_param:
        month_list = months_param.split(',')
        # Create placeholders (?,?,?) based on number of selected months
        placeholders = ','.join(['?'] * len(month_list))
        query += f" AND strftime('%m', date) IN ({placeholders})"
        params.extend(month_list)
    
    # Filter by Search Text (Merchant or Category)
    if search:
        query += " AND (merchant LIKE ? OR category LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY date DESC"

    expenses = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(row) for row in expenses])

# --- EDIT & DELETE ROUTE ---
@app.route('/api/expenses/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def modify_expense(id):
    conn = get_db_connection()
    
    if request.method == 'DELETE':
        conn.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (id, current_user.id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Deleted"}), 200

    if request.method == 'PUT':
        data = request.json
        conn.execute('''UPDATE expenses 
                     SET date=?, merchant=?, amount=?, category=?, type=?, payment_mode=?
                     WHERE id=? AND user_id=?''',
                  (data['date'], data['merchant'], data['amount'], data['category'], 
                   data['type'], data.get('payment_mode', 'Cash'), id, current_user.id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Updated"}), 200

# --- SCANNER ROUTE ---
@app.route('/api/upload', methods=['POST'])
@login_required
def upload_bill():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # 1. Check for duplicates
        img_hash = get_image_hash(filepath)
        conn = get_db_connection()
        existing = conn.execute("SELECT image_hash, id FROM expenses WHERE source='scanned' AND user_id=?", (current_user.id,)).fetchall()
        is_dup, orig_id = check_duplicate_image(img_hash, existing)
        conn.close()

        # 2. Run OCR & AI Analysis
        raw_text = extract_text(filepath)
        ai_data = clean_receipt_with_ai(raw_text) 
        
        # --- ROBUST DEFAULTS ---
        if not ai_data:
            ai_data = {}

        if not ai_data.get('date'):
            ai_data['date'] = date.today().strftime('%Y-%m-%d')
            
        if not ai_data.get('merchant'): ai_data['merchant'] = "Unknown Merchant"
        if not ai_data.get('amount'): ai_data['amount'] = 0
        if not ai_data.get('category'): ai_data['category'] = "Other"

        response = ai_data
        response['is_flagged'] = 1 if is_dup else 0
        response['flag_reason'] = f"Duplicate of ID {orig_id}" if is_dup else None
        response['image_hash'] = img_hash
        response['image_url'] = f"/static/uploads/{filename}"
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    conn = get_db_connection()
    
    # 1. Get User Profile
    user_info = conn.execute('SELECT full_name, role, occupation FROM users WHERE id=?', (current_user.id,)).fetchone()
    
    # 2. Fetch expenses
    expenses = conn.execute('SELECT category, amount, date, merchant, type FROM expenses WHERE user_id = ?', (current_user.id,)).fetchall()
    
    # 3. Fetch Budgets (FIXED: using 'amount' column)
    budgets = conn.execute('SELECT category, amount FROM budgets WHERE user_id=?', (current_user.id,)).fetchall()
    budget_map = {b['category']: b['amount'] for b in budgets}
    
    conn.close()
    
    summary = {
        "user_profile": dict(user_info) if user_info else {},
        "total_transactions": len(expenses),
        "recent_transactions": [dict(row) for row in expenses[:5]],
        "category_budgets": budget_map
    }
    
    return jsonify({"response": get_ai_insight(data.get('message'), summary)})

@app.route('/api/export', methods=['GET'])
@login_required
def export_excel():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM expenses WHERE user_id = ?", conn, params=(current_user.id,))
    conn.close()
    filename = "expense_report.xlsx"
    df.to_excel(filename, index=False)
    return send_file(filename, as_attachment=True)

# --- BUDGET ROUTES ---

@app.route('/api/budgets', methods=['GET', 'POST'])
@login_required
def handle_budgets():
    conn = get_db_connection()
    
    # 1. CREATE NEW BUDGET
    if request.method == 'POST':
        data = request.json
        conn.execute('''INSERT INTO budgets (user_id, category, amount, start_date, end_date) 
                        VALUES (?, ?, ?, ?, ?)''',
                     (current_user.id, data['category'], data['amount'], data['start_date'], data['end_date']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Budget saved"}), 200

    # 2. GET BUDGETS & CALCULATE PROGRESS
    budgets = conn.execute('SELECT * FROM budgets WHERE user_id=? ORDER BY end_date DESC', 
                           (current_user.id,)).fetchall()
    
    budget_status = []
    for b in budgets:
        # Sum expenses ONLY within the budget's specific date range
        spent = conn.execute('''
            SELECT SUM(amount) FROM expenses 
            WHERE user_id=? AND category=? AND type='Debit' 
            AND date >= ? AND date <= ?
        ''', (current_user.id, b['category'], b['start_date'], b['end_date'])).fetchone()[0] or 0
        
        budget_status.append({
            "id": b['id'],
            "category": b['category'],
            "limit": b['amount'],
            "start_date": b['start_date'],
            "end_date": b['end_date'],
            "spent": spent,
            "percentage": min(100, (spent / b['amount']) * 100) if b['amount'] > 0 else 0
        })
    
    conn.close()
    return jsonify(budget_status)

@app.route('/api/budgets/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def modify_budget(id):
    conn = get_db_connection()
    
    if request.method == 'DELETE':
        conn.execute('DELETE FROM budgets WHERE id=? AND user_id=?', (id, current_user.id))
        
    elif request.method == 'PUT':
        data = request.json
        conn.execute('''UPDATE budgets SET category=?, amount=?, start_date=?, end_date=? 
                        WHERE id=? AND user_id=?''',
                     (data['category'], data['amount'], data['start_date'], data['end_date'], id, current_user.id))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Success"}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)