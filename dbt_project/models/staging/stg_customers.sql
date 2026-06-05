WITH source AS (
    SELECT * FROM {{ source('staging', 'customers') }}
),

cleaned AS (
    SELECT
        customer_id,
        LOWER(TRIM(email)) AS email,
        TRIM(full_name) AS full_name,
        LOWER(TRIM(plan)) AS plan,
        plan_price::NUMBER(10,2) AS plan_price,
        LOWER(TRIM(status)) AS status,
        signup_date::DATE AS signup_date,
        updated_at::TIMESTAMP_NTZ AS updated_at,
        _is_deleted AS is_deleted,
        CASE plan
            WHEN 'free' THEN 0
            WHEN 'basic' THEN 1
            WHEN 'premium' THEN 2
            WHEN 'enterprise' THEN 3
            ELSE -1
        END AS plan_rank,
        DATEDIFF('day', signup_date::DATE, CURRENT_DATE()) AS days_since_signup
    FROM source
    WHERE _is_deleted = FALSE
)

SELECT * FROM cleaned
