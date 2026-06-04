CREATE TASK IF NOT EXISTS SUBSTRACK_DB.RAW.PROCESS_CUSTOMERS_TASK
  WAREHOUSE = SUBSTRACK_WH
  SCHEDULE = '5 MINUTE'
  COMMENT = 'Merges customer CDC changes into staging table'
  WHEN SYSTEM$STREAM_HAS_DATA('SUBSTRACK_DB.RAW.CUSTOMERS_STREAM')
AS
MERGE INTO SUBSTRACK_DB.STAGING.CUSTOMERS AS target
USING (
    SELECT *
    FROM (
        SELECT
            customer_id,
            email,
            full_name,
            plan,
            plan_price,
            status,
            TRY_TO_DATE(signup_date) AS signup_date,
            TRY_TO_TIMESTAMP(updated_at) AS updated_at,
            _change_type,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY updated_at DESC
            ) AS rn
        FROM SUBSTRACK_DB.RAW.CUSTOMERS_STREAM
    )
    WHERE rn = 1
) AS source
ON target.customer_id = source.customer_id
WHEN NOT MATCHED THEN INSERT (
    customer_id, email, full_name, plan, plan_price,
    status, signup_date, updated_at, _dw_updated_at
)
VALUES (
    source.customer_id, source.email, source.full_name,
    source.plan, source.plan_price, source.status,
    source.signup_date, source.updated_at, CURRENT_TIMESTAMP()
)
WHEN MATCHED AND source._change_type = 'UPSERT' THEN UPDATE SET
    target.email = source.email,
    target.full_name = source.full_name,
    target.plan = source.plan,
    target.plan_price = source.plan_price,
    target.status = source.status,
    target.updated_at = source.updated_at,
    target._dw_updated_at = CURRENT_TIMESTAMP();

CREATE TASK IF NOT EXISTS SUBSTRACK_DB.RAW.PROCESS_PURCHASES_TASK
  WAREHOUSE = SUBSTRACK_WH
  SCHEDULE = '5 MINUTE'
  WHEN SYSTEM$STREAM_HAS_DATA('SUBSTRACK_DB.RAW.PURCHASES_STREAM')
AS
MERGE INTO SUBSTRACK_DB.STAGING.PURCHASES AS target
USING (
    SELECT
        purchase_id,
        customer_id,
        product_name,
        amount,
        TRY_TO_DATE(purchase_date) AS purchase_date,
        TRY_TO_TIMESTAMP(created_at) AS created_at
    FROM SUBSTRACK_DB.RAW.PURCHASES_STREAM
) AS source
ON target.purchase_id = source.purchase_id
WHEN NOT MATCHED THEN INSERT (
    purchase_id, customer_id, product_name,
    amount, purchase_date, created_at, _dw_updated_at
)
VALUES (
    source.purchase_id, source.customer_id, source.product_name,
    source.amount, source.purchase_date, source.created_at,
    CURRENT_TIMESTAMP()
);

ALTER TASK SUBSTRACK_DB.RAW.PROCESS_CUSTOMERS_TASK RESUME;
ALTER TASK SUBSTRACK_DB.RAW.PROCESS_PURCHASES_TASK RESUME;
