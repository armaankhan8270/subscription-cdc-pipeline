-- ============================================================================
-- 02_raw_tables.sql — RAW Layer (append-only, data as-is from CSV)
-- ============================================================================

-- CUSTOMERS
CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.RAW.CUSTOMERS (
    customer_id VARCHAR(50),
    email VARCHAR(255),
    full_name VARCHAR(255),
    plan VARCHAR(50),
    plan_price NUMBER(10,2),
    status VARCHAR(50),
    signup_date VARCHAR(50),
    updated_at VARCHAR(50),
    _change_type VARCHAR(20),
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- PURCHASES
CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.RAW.PURCHASES (
    purchase_id VARCHAR(50),
    customer_id VARCHAR(50),
    product_name VARCHAR(255),
    amount NUMBER(10,2),
    purchase_date VARCHAR(50),
    created_at VARCHAR(50),
    _change_type VARCHAR(20),
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- SUBSCRIPTIONS
CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.RAW.SUBSCRIPTIONS (
    subscription_id VARCHAR(50),
    customer_id VARCHAR(50),
    plan_type VARCHAR(50),
    plan_price NUMBER(10,2),
    status VARCHAR(50),
    start_date VARCHAR(50),
    end_date VARCHAR(50),
    created_at VARCHAR(50),
    updated_at VARCHAR(50),
    _change_type VARCHAR(20),
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- BILLING INVOICES
CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.RAW.BILLING_INVOICES (
    invoice_id VARCHAR(50),
    customer_id VARCHAR(50),
    subscription_id VARCHAR(50),
    amount NUMBER(10,2),
    currency VARCHAR(10),
    status VARCHAR(50),
    due_date VARCHAR(50),
    paid_at VARCHAR(50),
    created_at VARCHAR(50),
    updated_at VARCHAR(50),
    _change_type VARCHAR(20),
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- PAYMENT METHODS
CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.RAW.PAYMENT_METHODS (
    payment_method_id VARCHAR(50),
    customer_id VARCHAR(50),
    type VARCHAR(50),
    provider VARCHAR(50),
    last_four VARCHAR(10),
    exp_month INTEGER,
    exp_year INTEGER,
    is_default INTEGER,
    created_at VARCHAR(50),
    updated_at VARCHAR(50),
    _change_type VARCHAR(20),
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- USAGE EVENTS
CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.RAW.USAGE_EVENTS (
    event_id VARCHAR(50),
    customer_id VARCHAR(50),
    event_type VARCHAR(50),
    quantity NUMBER(12,2),
    recorded_at VARCHAR(50),
    created_at VARCHAR(50),
    _change_type VARCHAR(20),
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- SUPPORT TICKETS
CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.RAW.SUPPORT_TICKETS (
    ticket_id VARCHAR(50),
    customer_id VARCHAR(50),
    subject VARCHAR(500),
    description VARCHAR(5000),
    priority VARCHAR(50),
    status VARCHAR(50),
    created_at VARCHAR(50),
    updated_at VARCHAR(50),
    _change_type VARCHAR(20),
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
