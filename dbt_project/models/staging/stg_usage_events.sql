WITH source AS (
    SELECT * FROM {{ source('staging', 'usage_events') }}
),

cleaned AS (
    SELECT
        event_id,
        customer_id,
        LOWER(TRIM(event_type)) AS event_type,
        quantity,
        recorded_at,
        created_at,
        DATE_TRUNC('day', recorded_at) AS event_date,
        DATE_TRUNC('month', recorded_at) AS event_month,
        CASE
            WHEN LOWER(TRIM(event_type)) = 'api_call' THEN 'count'
            WHEN LOWER(TRIM(event_type)) = 'storage_gb' THEN 'storage'
            WHEN LOWER(TRIM(event_type)) = 'bandwidth_gb' THEN 'bandwidth'
            WHEN LOWER(TRIM(event_type)) = 'users_count' THEN 'users'
            ELSE 'other'
        END AS event_category
    FROM source
)

SELECT * FROM cleaned
