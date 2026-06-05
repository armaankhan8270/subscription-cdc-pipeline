import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "substrack.db")

def seed_customers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    customers = [
        ("CUST_001", "alice@example.com", "Alice Johnson", "basic", 29.00, "active", "2024-01-01", "2024-01-01 00:00:00"),
        ("CUST_002", "bob@example.com", "Bob Smith", "premium", 79.00, "active", "2024-01-15", "2024-01-15 00:00:00"),
        ("CUST_003", "carol@example.com", "Carol White", "enterprise", 299.00, "active", "2024-02-01", "2024-02-01 00:00:00"),
        ("CUST_004", "dave@example.com", "Dave Brown", "free", 0.00, "active", "2024-01-20", "2024-01-20 00:00:00"),
        ("CUST_005", "eve@example.com", "Eve Davis", "premium", 79.00, "active", "2024-02-10", "2024-02-10 00:00:00"),
        ("CUST_006", "frank@example.com", "Frank Miller", "basic", 29.00, "active", "2024-03-01", "2024-03-01 00:00:00"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO customers
        (customer_id, email, full_name, plan, plan_price, status, signup_date, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, customers)
    conn.commit()
    conn.close()
    print(f"Seeded {len(customers)} customers")

def seed_purchases():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    purchases = [
        ("PUR_001", "CUST_001", "Annual Report Add-on", 49.99, "2024-02-15", "2024-02-15 10:00:00"),
        ("PUR_002", "CUST_002", "API Access Pack", 99.99, "2024-02-20", "2024-02-20 14:00:00"),
        ("PUR_003", "CUST_001", "Data Export Pack", 29.99, "2024-05-10", "2024-05-10 09:00:00"),
        ("PUR_004", "CUST_004", "Premium Feature Pack", 59.99, "2024-04-15", "2024-04-15 11:00:00"),
        ("PUR_005", "CUST_003", "Enterprise Support", 199.99, "2024-03-01", "2024-03-01 16:00:00"),
        ("PUR_006", "CUST_005", "Team License", 149.99, "2024-03-15", "2024-03-15 08:00:00"),
        ("PUR_007", "CUST_006", "Storage Add-on", 19.99, "2024-04-01", "2024-04-01 12:00:00"),
        ("PUR_008", "CUST_002", "Audit Log Export", 39.99, "2024-05-20", "2024-05-20 15:00:00"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO purchases
        (purchase_id, customer_id, product_name, amount, purchase_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, purchases)
    conn.commit()
    conn.close()
    print(f"Seeded {len(purchases)} purchases")

def seed_subscriptions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    subscriptions = [
        ("SUB_001", "CUST_001", "basic", 29.00, "active", "2024-01-01", None, "2024-01-01 00:00:00", "2024-01-01 00:00:00"),
        ("SUB_002", "CUST_002", "premium", 79.00, "active", "2024-01-15", None, "2024-01-15 00:00:00", "2024-01-15 00:00:00"),
        ("SUB_003", "CUST_003", "enterprise", 299.00, "cancelled", "2024-02-01", "2026-06-01", "2024-02-01 00:00:00", "2026-06-01 12:00:00"),
        ("SUB_004", "CUST_004", "free", 0.00, "active", "2024-01-20", None, "2024-01-20 00:00:00", "2024-01-20 00:00:00"),
        ("SUB_005", "CUST_005", "premium", 79.00, "active", "2024-02-10", None, "2024-02-10 00:00:00", "2024-02-10 00:00:00"),
        ("SUB_006", "CUST_006", "basic", 29.00, "active", "2024-03-01", None, "2024-03-01 00:00:00", "2024-03-01 00:00:00"),
        ("SUB_007", "CUST_001", "premium", 79.00, "active", "2026-06-05", None, "2026-06-05 14:00:00", "2026-06-05 14:00:00"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO subscriptions
        (subscription_id, customer_id, plan_type, plan_price, status, start_date, end_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, subscriptions)
    conn.commit()
    conn.close()
    print(f"Seeded {len(subscriptions)} subscriptions")

def seed_billing_invoices():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    invoices = [
        ("INV_001", "CUST_001", "SUB_001", 29.00, "USD", "paid", "2024-02-01", "2024-02-01 05:00:00", "2024-02-01 00:00:00", "2024-02-01 05:00:00"),
        ("INV_002", "CUST_001", "SUB_001", 29.00, "USD", "paid", "2024-03-01", "2024-03-01 06:00:00", "2024-03-01 00:00:00", "2024-03-01 06:00:00"),
        ("INV_003", "CUST_001", "SUB_001", 29.00, "USD", "paid", "2024-04-01", "2024-04-01 04:00:00", "2024-04-01 00:00:00", "2024-04-01 04:00:00"),
        ("INV_004", "CUST_001", "SUB_001", 29.00, "USD", "paid", "2024-05-01", "2024-05-01 05:30:00", "2024-05-01 00:00:00", "2024-05-01 05:30:00"),
        ("INV_005", "CUST_002", "SUB_002", 79.00, "USD", "paid", "2024-02-15", "2024-02-15 08:00:00", "2024-02-15 00:00:00", "2024-02-15 08:00:00"),
        ("INV_006", "CUST_002", "SUB_002", 79.00, "USD", "paid", "2024-03-15", "2024-03-15 09:00:00", "2024-03-15 00:00:00", "2024-03-15 09:00:00"),
        ("INV_007", "CUST_002", "SUB_002", 79.00, "USD", "paid", "2024-04-15", "2024-04-15 07:00:00", "2024-04-15 00:00:00", "2024-04-15 07:00:00"),
        ("INV_008", "CUST_003", "SUB_003", 299.00, "USD", "paid", "2024-03-01", "2024-03-01 10:00:00", "2024-03-01 00:00:00", "2024-03-01 10:00:00"),
        ("INV_009", "CUST_003", "SUB_003", 299.00, "USD", "paid", "2024-04-01", "2024-04-01 10:00:00", "2024-04-01 00:00:00", "2024-04-01 10:00:00"),
        ("INV_010", "CUST_003", "SUB_003", 299.00, "USD", "paid", "2024-05-01", "2024-05-01 09:00:00", "2024-05-01 00:00:00", "2024-05-01 09:00:00"),
        ("INV_011", "CUST_003", "SUB_003", 299.00, "USD", "overdue", "2024-06-01", None, "2024-06-01 00:00:00", "2024-06-01 00:00:00"),
        ("INV_012", "CUST_005", "SUB_005", 79.00, "USD", "paid", "2024-03-10", "2024-03-10 06:00:00", "2024-03-10 00:00:00", "2024-03-10 06:00:00"),
        ("INV_013", "CUST_005", "SUB_005", 79.00, "USD", "paid", "2024-04-10", "2024-04-10 05:00:00", "2024-04-10 00:00:00", "2024-04-10 05:00:00"),
        ("INV_014", "CUST_005", "SUB_005", 79.00, "USD", "pending", "2024-05-10", None, "2024-05-10 00:00:00", "2024-05-10 00:00:00"),
        ("INV_015", "CUST_006", "SUB_006", 29.00, "USD", "paid", "2024-04-01", "2024-04-01 08:00:00", "2024-04-01 00:00:00", "2024-04-01 08:00:00"),
        ("INV_016", "CUST_006", "SUB_006", 29.00, "USD", "paid", "2024-05-01", "2024-05-01 07:30:00", "2024-05-01 00:00:00", "2024-05-01 07:30:00"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO billing_invoices
        (invoice_id, customer_id, subscription_id, amount, currency, status, due_date, paid_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, invoices)
    conn.commit()
    conn.close()
    print(f"Seeded {len(invoices)} billing invoices")

def seed_payment_methods():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    methods = [
        ("PM_001", "CUST_001", "credit_card", "visa", "4242", 12, 2026, 1, "2024-01-01 00:00:00", "2024-01-01 00:00:00"),
        ("PM_002", "CUST_002", "credit_card", "mastercard", "1234", 8, 2025, 1, "2024-01-15 00:00:00", "2024-01-15 00:00:00"),
        ("PM_003", "CUST_003", "bank_transfer", "ach", "6789", 0, 0, 1, "2024-02-01 00:00:00", "2024-02-01 00:00:00"),
        ("PM_004", "CUST_004", "paypal", "paypal", "9876", 0, 0, 1, "2024-01-20 00:00:00", "2024-01-20 00:00:00"),
        ("PM_005", "CUST_005", "credit_card", "amex", "5555", 3, 2027, 1, "2024-02-10 00:00:00", "2024-02-10 00:00:00"),
        ("PM_006", "CUST_006", "credit_card", "visa", "7777", 9, 2025, 0, "2024-03-01 00:00:00", "2024-03-01 00:00:00"),
        ("PM_007", "CUST_006", "credit_card", "mastercard", "8888", 11, 2026, 1, "2024-04-01 00:00:00", "2024-04-01 00:00:00"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO payment_methods
        (payment_method_id, customer_id, type, provider, last_four, exp_month, exp_year, is_default, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, methods)
    conn.commit()
    conn.close()
    print(f"Seeded {len(methods)} payment methods")

def seed_usage_events():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    events = [
        ("EVT_001", "CUST_001", "api_call", 250, "2024-06-01 10:00:00", "2024-06-01 10:00:00"),
        ("EVT_002", "CUST_001", "storage_gb", 15.5, "2024-06-01 12:00:00", "2024-06-01 12:00:00"),
        ("EVT_003", "CUST_001", "bandwidth_gb", 45.2, "2024-06-01 14:00:00", "2024-06-01 14:00:00"),
        ("EVT_004", "CUST_001", "users_count", 8, "2024-06-01 16:00:00", "2024-06-01 16:00:00"),
        ("EVT_005", "CUST_002", "api_call", 520, "2024-06-01 10:30:00", "2024-06-01 10:30:00"),
        ("EVT_006", "CUST_002", "storage_gb", 42.8, "2024-06-01 11:00:00", "2024-06-01 11:00:00"),
        ("EVT_007", "CUST_002", "bandwidth_gb", 128.3, "2024-06-01 13:00:00", "2024-06-01 13:00:00"),
        ("EVT_008", "CUST_002", "users_count", 25, "2024-06-01 15:00:00", "2024-06-01 15:00:00"),
        ("EVT_009", "CUST_003", "api_call", 80, "2024-06-01 09:00:00", "2024-06-01 09:00:00"),
        ("EVT_010", "CUST_003", "bandwidth_gb", 15.0, "2024-06-01 11:00:00", "2024-06-01 11:00:00"),
        ("EVT_011", "CUST_004", "api_call", 15, "2024-06-01 08:00:00", "2024-06-01 08:00:00"),
        ("EVT_012", "CUST_004", "storage_gb", 2.3, "2024-06-01 09:00:00", "2024-06-01 09:00:00"),
        ("EVT_013", "CUST_005", "api_call", 680, "2024-06-01 10:00:00", "2024-06-01 10:00:00"),
        ("EVT_014", "CUST_005", "storage_gb", 85.1, "2024-06-01 11:00:00", "2024-06-01 11:00:00"),
        ("EVT_015", "CUST_005", "bandwidth_gb", 210.6, "2024-06-01 12:00:00", "2024-06-01 12:00:00"),
        ("EVT_016", "CUST_005", "users_count", 40, "2024-06-01 13:00:00", "2024-06-01 13:00:00"),
        ("EVT_017", "CUST_006", "api_call", 95, "2024-06-01 14:00:00", "2024-06-01 14:00:00"),
        ("EVT_018", "CUST_006", "storage_gb", 8.7, "2024-06-01 15:00:00", "2024-06-01 15:00:00"),
        ("EVT_019", "CUST_001", "api_call", 310, "2024-06-02 10:00:00", "2024-06-02 10:00:00"),
        ("EVT_020", "CUST_005", "api_call", 720, "2024-06-02 11:00:00", "2024-06-02 11:00:00"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO usage_events
        (event_id, customer_id, event_type, quantity, recorded_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, events)
    conn.commit()
    conn.close()
    print(f"Seeded {len(events)} usage events")

def seed_support_tickets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tickets = [
        ("TKT_001", "CUST_001", "Cannot access dashboard", "Getting 403 error on login", "high", "resolved", "2024-03-05 09:00:00", "2024-03-05 14:00:00"),
        ("TKT_002", "CUST_001", "Billing question about upgrade", "How will upgrading affect my existing invoices?", "medium", "closed", "2024-06-05 10:00:00", "2024-06-05 12:00:00"),
        ("TKT_003", "CUST_002", "API rate limiting too strict", "We are hitting limits at 500 requests/day. Need increase.", "high", "in_progress", "2024-05-20 11:00:00", "2024-05-20 11:00:00"),
        ("TKT_004", "CUST_003", "Cancel account request", "Please process account cancellation as discussed", "medium", "resolved", "2024-05-25 15:00:00", "2024-06-01 10:00:00"),
        ("TKT_005", "CUST_004", "How to upgrade from free tier?", "I want to upgrade but need to understand pricing first", "low", "open", "2024-06-03 08:00:00", "2024-06-03 08:00:00"),
        ("TKT_006", "CUST_005", "Data export taking too long", "Export of 5GB dataset has been running for 6 hours", "critical", "in_progress", "2024-06-02 16:00:00", "2024-06-02 16:00:00"),
        ("TKT_007", "CUST_006", "Need help with SSO setup", "SAML configuration not working with our IdP", "medium", "open", "2024-06-04 09:30:00", "2024-06-04 09:30:00"),
        ("TKT_008", "CUST_002", "Invoice history missing months", "March and April invoices not showing in billing portal", "high", "resolved", "2024-05-15 13:00:00", "2024-05-16 09:00:00"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO support_tickets
        (ticket_id, customer_id, subject, description, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, tickets)
    conn.commit()
    conn.close()
    print(f"Seeded {len(tickets)} support tickets")

if __name__ == "__main__":
    seed_customers()
    seed_purchases()
    seed_subscriptions()
    seed_billing_invoices()
    seed_payment_methods()
    seed_usage_events()
    seed_support_tickets()
