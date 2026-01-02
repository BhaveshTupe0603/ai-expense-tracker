import os
import pandas as pd
import sqlite3
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from database import init_db, get_db_connection
from ocr_engine import extract_text, parse_receipt_data, get_image_hash, check_duplicate_image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/expenses', methods=['GET', 'POST'])
def handle_expenses():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.json
        c = conn.cursor()
        
        # Check duplicates only for debits usually, but we check all here
        if data.get('source') == 'manual':
            c.execute("SELECT id FROM expenses WHERE date=? AND amount=? AND merchant=?", 
                      (data['date'], data['amount'], data['merchant']))
            if c.fetchone():
                return jsonify({"error": "Duplicate entry detected"}), 409

        # ... inside handle_expenses ...
        
        # CHANGED: Use data.get('currency', 'INR') to prevent crashes
        c.execute('''INSERT INTO expenses (date, merchant, amount, currency, category, type, payment_mode, notes, source, is_flagged, flag_reason)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data['date'], data['merchant'], data['amount'], data.get('currency', 'INR'), 
                   data['category'], data['type'], data['payment_mode'], data['notes'], 
                   data['source'], data.get('is_flagged', 0), data.get('flag_reason')))
        
        # ... rest of the function ...
        conn.commit()
        expense_id = c.lastrowid
        conn.close()
        return jsonify({"message": "Added", "id": expense_id}), 201

    # Return all expenses sorted by date
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in expenses])

@app.route('/api/expenses/<int:id>', methods=['PUT', 'DELETE'])
def modify_expense(id):
    conn = get_db_connection()
    c = conn.cursor()
    
    if request.method == 'DELETE':
        c.execute('DELETE FROM expenses WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Deleted"}), 200

    # ... inside modify_expense ...
    if request.method == 'PUT':
        data = request.json
        # CHANGED: Use data.get('currency', 'INR')
        c.execute('''UPDATE expenses 
                     SET date=?, merchant=?, amount=?, category=?, currency=?, type=? 
                     WHERE id=?''',
                  (data['date'], data['merchant'], data['amount'], data['category'], 
                   data.get('currency', 'INR'), data['type'], id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Updated"}), 200

@app.route('/api/upload', methods=['POST'])
def upload_bill():
    # This endpoint now ONLY SCANS and returns data. It does NOT save to DB.
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        img_hash = get_image_hash(filepath)
        conn = get_db_connection()
        existing = conn.execute("SELECT image_hash, id FROM expenses WHERE source='scanned'").fetchall()
        is_dup, orig_id = check_duplicate_image(img_hash, existing)
        
        flag_reason = f"Duplicate of ID {orig_id}" if is_dup else None
        is_flagged = 1 if is_dup else 0

        raw_text = extract_text(filepath)
        parsed = parse_receipt_data(raw_text)

        # Return data to frontend for verification
        response = parsed
        response['is_flagged'] = is_flagged
        response['flag_reason'] = flag_reason
        response['type'] = 'Debit' # Receipts are usually debits
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export', methods=['GET'])
def export_excel():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    filename = "expense_report.xlsx"
    df.to_excel(filename, index=False)
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)