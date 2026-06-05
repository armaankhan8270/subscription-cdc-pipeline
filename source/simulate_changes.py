import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "substrack.db")

def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def alice_upgrades_to_premium():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET plan = 'premium',
            plan_price = 79.00,
            updated_at = ?
        WHERE customer_id = 'CUST_001'
    """, (get_now(),))
    conn.commit()
    conn.close()
    print(f"Alice upgraded to Premium at {get_now()}")

def bob_downgrades_to_basic():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET plan = 'basic',
            plan_price = 29.00,
            updated_at = ?
        WHERE customer_id = 'CUST_002'
    """, (get_now(),))
    conn.commit()
    conn.close()
    print(f"Bob downgraded to Basic at {get_now()}")

def carol_cancels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET status = 'cancelled',
            updated_at = ?
        WHERE customer_id = 'CUST_003'
    """, (get_now(),))
    conn.commit()
    conn.close()
    print(f"Carol cancelled at {get_now()}")

def dave_upgrades_to_basic():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET plan = 'basic',
            plan_price = 29.00,
            updated_at = ?
        WHERE customer_id = 'CUST_004'
    """, (get_now(),))
    conn.commit()
    conn.close()
    print(f"Dave upgraded to Basic at {get_now()}")

def dave_upgrades_to_premium():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET plan = 'premium',
            plan_price = 79.00,
            updated_at = ?
        WHERE customer_id = 'CUST_004'
    """, (get_now(),))
    conn.commit()
    conn.close()
    print(f"Dave upgraded to Premium at {get_now()}")

def dave_downgrades_to_basic():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET plan = 'basic',
            plan_price = 29.00,
            updated_at = ?
        WHERE customer_id = 'CUST_004'
    """, (get_now(),))
    conn.commit()
    conn.close()
    print(f"Dave downgraded back to Basic at {get_now()}")

if __name__ == "__main__":
    print("Simulating customer changes...")
    print("Run individual functions as needed")
    print("Example: alice_upgrades_to_premium()")
