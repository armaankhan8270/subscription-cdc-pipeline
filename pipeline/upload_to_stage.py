import snowflake.connector
import os
import time
from dotenv import load_dotenv

load_dotenv()

TABLE_CONFIGS = [
    {"name": "customers", "stage_path": "@SUBSTRACK_DB.RAW.RAW_STAGE/customers/", "pipe_name": "SUBSTRACK_DB.RAW.CUSTOMERS_PIPE", "task_name": "SUBSTRACK_DB.RAW.PROCESS_CUSTOMERS_TASK"},
    {"name": "purchases", "stage_path": "@SUBSTRACK_DB.RAW.RAW_STAGE/purchases/", "pipe_name": "SUBSTRACK_DB.RAW.PURCHASES_PIPE", "task_name": "SUBSTRACK_DB.RAW.PROCESS_PURCHASES_TASK"},
    {"name": "subscriptions", "stage_path": "@SUBSTRACK_DB.RAW.RAW_STAGE/subscriptions/", "pipe_name": "SUBSTRACK_DB.RAW.SUBSCRIPTIONS_PIPE", "task_name": "SUBSTRACK_DB.RAW.PROCESS_SUBSCRIPTIONS_TASK"},
    {"name": "billing_invoices", "stage_path": "@SUBSTRACK_DB.RAW.RAW_STAGE/billing_invoices/", "pipe_name": "SUBSTRACK_DB.RAW.BILLING_INVOICES_PIPE", "task_name": "SUBSTRACK_DB.RAW.PROCESS_BILLING_INVOICES_TASK"},
    {"name": "payment_methods", "stage_path": "@SUBSTRACK_DB.RAW.RAW_STAGE/payment_methods/", "pipe_name": "SUBSTRACK_DB.RAW.PAYMENT_METHODS_PIPE", "task_name": "SUBSTRACK_DB.RAW.PROCESS_PAYMENT_METHODS_TASK"},
    {"name": "usage_events", "stage_path": "@SUBSTRACK_DB.RAW.RAW_STAGE/usage_events/", "pipe_name": "SUBSTRACK_DB.RAW.USAGE_EVENTS_PIPE", "task_name": "SUBSTRACK_DB.RAW.PROCESS_USAGE_EVENTS_TASK"},
    {"name": "support_tickets", "stage_path": "@SUBSTRACK_DB.RAW.RAW_STAGE/support_tickets/", "pipe_name": "SUBSTRACK_DB.RAW.SUPPORT_TICKETS_PIPE", "task_name": "SUBSTRACK_DB.RAW.PROCESS_SUPPORT_TICKETS_TASK"},
]

def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )

def upload_file_to_stage(local_file_path, stage_path):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    abs_path = os.path.abspath(local_file_path)
    cursor.execute(f"PUT file://{abs_path} {stage_path} AUTO_COMPRESS = TRUE OVERWRITE = FALSE")
    result = cursor.fetchall()
    print(f"    Upload result: {result}")
    cursor.close()
    conn.close()

def trigger_snowpipe(pipe_name):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute(f"ALTER PIPE {pipe_name} REFRESH")
    cursor.close()
    conn.close()
    print(f"    Snowpipe {pipe_name} triggered")

def execute_task(task_name):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute(f"EXECUTE TASK {task_name}")
    cursor.close()
    conn.close()
    print(f"    Task {task_name} executed")

def run_pipeline(output_files):
    tables_with_data = []

    for t in TABLE_CONFIGS:
        fname = output_files.get(t["name"])
        if fname:
            tables_with_data.append(t)
            print(f"\n[{t['name']}]")
            upload_file_to_stage(fname, t["stage_path"])
            trigger_snowpipe(t["pipe_name"])

    if tables_with_data:
        print(f"\nWaiting 5 seconds for Snowpipe to load data into RAW tables...")
        time.sleep(5)

        for t in tables_with_data:
            print(f"\n[{t['name']}] executing task...")
            execute_task(t["task_name"])

    print("\n=== Pipeline complete ===")

if __name__ == "__main__":
    from cdc_extract import run_extraction
    output_files = run_extraction()
    run_pipeline(output_files)
