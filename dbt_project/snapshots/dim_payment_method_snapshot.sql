{% snapshot dim_payment_method_snapshot %}

{{
    config(
        target_schema='SNAPSHOTS',
        unique_key='payment_method_id',
        strategy='timestamp',
        updated_at='updated_at',
        invalidate_hard_deletes=True
    )
}}

SELECT * FROM {{ source('staging', 'payment_methods') }}

{% endsnapshot %}
