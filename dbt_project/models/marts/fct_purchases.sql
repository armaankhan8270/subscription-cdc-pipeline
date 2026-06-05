WITH purchases AS (
    SELECT * FROM {{ ref('stg_purchases') }}
),

customers AS (
    SELECT * FROM {{ ref('dim_customer') }}
),

joined AS (
    SELECT
        p.purchase_id,
        p.customer_id,
        c.full_name AS customer_name,
        p.product_name,
        p.amount,
        p.purchase_date,
        p.created_at,
        p.purchase_month,
        p.purchase_year,
        c.plan AS plan_at_purchase,
        c.plan_tier AS plan_tier_at_purchase,
        c.days_on_plan AS customer_days_on_plan_at_purchase,
        CASE WHEN c.plan = 'free' THEN 0 ELSE p.amount END AS effective_revenue
    FROM purchases p
    LEFT JOIN customers c
        ON p.customer_id = c.customer_id
        AND p.purchase_date >= c.dbt_valid_from::DATE
        AND p.purchase_date < COALESCE(c.dbt_valid_to::DATE, '9999-12-31')
)

SELECT * FROM joined
