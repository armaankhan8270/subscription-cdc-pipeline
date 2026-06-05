WITH source AS (
    SELECT * FROM {{ source('staging', 'support_tickets') }}
),

cleaned AS (
    SELECT
        ticket_id,
        customer_id,
        TRIM(subject) AS subject,
        TRIM(description) AS description,
        LOWER(TRIM(priority)) AS priority,
        LOWER(TRIM(status)) AS status,
        created_at,
        updated_at,
        CASE
            WHEN LOWER(TRIM(priority)) = 'critical' THEN 0
            WHEN LOWER(TRIM(priority)) = 'high' THEN 1
            WHEN LOWER(TRIM(priority)) = 'medium' THEN 2
            WHEN LOWER(TRIM(priority)) = 'low' THEN 3
            ELSE 99
        END AS priority_rank,
        DATEDIFF('day', created_at, CURRENT_DATE) AS ticket_age_days,
        CASE
            WHEN LOWER(TRIM(status)) = 'resolved' OR LOWER(TRIM(status)) = 'closed'
            THEN TRUE ELSE FALSE
        END AS is_resolved
    FROM source
)

SELECT * FROM cleaned
