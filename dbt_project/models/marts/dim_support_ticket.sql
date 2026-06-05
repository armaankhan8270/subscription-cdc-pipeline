WITH tickets AS (
    SELECT * FROM {{ ref('dim_support_ticket_snapshot') }}
),

customers AS (
    SELECT customer_id, full_name, plan, is_current
    FROM {{ ref('dim_customer') }}
    WHERE is_current = TRUE
),

enriched AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['t.ticket_id', 't.dbt_valid_from']) }} AS ticket_sk,
        t.ticket_id,
        t.customer_id,
        c.full_name AS customer_name,
        c.plan AS customer_plan,
        t.subject,
        t.description,
        t.priority,
        t.status,
        t.created_at,
        t.updated_at,
        t.dbt_valid_from,
        t.dbt_valid_to,
        CASE WHEN t.dbt_valid_to IS NULL THEN TRUE ELSE FALSE END AS is_current_status,
        t.priority_rank,
        t.ticket_age_days,
        t.is_resolved
    FROM tickets t
    LEFT JOIN customers c
        ON t.customer_id = c.customer_id
)

SELECT * FROM enriched
