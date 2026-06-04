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
