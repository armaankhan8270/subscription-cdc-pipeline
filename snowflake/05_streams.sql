-- ============================================================================
-- 05_streams.sql — Streams on RAW tables (capture new records for MERGE)
-- All streams are APPEND_ONLY = TRUE (only INSERTs detected)
-- ============================================================================

CREATE STREAM IF NOT EXISTS SUBSTRACK_DB.RAW.CUSTOMERS_STREAM
  ON TABLE SUBSTRACK_DB.RAW.CUSTOMERS
  APPEND_ONLY = TRUE
  COMMENT = 'Captures new customer records landed by Snowpipe';

CREATE STREAM IF NOT EXISTS SUBSTRACK_DB.RAW.PURCHASES_STREAM
  ON TABLE SUBSTRACK_DB.RAW.PURCHASES
  APPEND_ONLY = TRUE
  COMMENT = 'Captures new purchase records landed by Snowpipe';

CREATE STREAM IF NOT EXISTS SUBSTRACK_DB.RAW.SUBSCRIPTIONS_STREAM
  ON TABLE SUBSTRACK_DB.RAW.SUBSCRIPTIONS
  APPEND_ONLY = TRUE
  COMMENT = 'Captures new subscription records landed by Snowpipe';

CREATE STREAM IF NOT EXISTS SUBSTRACK_DB.RAW.BILLING_INVOICES_STREAM
  ON TABLE SUBSTRACK_DB.RAW.BILLING_INVOICES
  APPEND_ONLY = TRUE
  COMMENT = 'Captures new billing invoice records landed by Snowpipe';

CREATE STREAM IF NOT EXISTS SUBSTRACK_DB.RAW.PAYMENT_METHODS_STREAM
  ON TABLE SUBSTRACK_DB.RAW.PAYMENT_METHODS
  APPEND_ONLY = TRUE
  COMMENT = 'Captures new payment method records landed by Snowpipe';

CREATE STREAM IF NOT EXISTS SUBSTRACK_DB.RAW.USAGE_EVENTS_STREAM
  ON TABLE SUBSTRACK_DB.RAW.USAGE_EVENTS
  APPEND_ONLY = TRUE
  COMMENT = 'Captures new usage event records landed by Snowpipe';

CREATE STREAM IF NOT EXISTS SUBSTRACK_DB.RAW.SUPPORT_TICKETS_STREAM
  ON TABLE SUBSTRACK_DB.RAW.SUPPORT_TICKETS
  APPEND_ONLY = TRUE
  COMMENT = 'Captures new support ticket records landed by Snowpipe';
