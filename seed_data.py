import sqlite3
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

DB_NAME = 'expenses.db'

def get_random_date_in_month(year, month):
    """Generates a random date within a specific month"""
    # Handle Feb (leap year check not strictly needed for demo, assuming 28 days)
    if month == 2:
        max_days = 28
    elif month in [4, 6, 9, 11]:
        max_days = 30
    else:
        max_days = 31
        
    day = random.randint(1, max_days)
    return f"{year}-{month:02d}-{day:02d}"

def seed_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    users = [
        {
            "username": "student", "email": "student@demo.com", "password": "pass",
            "full_name": "Rahul Verma", "age": 21, "occupation": "B.Tech Student", "role": "Student",
            "expenses": [
                ("Food", "McDonalds", 250), ("Food", "College Canteen", 80), ("Travel", "Metro Card", 500),
                ("Utilities", "Mobile Recharge", 299), ("Shopping", "Course Books", 1200), ("Food", "Chai Point", 40),
                ("Travel", "Uber to Mall", 350), ("Utilities", "Spotify", 119), ("Food", "Maggi Point", 60),
                ("Shopping", "New T-Shirt", 600), ("Travel", "Bus Ticket", 20)
            ],
            "income": ("Dad (Pocket Money)", 8000)
        },
        {
            "username": "employee", "email": "employee@demo.com", "password": "pass",
            "full_name": "Priya Sharma", "age": 28, "occupation": "Software Engineer", "role": "Employee",
            "expenses": [
                ("Food", "Grocery Mart", 4500), ("Utilities", "Electricity Bill", 1200), ("Travel", "Fuel", 3000),
                ("Shopping", "Myntra Sale", 5500), ("Food", "Zomato Orders", 650), ("Utilities", "Wifi Bill", 999),
                ("Medical", "Pharmacy", 1500), ("Travel", "Flight Tickets", 8000), ("Food", "Fine Dining", 2500),
                ("Utilities", "Netflix", 649), ("Other", "Gym Membership", 1500)
            ],
            "income": ("Salary Credit", 85000)
        },
        {
            "username": "startup", "email": "founder@demo.com", "password": "pass",
            "full_name": "Vikram Singh", "age": 34, "occupation": "CEO", "role": "Startup",
            "expenses": [
                ("Utilities", "AWS Server Bill", 15000), ("Shopping", "Office Chairs", 25000), ("Travel", "Client Visit", 4500),
                ("Food", "Team Lunch", 6000), ("Utilities", "Marketing Ads", 12000), ("Utilities", "Zoom Subscription", 2000),
                ("Other", "Legal Fees", 10000), ("Travel", "Bangalore Trip", 12000), ("Utilities", "Office Rent", 40000),
                ("Utilities", "Internet Leased Line", 3000)
            ],
            "income": ("Client Invoice", 150000)
        }
    ]

    print("🚀 Adding RICH Monthly Data for 2025...")

    for u in users:
        print(f"   👤 Processing: {u['username']}...")
        
        # 1. Get or Create User
        existing = c.execute("SELECT id FROM users WHERE username=?", (u['username'],)).fetchone()
        
        if existing:
            user_id = existing[0]
        else:
            hashed_pw = generate_password_hash(u['password'], method='scrypt')
            c.execute('''INSERT INTO users (username, email, password_hash, full_name, age, occupation, role) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                      (u['username'], u['email'], hashed_pw, u['full_name'], u['age'], u['occupation'], u['role']))
            user_id = c.lastrowid

        # 2. Loop through EVERY MONTH (Jan to Dec)
        for month in range(1, 13):
            income_src, income_amt = u['income']
            income_date = f"2025-{month:02d}-01"

            # --- A. CHECK IF SALARY ALREADY EXISTS FOR THIS MONTH ---
            # We check if there's already a 'Credit' transaction on the 1st of this month for this user.
            salary_exists = c.execute('''
                SELECT id FROM expenses 
                WHERE user_id=? AND date=? AND type='Credit'
            ''', (user_id, income_date)).fetchone()

            if not salary_exists:
                # Add Monthly Income (Credit) - ONLY if not present
                final_income = income_amt
                if u['role'] == "Startup": 
                    final_income += random.randint(-20000, 50000) # Startup income varies

                c.execute('''INSERT INTO expenses (user_id, date, merchant, amount, category, type, payment_mode, source) 
                             VALUES (?, ?, ?, ?, 'Salary', 'Credit', 'Bank', 'demo_seed')''', 
                          (user_id, income_date, income_src, final_income))
            
            # --- B. Add 8-12 Expenses PER MONTH (Debit) ---
            # We always add expenses to make the chart richer (even if we run it again)
            num_txns = random.randint(8, 12)
            for _ in range(num_txns):
                cat, merch, base_amt = random.choice(u['expenses'])
                
                # Add randomness to amount (+/- 20%)
                variance = int(base_amt * 0.2)
                final_amt = base_amt + random.randint(-variance, variance)
                if final_amt <= 0: final_amt = 50

                txn_date = get_random_date_in_month(2025, month)
                
                c.execute('''INSERT INTO expenses (user_id, date, merchant, amount, category, type, payment_mode, source)
                             VALUES (?, ?, ?, ?, ?, 'Debit', 'UPI', 'demo_seed')''',
                          (user_id, txn_date, merch, final_amt, cat))

    conn.commit()
    conn.close()
    print("✅ Success! Added dense monthly data for Jan-Dec 2025.")

if __name__ == "__main__":
    seed_data()