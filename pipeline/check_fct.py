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

print("=== FCT PURCHASES ===")
cursor.execute("SELECT * FROM MARTS.FCT_PURCHASES ORDER BY purchase_date")
rows = cursor.fetchall()
print(f"  Total rows: {len(rows)}")
col_names = [d[0] for d in cursor.description]
print(f"  Columns: {col_names}")
for row in rows:
    print(f"  {row}")

print()
print("=== DIM CUSTOMER ===")
cursor.execute("SELECT customer_id, plan, valid_from, valid_to, is_current FROM MARTS.DIM_CUSTOMER ORDER BY customer_id, valid_from")
for row in cursor.fetchall():
    vto = str(row[3])[:10] if row[3] else "NOW"
    print(f"  {row[0]} | plan={row[1]:10s} | from={str(row[2])[:10]} | to={vto} | current={row[4]}")

cursor.close()
conn.close()
