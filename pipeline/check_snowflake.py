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

for tbl in ["RAW.CUSTOMERS", "RAW.PURCHASES"]:
    cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
    print(f"{tbl}: {cursor.fetchone()[0]} rows")

for tbl in ["STAGING.CUSTOMERS", "STAGING.PURCHASES"]:
    cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
    print(f"{tbl}: {cursor.fetchone()[0]} rows")

cursor.close()
conn.close()
