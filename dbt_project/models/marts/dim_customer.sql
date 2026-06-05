WITH snapshot AS (
    SELECT * FROM {{ ref('dim_customer_snapshot') }}
),

enriched AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['customer_id', 'dbt_valid_from']) }} AS customer_sk,
        customer_id,
        email,
        full_name,
        plan,
        plan_price,
        status,
        signup_date,
        dbt_valid_from,
        dbt_valid_to,
        CASE WHEN dbt_valid_to IS NULL THEN TRUE ELSE FALSE END AS is_current,
        plan_rank,
        DATEDIFF('day', dbt_valid_from, COALESCE(dbt_valid_to, CURRENT_DATE)) AS days_on_plan,
        days_on_plan * plan_price AS estimated_revenue_this_period,
        CASE
            WHEN plan = 'free' THEN 'Starter'
            WHEN plan = 'basic' THEN 'Growth'
            WHEN plan = 'premium' THEN 'Growth'
            WHEN plan = 'enterprise' THEN 'Enterprise'
            ELSE 'Unknown'
        END AS plan_tier
    FROM snapshot
)

SELECT * FROM enriched
