WITH source AS (
    SELECT * FROM {{ source('staging', 'billing_invoices') }}
),

cleaned AS (
    SELECT
        invoice_id,
        customer_id,
        amount,
        UPPER(TRIM(currency)) AS currency,
        LOWER(TRIM(status)) AS status,
        due_date,
        paid_at,
        created_at,
        updated_at,
        CASE
            WHEN paid_at IS NOT NULL THEN TRUE
            ELSE FALSE
        END AS is_paid,
        CASE
            WHEN paid_at IS NOT NULL THEN DATEDIFF('day', due_date, paid_at)
            ELSE DATEDIFF('day', due_date, CURRENT_DATE)
        END AS days_to_pay
    FROM source
)

SELECT * FROM cleaned
