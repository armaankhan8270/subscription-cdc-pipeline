WITH snapshot AS (
    SELECT * FROM {{ ref('dim_customer_snapshot') }}
),

enriched AS (
    SELECT
        dbt_scd_id AS customer_sk,
        customer_id,
        email,
        full_name,
        plan,
        plan_price,
        status,
        signup_date,
        dbt_valid_from AS valid_from,
        dbt_valid_to AS valid_to,
        CASE
            WHEN dbt_valid_to IS NULL THEN TRUE
            ELSE FALSE
        END AS is_current,
        CASE plan
            WHEN 'free' THEN 'Starter'
            WHEN 'basic' THEN 'Starter'
            WHEN 'premium' THEN 'Growth'
            WHEN 'enterprise' THEN 'Enterprise'
        END AS plan_tier,
        DATEDIFF('day', dbt_valid_from, COALESCE(dbt_valid_to, CURRENT_TIMESTAMP())) AS days_on_plan,
        plan_price * (DATEDIFF('day', dbt_valid_from, COALESCE(dbt_valid_to, CURRENT_TIMESTAMP())) / 30.0) AS estimated_revenue_this_period
    FROM snapshot
)

SELECT * FROM enriched
