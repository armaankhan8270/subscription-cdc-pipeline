import sqlite3
import pandas as pd
import json
import os
from datetime import datetime

DB_PATH = "source/substrack.db"
WATERMARK_PATH = "pipeline/watermark.json"
OUTPUT_PATH = "pipeline/output/"

os.makedirs(OUTPUT_PATH, exist_ok=True)

def load_watermark():
    with open(WATERMARK_PATH, "r") as f:
        return json.load(f)

def save_watermark(watermark):
    with open(WATERMARK_PATH, "w") as f:
        json.dump(watermark, f, indent=2)

def extract_customer_changes(last_processed):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            customer_id,
            email,
            full_name,
            plan,
            plan_price,
            status,
            signup_date,
            updated_at,
            'UPSERT' as _change_type
        FROM customers
        WHERE updated_at > ?
        ORDER BY updated_at ASC
    """
    df = pd.read_sql_query(query, conn, params=(last_processed,))
    conn.close()
    print(f"Found {len(df)} customer changes since {last_processed}")
    return df

def extract_purchase_changes(last_processed):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            purchase_id,
            customer_id,
            product_name,
            amount,
            purchase_date,
            created_at,
            'INSERT' as _change_type
        FROM purchases
        WHERE created_at > ?
        ORDER BY created_at ASC
    """
    df = pd.read_sql_query(query, conn, params=(last_processed,))
    conn.close()
    print(f"Found {len(df)} new purchases since {last_processed}")
    return df

def write_to_csv(df, table_name):
    if df.empty:
        print(f"No changes for {table_name} — skipping")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{OUTPUT_PATH}{table_name}_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"Written to {filename}")
    return filename

def run_extraction():
    watermark = load_watermark()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    customers_df = extract_customer_changes(watermark["customers"])
    purchases_df = extract_purchase_changes(watermark["purchases"])

    customers_file = write_to_csv(customers_df, "customers")
    purchases_file = write_to_csv(purchases_df, "purchases")

    if not customers_df.empty:
        watermark["customers"] = current_time
    if not purchases_df.empty:
        watermark["purchases"] = current_time
    save_watermark(watermark)

    return customers_file, purchases_file

if __name__ == "__main__":
    run_extraction()
