import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "source", "substrack.db")
WATERMARK_PATH = "pipeline/watermark.json"
OUTPUT_PATH = "pipeline/output/"

TABLE_CONFIGS = {
    "customers": {
        "cursor_field": "updated_at",
        "change_type": "UPSERT",
        "columns": "customer_id, email, full_name, plan, plan_price, status, signup_date, updated_at, 'UPSERT' as _change_type",
        "order_by": "updated_at ASC",
    },
    "purchases": {
        "cursor_field": "created_at",
        "change_type": "INSERT",
        "columns": "purchase_id, customer_id, product_name, amount, purchase_date, created_at, 'INSERT' as _change_type",
        "order_by": "created_at ASC",
    },
    "subscriptions": {
        "cursor_field": "updated_at",
        "change_type": "UPSERT",
        "columns": "subscription_id, customer_id, plan_type, plan_price, status, start_date, end_date, created_at, updated_at, 'UPSERT' as _change_type",
        "order_by": "updated_at ASC",
    },
    "billing_invoices": {
        "cursor_field": "updated_at",
        "change_type": "UPSERT",
        "columns": "invoice_id, customer_id, amount, currency, status, due_date, paid_at, created_at, updated_at, 'UPSERT' as _change_type",
        "order_by": "updated_at ASC",
    },
    "payment_methods": {
        "cursor_field": "updated_at",
        "change_type": "UPSERT",
        "columns": "payment_method_id, customer_id, type, provider, last_four, exp_month, exp_year, is_default, created_at, updated_at, 'UPSERT' as _change_type",
        "order_by": "updated_at ASC",
    },
    "usage_events": {
        "cursor_field": "created_at",
        "change_type": "INSERT",
        "columns": "event_id, customer_id, event_type, quantity, recorded_at, created_at, 'INSERT' as _change_type",
        "order_by": "created_at ASC",
    },
    "support_tickets": {
        "cursor_field": "updated_at",
        "change_type": "UPSERT",
        "columns": "ticket_id, customer_id, subject, description, priority, status, created_at, updated_at, 'UPSERT' as _change_type",
        "order_by": "updated_at ASC",
    },
}

os.makedirs(OUTPUT_PATH, exist_ok=True)

def load_watermark():
    with open(WATERMARK_PATH, "r") as f:
        return json.load(f)

def save_watermark(watermark):
    with open(WATERMARK_PATH, "w") as f:
        json.dump(watermark, f, indent=2)

def extract_changes(table_name, config, last_processed):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"""
        SELECT {config['columns']}
        FROM {table_name}
        WHERE {config['cursor_field']} > ?
        ORDER BY {config['order_by']}
    """
    cursor.execute(query, (last_processed,))
    rows = cursor.fetchall()
    col_names = [d[0] for d in cursor.description]
    conn.close()
    print(f"  {table_name}: {len(rows)} changes since {last_processed}")
    return rows, col_names

def write_to_csv(rows, col_names, table_name):
    if not rows:
        print(f"  {table_name}: no changes — skipping")
        return None

    import csv
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{OUTPUT_PATH}{table_name}_{timestamp}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        writer.writerows(rows)
    print(f"  {table_name}: written to {filename} ({len(rows)} rows)")
    return filename

def run_extraction():
    watermark = load_watermark()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_files = {}

    print(f"=== CDC Extraction started at {current_time} ===")
    for table_name, config in TABLE_CONFIGS.items():
        rows, col_names = extract_changes(table_name, config, watermark[table_name])
        fname = write_to_csv(rows, col_names, table_name)
        output_files[table_name] = fname
        if rows:
            watermark[table_name] = current_time

    save_watermark(watermark)
    print("=== CDC Extraction complete ===")
    return output_files

if __name__ == "__main__":
    run_extraction()
