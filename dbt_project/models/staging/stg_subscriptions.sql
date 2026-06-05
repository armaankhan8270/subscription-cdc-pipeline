WITH source AS (
    SELECT * FROM {{ source('staging', 'subscriptions') }}
),

cleaned AS (
    SELECT
        subscription_id,
        customer_id,
        LOWER(TRIM(plan_type)) AS plan_type,
        plan_price,
        LOWER(TRIM(status)) AS status,
        start_date,
        end_date,
        created_at,
        updated_at,
        CASE
            WHEN LOWER(TRIM(plan_type)) = 'free' THEN 0
            WHEN LOWER(TRIM(plan_type)) = 'basic' THEN 1
            WHEN LOWER(TRIM(plan_type)) = 'premium' THEN 2
            WHEN LOWER(TRIM(plan_type)) = 'enterprise' THEN 3
            ELSE -1
        END AS plan_rank,
        CASE WHEN end_date IS NULL THEN TRUE ELSE FALSE END AS is_active
    FROM source
    WHERE _is_deleted = FALSE
)

SELECT * FROM cleaned
