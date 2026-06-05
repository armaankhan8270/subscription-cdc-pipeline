-- ============================================================================
-- 04_snowpipe.sql — Snowpipe definitions (serverless COPY INTO RAW)
-- All pipes are AUTO_INGEST = FALSE (manual trigger via ALTER PIPE REFRESH)
-- ============================================================================

-- CUSTOMERS
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

-- PURCHASES
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

-- SUBSCRIPTIONS
CREATE PIPE IF NOT EXISTS SUBSTRACK_DB.RAW.SUBSCRIPTIONS_PIPE
  AUTO_INGEST = FALSE
  COMMENT = 'Loads subscription CSV files from stage to raw table'
AS
COPY INTO SUBSTRACK_DB.RAW.SUBSCRIPTIONS (
    subscription_id, customer_id, plan_type, plan_price,
    status, start_date, end_date, created_at, updated_at, _change_type
)
FROM @SUBSTRACK_DB.RAW.RAW_STAGE/subscriptions/
FILE_FORMAT = (FORMAT_NAME = 'SUBSTRACK_DB.RAW.CSV_FORMAT')
ON_ERROR = CONTINUE;

-- BILLING INVOICES
CREATE PIPE IF NOT EXISTS SUBSTRACK_DB.RAW.BILLING_INVOICES_PIPE
  AUTO_INGEST = FALSE
  COMMENT = 'Loads billing invoice CSV files from stage to raw table'
AS
COPY INTO SUBSTRACK_DB.RAW.BILLING_INVOICES (
    invoice_id, customer_id, subscription_id, amount,
    currency, status, due_date, paid_at, created_at, updated_at, _change_type
)
FROM @SUBSTRACK_DB.RAW.RAW_STAGE/billing_invoices/
FILE_FORMAT = (FORMAT_NAME = 'SUBSTRACK_DB.RAW.CSV_FORMAT')
ON_ERROR = CONTINUE;

-- PAYMENT METHODS
CREATE PIPE IF NOT EXISTS SUBSTRACK_DB.RAW.PAYMENT_METHODS_PIPE
  AUTO_INGEST = FALSE
  COMMENT = 'Loads payment method CSV files from stage to raw table'
AS
COPY INTO SUBSTRACK_DB.RAW.PAYMENT_METHODS (
    payment_method_id, customer_id, type, provider,
    last_four, exp_month, exp_year, is_default, created_at, updated_at, _change_type
)
FROM @SUBSTRACK_DB.RAW.RAW_STAGE/payment_methods/
FILE_FORMAT = (FORMAT_NAME = 'SUBSTRACK_DB.RAW.CSV_FORMAT')
ON_ERROR = CONTINUE;

-- USAGE EVENTS
CREATE PIPE IF NOT EXISTS SUBSTRACK_DB.RAW.USAGE_EVENTS_PIPE
  AUTO_INGEST = FALSE
  COMMENT = 'Loads usage event CSV files from stage to raw table'
AS
COPY INTO SUBSTRACK_DB.RAW.USAGE_EVENTS (
    event_id, customer_id, event_type, quantity, recorded_at, created_at, _change_type
)
FROM @SUBSTRACK_DB.RAW.RAW_STAGE/usage_events/
FILE_FORMAT = (FORMAT_NAME = 'SUBSTRACK_DB.RAW.CSV_FORMAT')
ON_ERROR = CONTINUE;

-- SUPPORT TICKETS
CREATE PIPE IF NOT EXISTS SUBSTRACK_DB.RAW.SUPPORT_TICKETS_PIPE
  AUTO_INGEST = FALSE
  COMMENT = 'Loads support ticket CSV files from stage to raw table'
AS
COPY INTO SUBSTRACK_DB.RAW.SUPPORT_TICKETS (
    ticket_id, customer_id, subject, description,
    priority, status, created_at, updated_at, _change_type
)
FROM @SUBSTRACK_DB.RAW.RAW_STAGE/support_tickets/
FILE_FORMAT = (FORMAT_NAME = 'SUBSTRACK_DB.RAW.CSV_FORMAT')
ON_ERROR = CONTINUE;
