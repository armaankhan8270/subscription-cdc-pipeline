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

# DON'T read from stream - it consumes it

cursor.execute("EXECUTE TASK RAW.PROCESS_PURCHASES_TASK")
print("Task executed")

cursor.execute("SELECT COUNT(*) FROM STAGING.PURCHASES")
print(f"STAGING.PURCHASES: {cursor.fetchone()[0]}")

cursor.execute("SELECT * FROM STAGING.PURCHASES")
for r in cursor.fetchall():
    print(f"  {r}")

cursor.close()
conn.close()
