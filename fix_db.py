import sqlite3
from datetime import date

def reset_dates_to_january():
    print("🔄 Connecting to expenses.db...")
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    # FORCE UPDATE: Set all transaction dates to Today (or Jan 2nd)
    # This guarantees they appear in the current month's budget
    today_str = date.today().strftime('%Y-%m-%d')
    print(f"🔧 Resetting ALL transaction dates to: {today_str} (Current Month)...")
    
    c.execute("UPDATE expenses SET date = ?", (today_str,))
    
    # Check how many were updated
    rows_affected = c.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ Success! Moved {rows_affected} transactions to {today_str}.")
    print("🚀 Refresh your dashboard now. The budget bars should fill up!")

if __name__ == "__main__":
    reset_dates_to_january()