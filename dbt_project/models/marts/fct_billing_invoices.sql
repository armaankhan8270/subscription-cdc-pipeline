WITH invoices AS (
    SELECT * FROM {{ ref('stg_billing_invoices') }}
),

customers AS (
    SELECT * FROM {{ ref('dim_customer') }}
),

joined AS (
    SELECT
        i.invoice_id,
        i.customer_id,
        c.full_name AS customer_name,
        i.subscription_id,
        i.amount,
        i.currency,
        i.status AS payment_status,
        i.due_date,
        i.paid_at,
        i.created_at,
        i.updated_at,
        i.is_paid,
        i.days_to_pay,
        CASE
            WHEN i.status = 'paid' AND c.plan = 'free' THEN 0
            WHEN i.status = 'paid' THEN i.amount
            ELSE 0
        END AS collected_revenue,
        CASE WHEN i.status IN ('pending', 'overdue') THEN i.amount ELSE 0 END AS outstanding_revenue
    FROM invoices i
    LEFT JOIN customers c
        ON i.customer_id = c.customer_id
        AND i.due_date >= c.dbt_valid_from::DATE
        AND i.due_date < COALESCE(c.dbt_valid_to::DATE, '9999-12-31')
        AND c.is_current = TRUE
)

SELECT * FROM joined
