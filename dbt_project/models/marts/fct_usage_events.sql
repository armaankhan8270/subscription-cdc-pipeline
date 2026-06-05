WITH events AS (
    SELECT * FROM {{ ref('stg_usage_events') }}
),

customers AS (
    SELECT customer_id, full_name, plan, is_current
    FROM {{ ref('dim_customer') }}
    WHERE is_current = TRUE
),

aggregated AS (
    SELECT
        e.event_id,
        e.customer_id,
        c.full_name AS customer_name,
        c.plan AS current_plan,
        e.event_type,
        e.event_category,
        e.quantity,
        e.recorded_at,
        e.event_date,
        e.event_month,
        e.created_at
    FROM events e
    LEFT JOIN customers c
        ON e.customer_id = c.customer_id
)

SELECT * FROM aggregated
