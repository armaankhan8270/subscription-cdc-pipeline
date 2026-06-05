-- ============================================================================
-- 03_staging_tables.sql — STAGING Layer (current state, type-cast)
-- ============================================================================

CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.STAGING.CUSTOMERS (
    customer_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255),
    full_name VARCHAR(255),
    plan VARCHAR(50),
    plan_price NUMBER(10,2),
    status VARCHAR(50),
    signup_date DATE,
    updated_at TIMESTAMP_NTZ,
    _is_deleted BOOLEAN DEFAULT FALSE,
    _deleted_at TIMESTAMP_NTZ,
    _dw_updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.STAGING.PURCHASES (
    purchase_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    product_name VARCHAR(255),
    amount NUMBER(10,2),
    purchase_date DATE,
    created_at TIMESTAMP_NTZ,
    _dw_updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.STAGING.SUBSCRIPTIONS (
    subscription_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    plan_type VARCHAR(50),
    plan_price NUMBER(10,2),
    status VARCHAR(50),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP_NTZ,
    updated_at TIMESTAMP_NTZ,
    _is_deleted BOOLEAN DEFAULT FALSE,
    _dw_updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.STAGING.BILLING_INVOICES (
    invoice_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    amount NUMBER(10,2),
    currency VARCHAR(10),
    status VARCHAR(50),
    due_date DATE,
    paid_at TIMESTAMP_NTZ,
    created_at TIMESTAMP_NTZ,
    updated_at TIMESTAMP_NTZ,
    _dw_updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.STAGING.PAYMENT_METHODS (
    payment_method_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    type VARCHAR(50),
    provider VARCHAR(50),
    last_four VARCHAR(10),
    exp_month INTEGER,
    exp_year INTEGER,
    is_default BOOLEAN,
    created_at TIMESTAMP_NTZ,
    updated_at TIMESTAMP_NTZ,
    _dw_updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.STAGING.USAGE_EVENTS (
    event_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    event_type VARCHAR(50),
    quantity NUMBER(12,2),
    recorded_at TIMESTAMP_NTZ,
    created_at TIMESTAMP_NTZ,
    _dw_updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS SUBSTRACK_DB.STAGING.SUPPORT_TICKETS (
    ticket_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    subject VARCHAR(500),
    description VARCHAR(5000),
    priority VARCHAR(50),
    status VARCHAR(50),
    created_at TIMESTAMP_NTZ,
    updated_at TIMESTAMP_NTZ,
    _dw_updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
