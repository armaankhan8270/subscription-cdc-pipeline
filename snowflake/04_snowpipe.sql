CREATE PIPE IF NOT EXISTS SUBSTRACK_DB.RAW.CUSTOMERS_PIPE
  AUTO_INGEST = FALSE
  COMMENT = 'Loads customer CSV files from stage to raw table'
AS
COPY INTO SUBSTRACK_DB.RAW.CUSTOMERS (
    customer_id, email, full_name, plan, plan_price,
    status, signup_date, updated_at, _change_type
)
FROM @SUBSTRACK_DB.RAW.RAW_STAGE/customers/
FILE_FORMAT = (FORMAT_NAME = 'SUBSTRACK_DB.RAW.CSV_FORMAT')
ON_ERROR = CONTINUE;

CREATE PIPE IF NOT EXISTS SUBSTRACK_DB.RAW.PURCHASES_PIPE
  AUTO_INGEST = FALSE
  COMMENT = 'Loads purchase CSV files from stage to raw table'
AS
COPY INTO SUBSTRACK_DB.RAW.PURCHASES (
    purchase_id, customer_id, product_name,
    amount, purchase_date, created_at, _change_type
)
FROM @SUBSTRACK_DB.RAW.RAW_STAGE/purchases/
FILE_FORMAT = (FORMAT_NAME = 'SUBSTRACK_DB.RAW.CSV_FORMAT')
ON_ERROR = CONTINUE;
