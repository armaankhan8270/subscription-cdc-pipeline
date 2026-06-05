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

print("=== STAGING CUSTOMERS ===")
cursor.execute("SELECT customer_id, full_name, plan, status, updated_at FROM STAGING.CUSTOMERS ORDER BY customer_id")
for row in cursor.fetchall():
    print(f"  {row[0]} | {row[1]:15s} | {row[2]:10s} | {row[3]:10s} | updated={str(row[4])[:19]}")

cursor.close()
conn.close()
