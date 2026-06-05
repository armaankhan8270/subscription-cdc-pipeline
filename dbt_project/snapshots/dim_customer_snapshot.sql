{% snapshot dim_customer_snapshot %}

{{
    config(
        target_schema='SNAPSHOTS',
        target_database='SUBSTRACK_DB',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at',
        invalidate_hard_deletes=True
    )
}}

SELECT
    customer_id,
    email,
    full_name,
    plan,
    plan_price,
    status,
    signup_date,
    updated_at
FROM {{ source('staging', 'customers') }}

{% endsnapshot %}
