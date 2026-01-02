import sqlite3

DB_NAME = "expenses.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create table with columns for manual entry + AI fields
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            merchant TEXT,
            amount REAL,
            currency TEXT,
            category TEXT,
            payment_mode TEXT,
            notes TEXT,
            source TEXT, -- 'manual' or 'scanned'
            image_hash TEXT, -- For fraud detection
            is_flagged INTEGER DEFAULT 0, -- 0=No, 1=Yes
            flag_reason TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn