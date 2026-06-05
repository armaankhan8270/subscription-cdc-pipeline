{% snapshot dim_subscription_snapshot %}

{{
    config(
        target_schema='SNAPSHOTS',
        unique_key='subscription_id',
        strategy='timestamp',
        updated_at='updated_at',
        invalidate_hard_deletes=True
    )
}}

SELECT * FROM {{ source('staging', 'subscriptions') }}

{% endsnapshot %}
