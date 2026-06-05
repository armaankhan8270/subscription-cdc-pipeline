WITH source AS (
    SELECT * FROM {{ source('staging', 'customers') }}
),

cleaned AS (
    SELECT
        customer_id,
        LOWER(TRIM(email)) AS email,
        TRIM(full_name) AS full_name,
        LOWER(TRIM(plan)) AS plan,
        plan_price,
        LOWER(TRIM(status)) AS status,
        signup_date,
        updated_at,
        CASE
            WHEN LOWER(TRIM(plan)) = 'free' THEN 0
            WHEN LOWER(TRIM(plan)) = 'basic' THEN 1
            WHEN LOWER(TRIM(plan)) = 'premium' THEN 2
            WHEN LOWER(TRIM(plan)) = 'enterprise' THEN 3
            ELSE -1
        END AS plan_rank,
        DATEDIFF('day', signup_date, CURRENT_DATE) AS days_since_signup
    FROM source
    WHERE _is_deleted = FALSE
)

SELECT * FROM cleaned
