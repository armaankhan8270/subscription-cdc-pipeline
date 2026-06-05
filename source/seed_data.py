import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "substrack.db")
random.seed(42)

CUSTOMER_COUNT = 1000

PLANS = [
    {"name": "free", "price": 0.00, "weight": 20},
    {"name": "basic", "price": 29.00, "weight": 35},
    {"name": "premium", "price": 79.00, "weight": 30},
    {"name": "enterprise", "price": 299.00, "weight": 15},
]

FIRST_NAMES = [
    "Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Hank", "Iris", "Jack",
    "Kate", "Leo", "Mia", "Noah", "Olivia", "Peter", "Quinn", "Rose", "Sam", "Tina",
    "Uma", "Victor", "Wendy", "Xander", "Yara", "Zane", "Aria", "Ben", "Clara", "Dan",
    "Elsa", "Finn", "Gina", "Hugo", "Ivy", "Jake", "Kara", "Liam", "Maya", "Nick",
    "Owen", "Paula", "Rex", "Sage", "Troy", "Vera", "Will", "Xena", "Yuki", "Zara",
    "Adam", "Belle", "Cruz", "Dora", "Elio", "Faye", "Glen", "Hope", "Ivan", "Jade",
    "Kurt", "Luna", "Milo", "Nina", "Otis", "Pearl", "Rico", "Suki", "Todd", "Ursa",
    "Vince", "Wade", "Xola", "Yves", "Zion", "Amy", "Blake", "Cora", "Drew", "Elle",
    "Fox", "Gail", "Hash", "Isla", "Joel", "Kai", "Lex", "Mack", "Nash", "Oona",
    "Pace", "Rhea", "Shay", "Tess", "Ugo", "Vann", "Wyck", "Xyla", "Yard", "Zuri",
]

LAST_NAMES = [
    "Johnson", "Smith", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson",
    "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster",
]

PRODUCTS = [
    ("Annual Report Add-on", 49.99),
    ("API Access Pack", 99.99),
    ("Data Export Pack", 29.99),
    ("Premium Feature Pack", 59.99),
    ("Enterprise Support", 199.99),
    ("Team License", 149.99),
    ("Storage Add-on", 19.99),
    ("Audit Log Export", 39.99),
    ("SSO Integration", 79.99),
    ("Custom Dashboard", 89.99),
    ("Webhook Gateway", 34.99),
    ("Backup & Restore", 24.99),
    ("Analytics Pro", 129.99),
    ("API Gateway", 59.99),
    ("Compliance Pack", 199.99),
    ("Multi-region Deploy", 299.99),
    ("Load Testing", 44.99),
    ("Monitoring Suite", 69.99),
    ("Security Scan", 149.99),
    ("Training Credits", 99.99),
]

TICKET_SUBJECTS = [
    "Cannot access dashboard",
    "Billing question about upgrade",
    "API rate limiting too strict",
    "Cancel account request",
    "How to upgrade from free tier",
    "Data export taking too long",
    "Need help with SSO setup",
    "Invoice history missing months",
    "Login issues after password reset",
    "Feature request: bulk operations",
    "Performance degradation reported",
    "Unable to add team members",
    "Data synchronization error",
    "Integration with Slack failing",
    "Report generation timeout",
    "User permission misconfiguration",
    "API endpoint returning 500",
    "Dashboard chart data mismatch",
    "Email notifications not sending",
    "Trial extension request",
]

TICKET_DESCRIPTIONS = [
    "Getting {error_code} error when trying to access the main dashboard page.",
    "I would like to understand how upgrading my plan will affect existing invoices and billing cycle.",
    "We are hitting the rate limit at {limit} requests per day. Our team needs an increase for normal operations.",
    "Please process the account cancellation as discussed with our account manager.",
    "I want to upgrade but need to understand the pricing differences between plans first.",
    "The export of our {size} dataset has been running for {hours} hours without completing.",
    "The SAML configuration is not working correctly with our identity provider. Need assistance.",
    "Several months of invoice history ({months}) are not showing up in the billing portal.",
    "After resetting my password, I am unable to log in using the new credentials.",
    "We need the ability to perform bulk operations on our customer records and data exports.",
    "System performance has degraded significantly since the last deployment. Response times are up {pct}%.",
    "I am unable to add new team members to our organization account. The invite emails are not sending.",
    "Data synchronization between our systems and the platform is failing with timeout errors.",
    "The Slack integration has stopped working after the recent workspace update.",
    "Report generation for our monthly analytics is timing out after {hours} hours of processing.",
    "Several team members are reporting incorrect permission levels after the latest role update.",
    "The API endpoint for user management is returning 500 errors intermittently since yesterday.",
    "The dashboard charts are showing different numbers compared to our internal reporting system.",
    "Email notifications for invoice generation and payment confirmations have stopped working.",
    "We would like to request an extension of our trial period to evaluate enterprise features.",
]

EVENT_TYPES = [
    ("api_call", "count"),
    ("storage_gb", "storage"),
    ("bandwidth_gb", "bandwidth"),
    ("users_count", "users"),
    ("api_call", "count"),
    ("storage_gb", "storage"),
    ("api_call", "count"),
    ("bandwidth_gb", "bandwidth"),
    ("api_call", "count"),
    ("users_count", "users"),
]

def random_date(start, end):
    delta = end - start
    offset = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=offset)

def seed_customers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    customers = []
    signup_base = datetime(2023, 6, 1)
    cutoff = datetime(2026, 6, 5)
    for i in range(1, CUSTOMER_COUNT + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        domain = random.choice(["example.com", "test.org", "demo.net", "mail.com", "corp.io"])
        email = f"{first.lower()}.{last.lower()}{i}@{domain}"
        plan = random.choices(PLANS, weights=[p["weight"] for p in PLANS])[0]
        signup_date = random_date(signup_base, cutoff - timedelta(days=90))
        signup_str = signup_date.strftime("%Y-%m-%d")
        updated_str = signup_date.strftime("%Y-%m-%d %H:%M:%S")
        customers.append((
            f"CUST_{i:04d}", email, f"{first} {last}",
            plan["name"], plan["price"], "active",
            signup_str, updated_str,
        ))
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
    purchases = []
    pid = 1
    for cid in range(1, CUSTOMER_COUNT + 1):
        num_purchases = random.choices([0, 1, 2, 3, 4, 5], weights=[10, 30, 25, 18, 10, 7])[0]
        customer_signup = cursor.execute(
            "SELECT signup_date FROM customers WHERE customer_id = ?",
            (f"CUST_{cid:04d}",)
        ).fetchone()[0]
        signup = datetime.strptime(customer_signup, "%Y-%m-%d")
        for _ in range(num_purchases):
            product, price = random.choice(PRODUCTS)
            purch_date = random_date(signup, datetime(2026, 6, 1))
            created = purch_date + timedelta(hours=random.randint(0, 12))
            purchases.append((
                f"PUR_{pid:04d}", f"CUST_{cid:04d}", product, price,
                purch_date.strftime("%Y-%m-%d"),
                created.strftime("%Y-%m-%d %H:%M:%S"),
            ))
            pid += 1
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
    subs = []
    sid = 1
    for cid in range(1, CUSTOMER_COUNT + 1):
        row = cursor.execute(
            "SELECT plan, plan_price, signup_date FROM customers WHERE customer_id = ?",
            (f"CUST_{cid:04d}",)
        ).fetchone()
        initial_plan, initial_price, signup_str = row
        signup = datetime.strptime(signup_str, "%Y-%m-%d")
        now = datetime(2026, 6, 5)
        subs.append((
            f"SUB_{sid:04d}", f"CUST_{cid:04d}",
            initial_plan, initial_price, "active",
            signup_str, None,
            signup_str + " 00:00:00", signup_str + " 00:00:00",
        ))
        sid += 1
        if random.random() < 0.08:
            new_plan = random.choice([p for p in PLANS if p["name"] != initial_plan])
            change_date = random_date(signup + timedelta(days=60), now - timedelta(days=30))
            subs.append((
                f"SUB_{sid:04d}", f"CUST_{cid:04d}",
                new_plan["name"], new_plan["price"], "active",
                change_date.strftime("%Y-%m-%d"), None,
                change_date.strftime("%Y-%m-%d %H:%M:%S"),
                change_date.strftime("%Y-%m-%d %H:%M:%S"),
            ))
            sid += 1
            cursor.execute("""
                UPDATE customers
                SET plan = ?, plan_price = ?, updated_at = ?
                WHERE customer_id = ?
            """, (new_plan["name"], new_plan["price"],
                  change_date.strftime("%Y-%m-%d %H:%M:%S"), f"CUST_{cid:04d}"))
        if random.random() < 0.03:
            cancel_date = random_date(signup + timedelta(days=30), now)
            cursor.execute("""
                UPDATE subscriptions
                SET status = 'cancelled', end_date = ?, updated_at = ?
                WHERE customer_id = ? AND status = 'active'
            """, (cancel_date.strftime("%Y-%m-%d"),
                  cancel_date.strftime("%Y-%m-%d %H:%M:%S"), f"CUST_{cid:04d}"))
            cursor.execute("""
                UPDATE customers SET status = 'cancelled', updated_at = ? WHERE customer_id = ?
            """, (cancel_date.strftime("%Y-%m-%d %H:%M:%S"), f"CUST_{cid:04d}"))
    cursor.executemany("""
        INSERT OR IGNORE INTO subscriptions
        (subscription_id, customer_id, plan_type, plan_price, status, start_date, end_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, subs)
    conn.commit()
    conn.close()
    print(f"Seeded {len(subs)} subscriptions")

def seed_billing_invoices():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    invoices = []
    iid = 1
    now = datetime(2026, 6, 5)
    for cid in range(1, CUSTOMER_COUNT + 1):
        row = cursor.execute(
            "SELECT plan_price, signup_date FROM customers WHERE customer_id = ?",
            (f"CUST_{cid:04d}",)
        ).fetchone()
        price, signup_str = row
        signup = datetime.strptime(signup_str, "%Y-%m-%d")
        months_active = max(1, (now.year - signup.year) * 12 + (now.month - signup.month))
        num_invoices = min(months_active, random.randint(2, 12))
        for m in range(num_invoices):
            due = signup + timedelta(days=30 * (m + 1) - random.randint(0, 5))
            if due > now:
                break
            paid = due + timedelta(days=random.randint(0, 7)) if random.random() < 0.85 else None
            status = "paid" if paid else random.choices(["pending", "overdue"], weights=[60, 40])[0]
            invoices.append((
                f"INV_{iid:05d}", f"CUST_{cid:04d}", price, "USD", status,
                due.strftime("%Y-%m-%d"),
                paid.strftime("%Y-%m-%d %H:%M:%S") if paid else None,
                due.strftime("%Y-%m-%d %H:%M:%S"),
                (paid or due).strftime("%Y-%m-%d %H:%M:%S"),
            ))
            iid += 1
    chunk_size = 500
    for i in range(0, len(invoices), chunk_size):
        chunk = invoices[i:i+chunk_size]
        cursor.executemany("""
            INSERT OR IGNORE INTO billing_invoices
            (invoice_id, customer_id, amount, currency, status, due_date, paid_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, chunk)
    conn.commit()
    conn.close()
    print(f"Seeded {len(invoices)} billing invoices")

def seed_payment_methods():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    methods = []
    mid = 1
    for cid in range(1, CUSTOMER_COUNT + 1):
        ptype = random.choices(["credit_card", "paypal", "bank_transfer"], weights=[65, 25, 10])[0]
        providers = {
            "credit_card": random.choice(["visa", "mastercard", "amex"]),
            "paypal": "paypal",
            "bank_transfer": "ach",
        }
        provider = providers[ptype]
        last_four = str(random.randint(1000, 9999))
        exp_month = random.randint(1, 12)
        exp_year = random.randint(2025, 2029)
        signup = cursor.execute(
            "SELECT signup_date FROM customers WHERE customer_id = ?",
            (f"CUST_{cid:04d}",)
        ).fetchone()[0]
        methods.append((
            f"PM_{mid:04d}", f"CUST_{cid:04d}",
            ptype, provider, last_four, exp_month, exp_year, 1,
            signup + " 00:00:00", signup + " 00:00:00",
        ))
        mid += 1
        if random.random() < 0.06:
            new_ptype = random.choice(["credit_card", "paypal"])
            new_provider = {
                "credit_card": random.choice(["visa", "mastercard"]),
                "paypal": "paypal",
            }[new_ptype]
            new_four = str(random.randint(1000, 9999))
            methods.append((
                f"PM_{mid:04d}", f"CUST_{cid:04d}",
                new_ptype, new_provider, new_four, random.randint(1, 12),
                random.randint(2026, 2030), 0,
                signup + " 00:00:00", signup + " 00:00:00",
            ))
            mid += 1
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
    events = []
    eid = 1
    now = datetime(2026, 6, 5)
    for cid in range(1, CUSTOMER_COUNT + 1):
        num_events = random.choices([0, 1, 2, 3, 4, 5], weights=[5, 25, 30, 22, 12, 6])[0]
        signup = cursor.execute(
            "SELECT signup_date FROM customers WHERE customer_id = ?",
            (f"CUST_{cid:04d}",)
        ).fetchone()[0]
        signup_dt = datetime.strptime(signup, "%Y-%m-%d")
        for _ in range(num_events):
            event_type, category = random.choice(EVENT_TYPES)
            base_quantities = {
                "api_call": random.randint(10, 2000),
                "storage_gb": round(random.uniform(0.5, 500.0), 1),
                "bandwidth_gb": round(random.uniform(1.0, 1000.0), 1),
                "users_count": random.randint(1, 200),
            }
            quantity = base_quantities[event_type]
            recorded = random_date(signup_dt, now)
            events.append((
                f"EVT_{eid:05d}", f"CUST_{cid:04d}",
                event_type, quantity,
                recorded.strftime("%Y-%m-%d %H:%M:%S"),
                recorded.strftime("%Y-%m-%d %H:%M:%S"),
            ))
            eid += 1
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
    tickets = []
    tid = 1
    now = datetime(2026, 6, 5)
    for cid in range(1, CUSTOMER_COUNT + 1):
        num_tickets = random.choices([0, 1, 2, 3], weights=[30, 40, 20, 10])[0]
        signup = cursor.execute(
            "SELECT signup_date FROM customers WHERE customer_id = ?",
            (f"CUST_{cid:04d}",)
        ).fetchone()[0]
        signup_dt = datetime.strptime(signup, "%Y-%m-%d")
        for _ in range(num_tickets):
            subject = random.choice(TICKET_SUBJECTS)
            desc_template = random.choice(TICKET_DESCRIPTIONS)
            description = desc_template.format(
                error_code=random.choice([403, 404, 500, 502, 503]),
                limit=random.choice([100, 500, 1000, 5000]),
                size=f"{random.randint(1, 50)}GB",
                hours=random.randint(2, 48),
                months=f"{random.choice(['January', 'February', 'March', 'April'])} and {random.choice(['May', 'June'])}",
                pct=random.randint(20, 80),
            )
            priority = random.choices(["low", "medium", "high", "critical"], weights=[15, 40, 35, 10])[0]
            status = random.choices(["open", "in_progress", "resolved", "closed"], weights=[15, 20, 40, 25])[0]
            created = random_date(signup_dt, now - timedelta(days=1))
            updated = created + timedelta(hours=random.randint(1, 168))
            tickets.append((
                f"TKT_{tid:04d}", f"CUST_{cid:04d}",
                subject, description, priority, status,
                created.strftime("%Y-%m-%d %H:%M:%S"),
                updated.strftime("%Y-%m-%d %H:%M:%S"),
            ))
            tid += 1
    cursor.executemany("""
        INSERT OR IGNORE INTO support_tickets
        (ticket_id, customer_id, subject, description, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, tickets)
    conn.commit()
    conn.close()
    print(f"Seeded {len(tickets)} support tickets")

if __name__ == "__main__":
    print("Seeding 1000+ customers with full SaaS data...")
    seed_customers()
    seed_purchases()
    seed_subscriptions()
    seed_billing_invoices()
    seed_payment_methods()
    seed_usage_events()
    seed_support_tickets()
    print("Done!")
