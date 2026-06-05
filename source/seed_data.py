import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "substrack.db")

def seed_customers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    customers = [
        (
            "CUST_001", "alice@example.com", "Alice Johnson",
            "basic", 29.00, "active",
            "2024-01-01", "2024-01-01 00:00:00"
        ),
        (
            "CUST_002", "bob@example.com", "Bob Smith",
            "premium", 79.00, "active",
            "2024-01-15", "2024-01-15 00:00:00"
        ),
        (
            "CUST_003", "carol@example.com", "Carol White",
            "enterprise", 299.00, "active",
            "2024-02-01", "2024-02-01 00:00:00"
        ),
        (
            "CUST_004", "dave@example.com", "Dave Brown",
            "free", 0.00, "active",
            "2024-01-20", "2024-01-20 00:00:00"
        ),
        (
            "CUST_005", "eve@example.com", "Eve Davis",
            "premium", 79.00, "active",
            "2024-02-10", "2024-02-10 00:00:00"
        ),
        (
            "CUST_006", "frank@example.com", "Frank Miller",
            "basic", 29.00, "active",
            "2024-03-01", "2024-03-01 00:00:00"
        ),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO customers
        (customer_id, email, full_name, plan, plan_price,
         status, signup_date, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, customers)

    conn.commit()
    conn.close()
    print(f"Seeded {len(customers)} customers")

def seed_purchases():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    purchases = [
        (
            "PUR_001", "CUST_001", "Annual Report Add-on",
            49.99, "2024-02-15", "2024-02-15 10:00:00"
        ),
        (
            "PUR_002", "CUST_002", "API Access Pack",
            99.99, "2024-02-20", "2024-02-20 14:00:00"
        ),
        (
            "PUR_003", "CUST_001", "Data Export Pack",
            29.99, "2024-05-10", "2024-05-10 09:00:00"
        ),
        (
            "PUR_004", "CUST_004", "Premium Feature Pack",
            59.99, "2024-04-15", "2024-04-15 11:00:00"
        ),
        (
            "PUR_005", "CUST_003", "Enterprise Support",
            199.99, "2024-03-01", "2024-03-01 16:00:00"
        ),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO purchases
        (purchase_id, customer_id, product_name,
         amount, purchase_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, purchases)

    conn.commit()
    conn.close()
    print(f"Seeded {len(purchases)} purchases")

if __name__ == "__main__":
    seed_customers()
    seed_purchases()
