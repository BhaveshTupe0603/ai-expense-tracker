import os
import sqlite3

DB_NAME = "expenses.db"

# 1. Delete the old database file if it exists
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print("Old database deleted.")

# 2. Create the new database with the 'type' column
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        merchant TEXT,
        amount REAL,
        currency TEXT,
        category TEXT,
        type TEXT, -- This is the missing column you need
        payment_mode TEXT,
        notes TEXT,
        source TEXT, 
        image_hash TEXT,
        is_flagged INTEGER DEFAULT 0,
        flag_reason TEXT
    )
''')
conn.commit()
conn.close()
print("New database created successfully with 'type' column!")