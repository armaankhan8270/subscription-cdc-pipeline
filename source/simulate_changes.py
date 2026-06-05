import sqlite3
import os
import random
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "substrack.db")
random.seed(42)

def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def batch_plan_changes(pct=0.05):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.execute("SELECT customer_id, plan FROM customers WHERE status = 'active' ORDER BY RANDOM() LIMIT (SELECT CAST(COUNT(*) * ? AS INTEGER) FROM customers WHERE status = 'active')", (pct,))
    targets = cursor.fetchall()
    for cust_id, current_plan in targets:
        new_plan = random.choice([p for p in ["free", "basic", "premium", "enterprise"] if p != current_plan])
        new_price = {"free": 0, "basic": 29, "premium": 79, "enterprise": 299}[new_plan]
        cursor.execute("UPDATE customers SET plan = ?, plan_price = ?, updated_at = ? WHERE customer_id = ?", (new_plan, new_price, now, cust_id))
        cursor.execute("UPDATE subscriptions SET plan_type = ?, plan_price = ?, updated_at = ? WHERE customer_id = ? AND status = 'active'", (new_plan, new_price, now, cust_id))
    conn.commit()
    conn.close()
    print(f"Batch plan changes: {len(targets)} customers updated at {now}")

def batch_cancellations(pct=0.02):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    now_date = now[:10]
    cursor.execute("SELECT customer_id FROM customers WHERE status = 'active' ORDER BY RANDOM() LIMIT (SELECT CAST(COUNT(*) * ? AS INTEGER) FROM customers WHERE status = 'active')", (pct,))
    targets = cursor.fetchall()
    for (cust_id,) in targets:
        cursor.execute("UPDATE customers SET status = 'cancelled', updated_at = ? WHERE customer_id = ?", (now, cust_id))
        cursor.execute("UPDATE subscriptions SET status = 'cancelled', end_date = ?, updated_at = ? WHERE customer_id = ? AND status = 'active'", (now_date, now, cust_id))
    conn.commit()
    conn.close()
    print(f"Batch cancellations: {len(targets)} customers cancelled at {now}")

def batch_new_tickets(count=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.execute("SELECT customer_id FROM customers WHERE status = 'active' ORDER BY RANDOM() LIMIT ?", (count,))
    targets = cursor.fetchall()
    subjects = [
        "Cannot access dashboard", "Billing question", "API rate limit",
        "Feature request", "Performance issue", "Login problem",
        "Data export request", "Integration help", "Account settings",
        "Security concern",
    ]
    tid = cursor.execute("SELECT COUNT(*) FROM support_tickets").fetchone()[0] + 1
    for (cust_id,) in targets:
        subject = random.choice(subjects)
        priority = random.choice(["low", "medium", "high"])
        cursor.execute("""
            INSERT INTO support_tickets (ticket_id, customer_id, subject, description, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'open', ?, ?)
        """, (f"TKT_{tid:04d}", cust_id, subject, f"Auto-generated ticket about: {subject}", priority, now, now))
        tid += 1
    conn.commit()
    conn.close()
    print(f"Batch new tickets: {count} tickets created at {now}")

def batch_usage_events(count=200):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    cursor.execute("SELECT customer_id FROM customers WHERE status = 'active' ORDER BY RANDOM() LIMIT ?", (count,))
    targets = cursor.fetchall()
    event_types = ["api_call", "storage_gb", "bandwidth_gb", "users_count"]
    eid = cursor.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0] + 1
    for (cust_id,) in targets:
        etype = random.choice(event_types)
        qty = {"api_call": random.randint(10, 3000), "storage_gb": round(random.uniform(0.1, 500), 1),
               "bandwidth_gb": round(random.uniform(0.1, 800), 1), "users_count": random.randint(1, 150)}[etype]
        cursor.execute("""
            INSERT INTO usage_events (event_id, customer_id, event_type, quantity, recorded_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (f"EVT_{eid:05d}", cust_id, etype, qty, now, now))
        eid += 1
    conn.commit()
    conn.close()
    print(f"Batch usage events: {count} events created at {now}")

def batch_new_invoices(count=100):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    now_date = now[:10]
    cursor.execute("SELECT customer_id, plan_price FROM customers WHERE status = 'active' ORDER BY RANDOM() LIMIT ?", (count,))
    targets = cursor.fetchall()
    iid = cursor.execute("SELECT COUNT(*) FROM billing_invoices").fetchone()[0] + 1
    for (cust_id, price) in targets:
        status = random.choices(["paid", "pending", "overdue"], weights=[70, 20, 10])[0]
        paid_at = now if status == "paid" else None
        cursor.execute("""
            INSERT INTO billing_invoices (invoice_id, customer_id, amount, currency, status, due_date, paid_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (f"INV_{iid:05d}", cust_id, price, "USD", status, now_date, paid_at, now, now))
        iid += 1
    conn.commit()
    conn.close()
    print(f"Batch new invoices: {count} invoices created at {now}")

if __name__ == "__main__":
    print("Batch simulation controls for 1000+ customer dataset")
    print()
    print("Functions:")
    print("  batch_plan_changes(pct=0.05)  — Randomly change plans for 5% of active customers")
    print("  batch_cancellations(pct=0.02) — Cancel 2% of active customers")
    print("  batch_new_tickets(count=50)   — Create 50 new support tickets")
    print("  batch_usage_events(count=200) — Create 200 new usage events")
    print("  batch_new_invoices(count=100) — Create 100 new invoices")
