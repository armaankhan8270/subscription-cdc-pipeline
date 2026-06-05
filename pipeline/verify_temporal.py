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

print("=== THE KEY QUESTION: What plan was each customer on when they purchased?")
print()
cursor.execute("""
    SELECT f.purchase_id, f.customer_name, f.purchase_date,
           f.product_name, f.amount,
           f.plan_at_purchase AS plan_when_bought,
           c.plan AS current_plan
    FROM MARTS.FCT_PURCHASES f
    JOIN MARTS.DIM_CUSTOMER c
      ON f.customer_id = c.customer_id AND c.is_current = TRUE
    ORDER BY f.purchase_date
""")
for row in cursor.fetchall():
    same = "SAME" if row[5] == row[6] else "DIFFERENT"
    print(f"  {row[0]} | {row[1]:15s} | {str(row[2])[:10]} | {row[3]:25s} | ${row[4]:>5}")
    print(f"           Plan when bought: {row[5]:10s} | Current plan: {row[6]:10s} | {same}")
    print()

cursor.close()
conn.close()
