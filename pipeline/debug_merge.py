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

# Run the full MERGE directly (doesn't use task, doesn't need stream)
# The stream data is consumed WITH the MERGE
print("=== Running MERGE directly ===")
merge_sql = """
MERGE INTO STAGING.CUSTOMERS AS target
USING (
    SELECT * FROM (
        SELECT
            customer_id, email, full_name, plan, plan_price,
            status, TRY_TO_DATE(signup_date) AS signup_date,
            TRY_TO_TIMESTAMP(updated_at) AS updated_at,
            _change_type,
            ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) AS rn
        FROM RAW.CUSTOMERS_STREAM
    ) WHERE rn = 1
) AS source
ON target.customer_id = source.customer_id
WHEN NOT MATCHED THEN INSERT (customer_id, email, full_name, plan, plan_price, status, signup_date, updated_at, _dw_updated_at)
VALUES (source.customer_id, source.email, source.full_name, source.plan, source.plan_price, source.status, source.signup_date, source.updated_at, CURRENT_TIMESTAMP())
WHEN MATCHED AND source._change_type = 'UPSERT' THEN UPDATE SET
    target.email = source.email, target.full_name = source.full_name,
    target.plan = source.plan, target.plan_price = source.plan_price,
    target.status = source.status, target.updated_at = source.updated_at,
    target._dw_updated_at = CURRENT_TIMESTAMP()
"""
cursor.execute(merge_sql)
print(f"Rows affected: {cursor.rowcount}")

cursor.execute("SELECT customer_id, plan, status, updated_at FROM STAGING.CUSTOMERS ORDER BY customer_id")
print("\nSTAGING after MERGE:")
for r in cursor.fetchall():
    print(f"  {r[0]} | {r[1]:10s} | {str(r[2]):10s} | updated={str(r[3])[:19]}")

cursor.close()
conn.close()
