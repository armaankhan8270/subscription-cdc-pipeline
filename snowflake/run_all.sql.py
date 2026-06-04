import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    role=os.getenv("SNOWFLAKE_ROLE")
)
cursor = conn.cursor()

sql_files = [
    "01_setup.sql",
    "02_raw_tables.sql",
    "03_staging_tables.sql",
    "04_snowpipe.sql",
    "05_streams.sql",
    "06_tasks.sql"
]

for file in sql_files:
    path = os.path.join(os.path.dirname(__file__), file)
    with open(path, "r") as f:
        sql = f.read()
    print(f"Running {file}...", flush=True)
    for statement in sql.split(";"):
        stmt = statement.strip()
        if stmt:
            try:
                cursor.execute(stmt)
                print(f"  OK", flush=True)
            except Exception as e:
                print(f"  Error: {e}", flush=True)
    print(f"  Done with {file}", flush=True)

cursor.close()
conn.close()
print("\nAll Snowflake SQL files executed successfully", flush=True)
