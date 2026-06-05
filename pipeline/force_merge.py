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

# Check if stream has data WITHOUT consuming it
cursor.execute("SELECT SYSTEM$STREAM_HAS_DATA('SUBSTRACK_DB.RAW.CUSTOMERS_STREAM')")
has_data = cursor.fetchone()[0]
print(f"Stream has data: {has_data}")

if has_data:
    cursor.execute("EXECUTE TASK RAW.PROCESS_CUSTOMERS_TASK")
    print("Task executed")

cursor.execute("SELECT customer_id, plan, status, updated_at FROM STAGING.CUSTOMERS ORDER BY customer_id")
print("\nSTAGING after:")
for r in cursor.fetchall():
    print(f"  {r[0]} | {r[1]:10s} | {str(r[2]):10s} | updated={str(r[3])[:19]}")

cursor.close()
conn.close()
