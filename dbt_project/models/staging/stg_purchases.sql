WITH source AS (
    SELECT * FROM {{ source('staging', 'purchases') }}
),

cleaned AS (
    SELECT
        purchase_id,
        customer_id,
        TRIM(product_name) AS product_name,
        amount::NUMBER(10,2) AS amount,
        purchase_date::DATE AS purchase_date,
        created_at::TIMESTAMP_NTZ AS created_at,
        DATE_TRUNC('month', purchase_date::DATE) AS purchase_month,
        EXTRACT('year', purchase_date::DATE) AS purchase_year
    FROM source
)

SELECT * FROM cleaned
