import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )

def upload_file_to_stage(local_file_path, stage_path):
    if local_file_path is None:
        return

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    abs_path = os.path.abspath(local_file_path)
    put_command = f"""
        PUT file://{abs_path}
        {stage_path}
        AUTO_COMPRESS = TRUE
        OVERWRITE = FALSE
    """
    cursor.execute(put_command)
    result = cursor.fetchall()
    print(f"Upload result: {result}")

    cursor.close()
    conn.close()

def trigger_snowpipe(pipe_name):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute(f"ALTER PIPE {pipe_name} REFRESH")
    print(f"Snowpipe {pipe_name} triggered")
    cursor.close()
    conn.close()

def run_pipeline(customers_file, purchases_file):
    if customers_file:
        upload_file_to_stage(
            customers_file,
            "@SUBSTRACK_DB.RAW.RAW_STAGE/customers/"
        )
        trigger_snowpipe("SUBSTRACK_DB.RAW.CUSTOMERS_PIPE")

    if purchases_file:
        upload_file_to_stage(
            purchases_file,
            "@SUBSTRACK_DB.RAW.RAW_STAGE/purchases/"
        )
        trigger_snowpipe("SUBSTRACK_DB.RAW.PURCHASES_PIPE")

if __name__ == "__main__":
    from cdc_extract import run_extraction
    customers_file, purchases_file = run_extraction()
    run_pipeline(customers_file, purchases_file)
