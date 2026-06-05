-- ============================================================================
-- 06_tasks.sql — Tasks that MERGE stream changes into STAGING
-- NO SCHEDULE — all tasks run manually via EXECUTE TASK
-- Each condition checks SYSTEM$STREAM_HAS_DATA before running
-- ============================================================================

-- CUSTOMERS: UPSERT logic (insert new, update existing)
CREATE TASK IF NOT EXISTS SUBSTRACK_DB.RAW.PROCESS_CUSTOMERS_TASK
  WAREHOUSE = SUBSTRACK_WH
  COMMENT = 'Run manually after CDC upload. Merges stream changes into STAGING.CUSTOMERS'
  WHEN SYSTEM$STREAM_HAS_DATA('SUBSTRACK_DB.RAW.CUSTOMERS_STREAM')
AS
MERGE INTO SUBSTRACK_DB.STAGING.CUSTOMERS AS target
USING (
    SELECT * FROM (
        SELECT
            customer_id, email, full_name, plan, plan_price,
            status, TRY_TO_DATE(signup_date) AS signup_date,
            TRY_TO_TIMESTAMP(updated_at) AS updated_at,
            _change_type,
            ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) AS rn
        FROM SUBSTRACK_DB.RAW.CUSTOMERS_STREAM
    ) WHERE rn = 1
) AS source
ON target.customer_id = source.customer_id
WHEN NOT MATCHED THEN INSERT (customer_id, email, full_name, plan, plan_price, status, signup_date, updated_at, _dw_updated_at)
VALUES (source.customer_id, source.email, source.full_name, source.plan, source.plan_price, source.status, source.signup_date, source.updated_at, CURRENT_TIMESTAMP())
WHEN MATCHED AND source._change_type = 'UPSERT' THEN UPDATE SET
    target.email = source.email, target.full_name = source.full_name,
    target.plan = source.plan, target.plan_price = source.plan_price,
    target.status = source.status, target.updated_at = source.updated_at,
    target._dw_updated_at = CURRENT_TIMESTAMP();

-- PURCHASES: INSERT only (append-only)
CREATE TASK IF NOT EXISTS SUBSTRACK_DB.RAW.PROCESS_PURCHASES_TASK
  WAREHOUSE = SUBSTRACK_WH
  COMMENT = 'Run manually after CDC upload. Merges stream changes into STAGING.PURCHASES'
  WHEN SYSTEM$STREAM_HAS_DATA('SUBSTRACK_DB.RAW.PURCHASES_STREAM')
AS
MERGE INTO SUBSTRACK_DB.STAGING.PURCHASES AS target
USING (
    SELECT purchase_id, customer_id, product_name, amount,
           TRY_TO_DATE(purchase_date) AS purchase_date,
           TRY_TO_TIMESTAMP(created_at) AS created_at
    FROM SUBSTRACK_DB.RAW.PURCHASES_STREAM
) AS source
ON target.purchase_id = source.purchase_id
WHEN NOT MATCHED THEN INSERT (purchase_id, customer_id, product_name, amount, purchase_date, created_at, _dw_updated_at)
VALUES (source.purchase_id, source.customer_id, source.product_name, source.amount, source.purchase_date, source.created_at, CURRENT_TIMESTAMP());

-- SUBSCRIPTIONS: UPSERT logic
CREATE TASK IF NOT EXISTS SUBSTRACK_DB.RAW.PROCESS_SUBSCRIPTIONS_TASK
  WAREHOUSE = SUBSTRACK_WH
  COMMENT = 'Run manually after CDC upload. Merges stream changes into STAGING.SUBSCRIPTIONS'
  WHEN SYSTEM$STREAM_HAS_DATA('SUBSTRACK_DB.RAW.SUBSCRIPTIONS_STREAM')
AS
MERGE INTO SUBSTRACK_DB.STAGING.SUBSCRIPTIONS AS target
USING (
    SELECT * FROM (
        SELECT
            subscription_id, customer_id, plan_type, plan_price,
            status, TRY_TO_DATE(start_date) AS start_date,
            TRY_TO_DATE(end_date) AS end_date,
            TRY_TO_TIMESTAMP(created_at) AS created_at,
            TRY_TO_TIMESTAMP(updated_at) AS updated_at,
            _change_type,
            ROW_NUMBER() OVER (PARTITION BY subscription_id ORDER BY updated_at DESC) AS rn
        FROM SUBSTRACK_DB.RAW.SUBSCRIPTIONS_STREAM
    ) WHERE rn = 1
) AS source
ON target.subscription_id = source.subscription_id
WHEN NOT MATCHED THEN INSERT (subscription_id, customer_id, plan_type, plan_price, status, start_date, end_date, created_at, updated_at, _dw_updated_at)
VALUES (source.subscription_id, source.customer_id, source.plan_type, source.plan_price, source.status, source.start_date, source.end_date, source.created_at, source.updated_at, CURRENT_TIMESTAMP())
WHEN MATCHED AND source._change_type = 'UPSERT' THEN UPDATE SET
    target.plan_type = source.plan_type, target.plan_price = source.plan_price,
    target.status = source.status, target.end_date = source.end_date,
    target.updated_at = source.updated_at, target._dw_updated_at = CURRENT_TIMESTAMP();

-- BILLING INVOICES: UPSERT logic
CREATE TASK IF NOT EXISTS SUBSTRACK_DB.RAW.PROCESS_BILLING_INVOICES_TASK
  WAREHOUSE = SUBSTRACK_WH
  COMMENT = 'Run manually after CDC upload. Merges stream changes into STAGING.BILLING_INVOICES'
  WHEN SYSTEM$STREAM_HAS_DATA('SUBSTRACK_DB.RAW.BILLING_INVOICES_STREAM')
AS
MERGE INTO SUBSTRACK_DB.STAGING.BILLING_INVOICES AS target
USING (
    SELECT * FROM (
        SELECT
            invoice_id, customer_id, amount,
            currency, status, TRY_TO_DATE(due_date) AS due_date,
            TRY_TO_TIMESTAMP(paid_at) AS paid_at,
            TRY_TO_TIMESTAMP(created_at) AS created_at,
            TRY_TO_TIMESTAMP(updated_at) AS updated_at,
            _change_type,
            ROW_NUMBER() OVER (PARTITION BY invoice_id ORDER BY updated_at DESC) AS rn
        FROM SUBSTRACK_DB.RAW.BILLING_INVOICES_STREAM
    ) WHERE rn = 1
) AS source
ON target.invoice_id = source.invoice_id
WHEN NOT MATCHED THEN INSERT (invoice_id, customer_id, amount, currency, status, due_date, paid_at, created_at, updated_at, _dw_updated_at)
VALUES (source.invoice_id, source.customer_id, source.amount, source.currency, source.status, source.due_date, source.paid_at, source.created_at, source.updated_at, CURRENT_TIMESTAMP())
WHEN MATCHED AND source._change_type = 'UPSERT' THEN UPDATE SET
    target.status = source.status, target.paid_at = source.paid_at,
    target.amount = source.amount, target.updated_at = source.updated_at,
    target._dw_updated_at = CURRENT_TIMESTAMP();

-- PAYMENT METHODS: UPSERT logic
CREATE TASK IF NOT EXISTS SUBSTRACK_DB.RAW.PROCESS_PAYMENT_METHODS_TASK
  WAREHOUSE = SUBSTRACK_WH
  COMMENT = 'Run manually after CDC upload. Merges stream changes into STAGING.PAYMENT_METHODS'
  WHEN SYSTEM$STREAM_HAS_DATA('SUBSTRACK_DB.RAW.PAYMENT_METHODS_STREAM')
AS
MERGE INTO SUBSTRACK_DB.STAGING.PAYMENT_METHODS AS target
USING (
    SELECT * FROM (
        SELECT
            payment_method_id, customer_id, type, provider, last_four,
            exp_month, exp_year, is_default,
            TRY_TO_TIMESTAMP(created_at) AS created_at,
            TRY_TO_TIMESTAMP(updated_at) AS updated_at,
            _change_type,
            ROW_NUMBER() OVER (PARTITION BY payment_method_id ORDER BY updated_at DESC) AS rn
        FROM SUBSTRACK_DB.RAW.PAYMENT_METHODS_STREAM
    ) WHERE rn = 1
) AS source
ON target.payment_method_id = source.payment_method_id
WHEN NOT MATCHED THEN INSERT (payment_method_id, customer_id, type, provider, last_four, exp_month, exp_year, is_default, created_at, updated_at, _dw_updated_at)
VALUES (source.payment_method_id, source.customer_id, source.type, source.provider, source.last_four, source.exp_month, source.exp_year, source.is_default, source.created_at, source.updated_at, CURRENT_TIMESTAMP())
WHEN MATCHED AND source._change_type = 'UPSERT' THEN UPDATE SET
    target.type = source.type, target.provider = source.provider,
    target.last_four = source.last_four, target.exp_month = source.exp_month,
    target.exp_year = source.exp_year, target.is_default = source.is_default,
    target.updated_at = source.updated_at, target._dw_updated_at = CURRENT_TIMESTAMP();

-- USAGE EVENTS: INSERT only (append-only)
CREATE TASK IF NOT EXISTS SUBSTRACK_DB.RAW.PROCESS_USAGE_EVENTS_TASK
  WAREHOUSE = SUBSTRACK_WH
  COMMENT = 'Run manually after CDC upload. Merges stream changes into STAGING.USAGE_EVENTS'
  WHEN SYSTEM$STREAM_HAS_DATA('SUBSTRACK_DB.RAW.USAGE_EVENTS_STREAM')
AS
MERGE INTO SUBSTRACK_DB.STAGING.USAGE_EVENTS AS target
USING (
    SELECT event_id, customer_id, event_type, quantity,
           TRY_TO_TIMESTAMP(recorded_at) AS recorded_at,
           TRY_TO_TIMESTAMP(created_at) AS created_at
    FROM SUBSTRACK_DB.RAW.USAGE_EVENTS_STREAM
) AS source
ON target.event_id = source.event_id
WHEN NOT MATCHED THEN INSERT (event_id, customer_id, event_type, quantity, recorded_at, created_at, _dw_updated_at)
VALUES (source.event_id, source.customer_id, source.event_type, source.quantity, source.recorded_at, source.created_at, CURRENT_TIMESTAMP());

-- SUPPORT TICKETS: UPSERT logic
CREATE TASK IF NOT EXISTS SUBSTRACK_DB.RAW.PROCESS_SUPPORT_TICKETS_TASK
  WAREHOUSE = SUBSTRACK_WH
  COMMENT = 'Run manually after CDC upload. Merges stream changes into STAGING.SUPPORT_TICKETS'
  WHEN SYSTEM$STREAM_HAS_DATA('SUBSTRACK_DB.RAW.SUPPORT_TICKETS_STREAM')
AS
MERGE INTO SUBSTRACK_DB.STAGING.SUPPORT_TICKETS AS target
USING (
    SELECT * FROM (
        SELECT
            ticket_id, customer_id, subject, description, priority, status,
            TRY_TO_TIMESTAMP(created_at) AS created_at,
            TRY_TO_TIMESTAMP(updated_at) AS updated_at,
            _change_type,
            ROW_NUMBER() OVER (PARTITION BY ticket_id ORDER BY updated_at DESC) AS rn
        FROM SUBSTRACK_DB.RAW.SUPPORT_TICKETS_STREAM
    ) WHERE rn = 1
) AS source
ON target.ticket_id = source.ticket_id
WHEN NOT MATCHED THEN INSERT (ticket_id, customer_id, subject, description, priority, status, created_at, updated_at, _dw_updated_at)
VALUES (source.ticket_id, source.customer_id, source.subject, source.description, source.priority, source.status, source.created_at, source.updated_at, CURRENT_TIMESTAMP())
WHEN MATCHED AND source._change_type = 'UPSERT' THEN UPDATE SET
    target.priority = source.priority, target.status = source.status,
    target.subject = source.subject, target.description = source.description,
    target.updated_at = source.updated_at, target._dw_updated_at = CURRENT_TIMESTAMP();
