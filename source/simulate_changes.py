import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "substrack.db")

def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def alice_upgrades_to_premium():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.execute("""
        UPDATE customers
        SET plan = 'premium', plan_price = 79.00, updated_at = ?
        WHERE customer_id = 'CUST_001'
    """, (now,))
    cursor.execute("""
        UPDATE subscriptions
        SET plan_type = 'premium', plan_price = 79.00, updated_at = ?
        WHERE customer_id = 'CUST_001' AND status = 'active'
    """, (now,))
    conn.commit()
    conn.close()
    print(f"Alice upgraded to Premium at {now}")

def bob_downgrades_to_basic():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.execute("""
        UPDATE customers
        SET plan = 'basic', plan_price = 29.00, updated_at = ?
        WHERE customer_id = 'CUST_002'
    """, (now,))
    cursor.execute("""
        UPDATE subscriptions
        SET plan_type = 'basic', plan_price = 29.00, updated_at = ?
        WHERE customer_id = 'CUST_002' AND status = 'active'
    """, (now,))
    conn.commit()
    conn.close()
    print(f"Bob downgraded to Basic at {now}")

def carol_cancels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.execute("""
        UPDATE customers
        SET status = 'cancelled', updated_at = ?
        WHERE customer_id = 'CUST_003'
    """, (now,))
    cursor.execute("""
        UPDATE subscriptions
        SET status = 'cancelled', end_date = ?, updated_at = ?
        WHERE customer_id = 'CUST_003' AND status = 'active'
    """, (now[:10], now))
    conn.commit()
    conn.close()
    print(f"Carol cancelled at {now}")

def dave_upgrades_to_basic():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.execute("""
        UPDATE customers
        SET plan = 'basic', plan_price = 29.00, updated_at = ?
        WHERE customer_id = 'CUST_004'
    """, (now,))
    cursor.execute("""
        UPDATE subscriptions
        SET plan_type = 'basic', plan_price = 29.00, updated_at = ?
        WHERE customer_id = 'CUST_004' AND status = 'active'
    """, (now,))
    conn.commit()
    conn.close()
    print(f"Dave upgraded to Basic at {now}")

def dave_upgrades_to_premium():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.execute("""
        UPDATE customers
        SET plan = 'premium', plan_price = 79.00, updated_at = ?
        WHERE customer_id = 'CUST_004'
    """, (now,))
    cursor.execute("""
        UPDATE subscriptions
        SET plan_type = 'premium', plan_price = 79.00, updated_at = ?
        WHERE customer_id = 'CUST_004' AND status = 'active'
    """, (now,))
    conn.commit()
    conn.close()
    print(f"Dave upgraded to Premium at {now}")

def dave_downgrades_to_basic():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.execute("""
        UPDATE customers
        SET plan = 'basic', plan_price = 29.00, updated_at = ?
        WHERE customer_id = 'CUST_004'
    """, (now,))
    cursor.execute("""
        UPDATE subscriptions
        SET plan_type = 'basic', plan_price = 29.00, updated_at = ?
        WHERE customer_id = 'CUST_004' AND status = 'active'
    """, (now,))
    conn.commit()
    conn.close()
    print(f"Dave downgraded back to Basic at {now}")

def eve_updates_payment():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.execute("""
        UPDATE payment_methods
        SET last_four = '4444', exp_year = 2028, updated_at = ?
        WHERE customer_id = 'CUST_005' AND is_default = 1
    """, (now,))
    conn.commit()
    conn.close()
    print(f"Eve updated payment card at {now}")

def frank_opens_ticket():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.execute("""
        INSERT INTO support_tickets
        (ticket_id, customer_id, subject, description, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ("TKT_009", "CUST_006", "Billing discrepancy", "Charged twice for May invoice", "high", "open", now, now))
    conn.commit()
    conn.close()
    print(f"Frank opened new support ticket at {now}")

def alice_usage_spike():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.executemany("""
        INSERT INTO usage_events (event_id, customer_id, event_type, quantity, recorded_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (f"EVT_021", "CUST_001", "api_call", 1500, now, now),
        (f"EVT_022", "CUST_001", "bandwidth_gb", 320.5, now, now),
        (f"EVT_023", "CUST_001", "storage_gb", 45.2, now, now),
    ])
    conn.commit()
    conn.close()
    print(f"Alice usage spike recorded at {now}")

if __name__ == "__main__":
    print("Simulating changes across all tables...")
    print("Available functions:")
    print("  alice_upgrades_to_premium()")
    print("  bob_downgrades_to_basic()")
    print("  carol_cancels()")
    print("  dave_upgrades_to_basic()")
    print("  dave_upgrades_to_premium()")
    print("  dave_downgrades_to_basic()")
    print("  eve_updates_payment()")
    print("  frank_opens_ticket()")
    print("  alice_usage_spike()")
