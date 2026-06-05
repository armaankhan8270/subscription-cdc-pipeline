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

print("=== SNAPSHOT (versions per customer) ===")
cursor.execute("""
    SELECT customer_id, plan, dbt_valid_from, dbt_valid_to
    FROM SNAPSHOTS.DIM_CUSTOMER_SNAPSHOT
    ORDER BY customer_id, dbt_valid_from
""")
for row in cursor.fetchall():
    print(f"  {row[0]} | plan={row[1]:10s} | from={str(row[2])[:19]} | to={row[3]}")

print("\n=== DIM CUSTOMER (enriched) ===")
cursor.execute("""
    SELECT customer_id, full_name, plan, plan_tier, is_current, valid_from, valid_to
    FROM MARTS.DIM_CUSTOMER
    ORDER BY customer_id
""")
for row in cursor.fetchall():
    print(f"  {row[0]} | {row[1]:15s} | plan={row[2]:10s} | tier={row[3]:10s} | current={row[4]} | from={str(row[5])[:19]}")

print("\n=== FCT PURCHASES (customer_sk check) ===")
cursor.execute("""
    SELECT purchase_id, customer_name, purchase_date, plan_at_purchase, customer_sk
    FROM MARTS.FCT_PURCHASES
    ORDER BY purchase_date
""")
for row in cursor.fetchall():
    print(f"  {row[0]} | {str(row[1]):15s} | {str(row[2])[:10]} | plan={str(row[3]):10s} | sk={row[4]}")

cursor.close()
conn.close()
