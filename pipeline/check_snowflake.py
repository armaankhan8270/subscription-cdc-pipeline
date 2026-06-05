import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()
conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    role=os.getenv("SNOWFLAKE_ROLE"),
    login_timeout=10
)
cursor = conn.cursor()

cursor.execute("USE DATABASE SUBSTRACK_DB")

print("=== RAW TABLES (append-only, may have duplicates) ===")
for tbl in ["RAW.CUSTOMERS", "RAW.PURCHASES"]:
    cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
    print(f"  {tbl}: {cursor.fetchone()[0]} rows")

print("\n=== STAGING TABLES (current state, 1 row per customer) ===")
cursor.execute("SELECT customer_id, full_name, plan, plan_price, status FROM STAGING.CUSTOMERS ORDER BY customer_id")
for row in cursor.fetchall():
    print(f"  {row[0]} | {row[1]:15s} | plan={row[2]:10s} | ${row[3]:>6} | {row[4]}")

cursor.execute("SELECT COUNT(*) FROM STAGING.PURCHASES")
print(f"\n  STAGING.PURCHASES: {cursor.fetchone()[0]} rows")

cursor.close()
conn.close()
