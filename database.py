import sqlite3

DB_NAME = 'expenses.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            age INTEGER,
            occupation TEXT,
            role TEXT,
            monthly_budget REAL DEFAULT 0
        )
    ''')

    # 2. Expenses Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT,
            merchant TEXT,
            amount REAL,
            currency TEXT,
            category TEXT,
            type TEXT,
            payment_mode TEXT,
            notes TEXT,
            source TEXT, 
            image_hash TEXT,
            is_flagged INTEGER DEFAULT 0,
            flag_reason TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # 3. Budgets Table (UPDATED FOR DATE RANGES)
    # Replaced 'monthly_limit' with 'amount', 'start_date', 'end_date'
    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT,
            amount REAL,
            start_date TEXT,
            end_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()