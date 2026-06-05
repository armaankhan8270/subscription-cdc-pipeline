WITH snapshot AS (
    SELECT * FROM {{ ref('dim_subscription_snapshot') }}
),

enriched AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['subscription_id', 'dbt_valid_from']) }} AS subscription_sk,
        subscription_id,
        customer_id,
        plan_type,
        plan_price,
        status,
        start_date,
        end_date,
        dbt_valid_from,
        dbt_valid_to,
        CASE WHEN dbt_valid_to IS NULL THEN TRUE ELSE FALSE END AS is_current,
        plan_rank,
        is_active,
        DATEDIFF('day', dbt_valid_from, COALESCE(dbt_valid_to, CURRENT_DATE)) AS days_in_this_state,
        CASE WHEN end_date IS NULL THEN DATEDIFF('day', start_date, CURRENT_DATE) ELSE DATEDIFF('day', start_date, end_date) END AS total_subscription_days,
        CASE
            WHEN plan_type = 'free' THEN 'Starter'
            WHEN plan_type = 'basic' THEN 'Growth'
            WHEN plan_type = 'premium' THEN 'Growth'
            WHEN plan_type = 'enterprise' THEN 'Enterprise'
            ELSE 'Unknown'
        END AS plan_tier
    FROM snapshot
)

SELECT * FROM enriched
