WITH source AS (
    SELECT * FROM {{ source('staging', 'payment_methods') }}
),

cleaned AS (
    SELECT
        payment_method_id,
        customer_id,
        LOWER(TRIM(type)) AS type,
        LOWER(TRIM(provider)) AS provider,
        last_four,
        exp_month,
        exp_year,
        is_default,
        created_at,
        updated_at,
        CASE WHEN is_default = TRUE THEN TRUE ELSE FALSE END AS is_default_method,
        DATE_FROM_PARTS(exp_year, exp_month, 1) AS expiration_date,
        CASE
            WHEN DATE_FROM_PARTS(exp_year, exp_month, 1) >= CURRENT_DATE THEN TRUE
            ELSE FALSE
        END AS is_valid
    FROM source
)

SELECT * FROM cleaned
