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
