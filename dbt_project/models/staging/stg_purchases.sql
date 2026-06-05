WITH source AS (
    SELECT * FROM {{ source('staging', 'purchases') }}
),

cleaned AS (
    SELECT
        purchase_id,
        customer_id,
        TRIM(product_name) AS product_name,
        amount,
        purchase_date,
        created_at,
        DATE_TRUNC('month', purchase_date) AS purchase_month,
        YEAR(purchase_date) AS purchase_year
    FROM source
)

SELECT * FROM cleaned
