WITH purchases AS (
    SELECT * FROM {{ ref('stg_purchases') }}
),

purchase_with_customer_sk AS (
    SELECT
        p.purchase_id,
        p.customer_id,
        p.product_name,
        p.amount,
        p.purchase_date,
        p.purchase_month,
        p.purchase_year,
        p.created_at,
        c.customer_sk,
        c.plan AS plan_at_purchase,
        c.plan_price AS plan_price_at_purchase,
        c.plan_tier AS plan_tier_at_purchase,
        c.full_name AS customer_name
    FROM purchases p
    LEFT JOIN {{ ref('dim_customer') }} c
        ON p.customer_id = c.customer_id
        AND p.purchase_date >= c.valid_from::DATE
        AND p.purchase_date < COALESCE(c.valid_to::DATE, '9999-12-31'::DATE)
)

SELECT * FROM purchase_with_customer_sk
